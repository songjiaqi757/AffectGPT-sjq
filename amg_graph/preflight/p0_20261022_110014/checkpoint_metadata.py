"""Static Torch ZIP metadata reader: no pickle loading, imports or callable execution."""
import pickletools
import zipfile

class Opaque:
    def __init__(self, kind, args=None):
        self.kind, self.args, self.state = kind, args, None

def read_checkpoint_metadata(path):
    with zipfile.ZipFile(path) as z:
        entries=[n for n in z.namelist() if n.endswith("/data.pkl")]
        if len(entries)!=1: raise ValueError("Expected one Torch data.pkl")
        info=z.getinfo(entries[0])
        if info.file_size>64*1024*1024: raise ValueError("Oversized pickle metadata")
        raw=z.read(entries[0])
    stack=[];memo={};marker=object()
    def pop_mark():
        pos=len(stack)-1
        while pos>=0 and stack[pos] is not marker: pos-=1
        if pos<0: raise ValueError("Missing MARK")
        items=stack[pos+1:];del stack[pos:]
        return items
    for op,arg,pos in pickletools.genops(raw):
        name=op.name
        if name in ("PROTO","FRAME"): continue
        elif name=="MARK": stack.append(marker)
        elif name=="EMPTY_DICT": stack.append({})
        elif name=="EMPTY_LIST": stack.append([])
        elif name=="EMPTY_TUPLE": stack.append(())
        elif name in ("BINUNICODE","SHORT_BINUNICODE","UNICODE","BINUNICODE8","BININT","BININT1","BININT2","INT","LONG","LONG1","LONG4","BINFLOAT","FLOAT","BINBYTES","SHORT_BINBYTES","BINBYTES8","STRING","BINSTRING","SHORT_BINSTRING"): stack.append(arg)
        elif name=="NONE": stack.append(None)
        elif name=="NEWTRUE": stack.append(True)
        elif name=="NEWFALSE": stack.append(False)
        elif name in ("BINPUT","LONG_BINPUT","PUT"): memo[int(arg)]=stack[-1]
        elif name=="MEMOIZE": memo[len(memo)]=stack[-1]
        elif name in ("BINGET","LONG_BINGET","GET"): stack.append(memo[int(arg)])
        elif name=="GLOBAL": stack.append(Opaque("global",arg))
        elif name=="STACK_GLOBAL":
            sym=stack.pop();module=stack.pop();stack.append(Opaque("global",module+" "+sym))
        elif name=="TUPLE": stack.append(tuple(pop_mark()))
        elif name in ("TUPLE1","TUPLE2","TUPLE3"):
            n=int(name[-1]);items=tuple(stack[-n:]);del stack[-n:];stack.append(items)
        elif name=="LIST": stack.append(pop_mark())
        elif name=="DICT":
            items=pop_mark();stack.append(dict(zip(items[::2],items[1::2])))
        elif name=="SETITEM":
            value=stack.pop();key=stack.pop();stack[-1][key]=value
        elif name=="SETITEMS":
            items=pop_mark();stack[-1].update(zip(items[::2],items[1::2]))
        elif name=="APPEND":
            value=stack.pop();stack[-1].append(value)
        elif name=="APPENDS":
            items=pop_mark();stack[-1].extend(items)
        elif name=="BINPERSID": stack.append(Opaque("persistent_storage",stack.pop()))
        elif name=="REDUCE":
            args=stack.pop();ref=stack.pop()
            if not isinstance(ref,Opaque) or ref.kind!="global": raise ValueError("Unexpected reducer")
            if ref.args=="collections OrderedDict" and args==(): stack.append({})
            else: stack.append(Opaque(ref.args,args))
        elif name=="BUILD":
            state=stack.pop()
            if not isinstance(stack[-1],Opaque): raise ValueError("Unexpected BUILD")
            stack[-1].state=state
        elif name=="POP": stack.pop()
        elif name=="DUP": stack.append(stack[-1])
        elif name=="STOP":
            if len(stack)!=1 or not isinstance(stack[0],dict): raise ValueError("Malformed root")
            return stack[0]
        else: raise ValueError("Unsupported static opcode: "+name)
    raise ValueError("Missing STOP")

def tensor_shape(value):
    if not isinstance(value,Opaque) or value.kind!="torch._utils _rebuild_tensor_v2":
        raise ValueError("Unsupported tensor metadata")
    return list(value.args[2])
