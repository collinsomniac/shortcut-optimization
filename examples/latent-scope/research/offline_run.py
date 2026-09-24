"""Linux local-only validation: deny network sockets before importing any runtime.
All weights and tokenizers must already be downloaded. The seccomp filter can
only remove this process's permissions and is inherited by child threads.
Usage: python research/offline_run.py research/build_atlas.py --source ... --out ...
"""
import ctypes, ctypes.util, errno, runpy, sys
lib = ctypes.CDLL(ctypes.util.find_library('seccomp'), use_errno=True)
lib.seccomp_init.argtypes=[ctypes.c_uint32];lib.seccomp_init.restype=ctypes.c_void_p
lib.seccomp_rule_add.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_int,ctypes.c_uint]
lib.seccomp_syscall_resolve_name.argtypes=[ctypes.c_char_p]
lib.seccomp_load.argtypes=[ctypes.c_void_p];lib.seccomp_release.argtypes=[ctypes.c_void_p]
ctx=lib.seccomp_init(0x7fff0000)
if not ctx:raise RuntimeError('Network-denial initialization failed')
try:
 for name in ['socket','socketpair','connect','sendto','sendmsg','sendmmsg']:
  n=lib.seccomp_syscall_resolve_name(name.encode())
  if n<0 or lib.seccomp_rule_add(ctx,0x00050000|errno.EPERM,n,0)!=0:raise RuntimeError('Cannot deny '+name)
 if lib.seccomp_load(ctx)!=0:raise RuntimeError('Cannot enforce network denial')
finally:lib.seccomp_release(ctx)
import socket
try:socket.socket(socket.AF_INET,socket.SOCK_STREAM)
except PermissionError:print('Verified: all network sockets denied by kernel.',flush=True)
else:raise RuntimeError('Network-denial self-test failed')
script=sys.argv[1];sys.argv=sys.argv[1:];runpy.run_path(script,run_name='__main__')
