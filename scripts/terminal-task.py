#!/usr/bin/env python3
"""Keep the result visible in terminals that close after their child exits."""
import subprocess,sys
from pathlib import Path
if __name__=='__main__':
    result=subprocess.run(['python3',str(Path(__file__).with_name('easy.py')),*sys.argv[1:]])
    print('\nEtapa encerrada com código',result.returncode,flush=True)
    if sys.stdin.isatty():
        try:input('Pressione Enter para fechar este terminal…')
        except (EOFError,KeyboardInterrupt):pass
    sys.exit(result.returncode)
