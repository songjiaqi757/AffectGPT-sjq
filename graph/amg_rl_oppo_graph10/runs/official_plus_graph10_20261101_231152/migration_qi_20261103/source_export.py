import os,sys,json
from pathlib import Path
CONTROL=Path(__file__).resolve().parent
command=os.environ.get('SSH_ORIGINAL_COMMAND','')
if command=='affectgpt-manifest-v1':
 sys.stdout.buffer.write((CONTROL/'manifest.json').read_bytes())
elif command=='affectgpt-stream-v1':
 os.execv('/bin/tar',['tar','--dereference','--no-recursion','--blocking-factor=128','-C','/ai/sjq','-cf','-','--null','--verbatim-files-from','-T',str(CONTROL/'files0')])
else:
 sys.stderr.write('This temporary key only permits the fixed AffectGPT inference export.\n');sys.exit(126)
