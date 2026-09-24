"""Invoke with offline_run.py; child inherits kernel network denial."""
import subprocess,sys
subprocess.run(['node','--no-js-float16array','research/validate_runtime.mjs',sys.argv[1]],check=True)
