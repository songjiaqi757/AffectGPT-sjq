import argparse,traceback
from .common import *
from .prepare import main
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--run",required=True);run=Path(a.parse_args().run)
 try:main(run)
 except BaseException as exc:
  status(run,"preparation_failed",state="failed",error=repr(exc),traceback=traceback.format_exc());raise
