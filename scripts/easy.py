#!/usr/bin/env python3
"""Small, inspectable entry point; delegates builds to upstream wrappers."""
import argparse
import os
import platform
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import dependencies
REGIONS = ('br','euw','eune','na','kr','jp','la1','la2','oc1','ru','tr')
LOCALES = {'br':'pt_BR','na':'en_US','kr':'ko_KR','jp':'ja_JP','euw':'en_GB','eune':'en_GB','la1':'es_MX','la2':'es_AR','oc1':'en_AU','ru':'ru_RU','tr':'tr_TR'}

def distro():
    try:
        values = {}
        for line in Path('/etc/os-release').read_text().splitlines():
            if '=' in line:
                key,value=line.split('=',1);values[key]=value.strip('"')
        return values.get('PRETTY_NAME',values.get('ID','Linux'))
    except OSError:
        return 'Linux'

def choose_backend(requested,action):
    if requested!='auto':return requested
    if action in ('run','doctor') and shutil.which('darling'):return 'native'
    if shutil.which('nix'):return 'nix'
    return 'native' if dependencies.family() else 'nix'

def plan(action,backend,region):
    nix = ['nix','--extra-experimental-features','nix-command flakes','run']
    if backend == 'nix':
        return {'install':[nix+['.#installer']], 'run':[nix+['.#default']],
                'doctor':[nix+['.#default','--','--doctor']]}[action]
    return {'install':[
        ['python3','-m','venv','build/venv'],
        ['build/venv/bin/python','-m','pip','install','-r','requirements.txt'],
        ['python3','scripts/configure.py','--guest-user',Path.home().name],
        ['sh','scripts/build.sh'],
        ['sudo','cmake','--install','build/darling-src/build'],
        ['sh','scripts/install-runtime.sh'],
        ['sh','scripts/installer.sh',region]],
        'run':[['sh','scripts/run.sh']],
        'doctor':[['python3','scripts/preflight.py']]}[action]

def main(argv=None):
    p=argparse.ArgumentParser(description='Instalação guiada do darling-lol (experimental).')
    p.add_argument('action',choices=('install','run','doctor'))
    p.add_argument('--backend',choices=('auto','nix','native'),default='auto')
    p.add_argument('--region',choices=REGIONS,default='br')
    p.add_argument('--locale')
    p.add_argument('--jobs',type=int,default=2)
    p.add_argument('--skip-deps',action='store_true',help='não prepara dependências nativas')
    p.add_argument('--dry-run',action='store_true',help='mostra os comandos sem executá-los')
    a=p.parse_args(argv)
    if a.jobs<1:p.error('--jobs deve ser pelo menos 1')
    if platform.system()!='Linux' or platform.machine()!='x86_64':
        p.error('Este runtime exige Linux x86_64.')
    a.backend=choose_backend(a.backend,a.action)
    commands=plan(a.action,a.backend,a.region)
    if a.action=='install' and a.backend=='native' and not a.skip_deps:
        dep_plan=dependencies.commands(dependencies.family())
        if not dep_plan:p.error('Sem plano nativo para esta distro. Use --backend nix com Nix instalado, ou prepare dependências e use --skip-deps.')
        commands=dep_plan+commands
    print(f'Sistema: {distro()} | backend: {a.backend} | região: {a.region}',flush=True)
    env=os.environ.copy();env.update(RCLOL_REGION=a.region.upper(),RCLOL_LOCALE=a.locale or LOCALES[a.region],JOBS=str(a.jobs))
    for key in ('RCLOL_REGION','RCLOL_LOCALE','JOBS'):print(f'{key}={env[key]}',flush=True)
    for cmd in commands:print('+ '+shlex.join(cmd),flush=True)
    if a.dry_run:return 0
    if hasattr(os,'geteuid') and os.geteuid()==0:p.error('Execute como usuário normal, sem sudo. Só a instalação base solicita sudo.')
    if a.backend=='nix' and not shutil.which('nix'):
        p.error('Nix não encontrado. Veja docs/INSTALACAO-FACIL.md e https://nixos.org/download/; o script não instala Nix automaticamente.')
    if a.action=='install':
        print('AVISO: runtime não oficial; há relatos de suspensão de contas. A compilação pode levar bastante tempo.',flush=True)
        if not sys.stdin.isatty():p.error('A instalação exige terminal interativo para os prompts do instalador.')
        if a.backend=='native':
            print('O gerenciador de pacotes preparará as dependências e pedirá sua confirmação. O preflight verificará antes do build.',flush=True)
            # Refuse a live prefix instead of overwriting active runtime libraries.
            for proc in Path('/proc').iterdir():
                if not proc.name.isdigit():continue
                try:comm=(proc/'comm').read_text().strip()
                except OSError:continue
                if comm in ('darlingserver','mldr','CrBrowserMain','CrGpuMain'):
                    p.error('Feche os clientes e encerre o runtime Darling antes de instalar. Nenhum processo será morto automaticamente.')
    try:
        for step,cmd in enumerate(commands,1):
            print(f'\nEtapa {step}/{len(commands)}: {shlex.join(cmd)}',flush=True)
            subprocess.run(cmd,cwd=ROOT,env=env,check=True)
    except (subprocess.CalledProcessError,OSError) as e:
        print(f'Etapa interrompida: {e}. Corrija o erro acima e execute novamente; os scripts upstream reutilizam o build.',file=sys.stderr)
        return 1
    return 0
if __name__=='__main__':sys.exit(main())
