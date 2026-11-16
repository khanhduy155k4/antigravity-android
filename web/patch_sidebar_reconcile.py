#!/usr/bin/env python3
"""Connect existing native confirmed-idle proof to actual upstream v2.4 React sidebar."""
from pathlib import Path
import sys

MARKER="/*AGY_SIDEBAR_RECONCILE_V24*/"
SECONDARY_MARKER="/*AGY_SIDEBAR_RUNNING_RECONCILE_V24*/"
PRIMARY='function otc(a){var b=Ak(h=>Tn(h)===a),c=!nkb(b?void 0:a),d=IC(b?a:void 0,{selector:ltc}),f=pI(b?a:void 0),g=WX(a);return(b?d||f:c)||g}'
REPLACEMENT=('function otc(a){var b=Ak(h=>Tn(h)===a),c=!nkb(b?void 0:a),'
    'd=IC(b?a:void 0,{selector:ltc}),f=pI(b?a:void 0),g=WX(a),'
    'verifiedIdle=B.useSyncExternalStore('
    'window.__AGY_VERIFIED_AGENT_SUBSCRIBE__||(()=>()=>{}),'
    '()=>window.__AGY_VERIFIED_AGENT_GET__?.(a)===true,()=>false);'
    +MARKER+'return((b?d||f:c)&&!verifiedIdle)||g}')
SECONDARY='n=k||u==="running";'
SECONDARY_REPLACEMENT=('n=k||(u==="running"&&!window.__AGY_VERIFIED_AGENT_GET__?.(a));'
    +SECONDARY_MARKER)

def patch(s):
    if MARKER in s or SECONDARY_MARKER in s:
        if s.count(MARKER)==s.count(SECONDARY_MARKER)==s.count(REPLACEMENT)==s.count(SECONDARY_REPLACEMENT)==1:
            return s
        raise ValueError("partial/inconsistent v2.4 React sidebar patch")
    if s.count(PRIMARY)!=1 or s.count(SECONDARY)!=1:
        raise ValueError(f"v2.4 React anchors changed: primary={s.count(PRIMARY)} secondary={s.count(SECONDARY)}")
    return s.replace(PRIMARY,REPLACEMENT,1).replace(SECONDARY,SECONDARY_REPLACEMENT,1)

if __name__=="__main__":
    if len(sys.argv)!=3:raise SystemExit("usage: patch_sidebar_reconcile.py INPUT OUTPUT")
    src,dst=map(Path,sys.argv[1:])
    try:out=patch(src.read_text(encoding="utf8"))
    except ValueError as err:raise SystemExit("v2.4 sidebar patch incompatible: "+str(err))
    dst.write_text(out,encoding="utf8")
    print("React VAb/z_ now use existing native confirmed-idle proof (v2.4)")
