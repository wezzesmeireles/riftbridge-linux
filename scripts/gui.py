#!/usr/bin/env python3
"""RiftBridge: desktop front end; privileged prompts stay in a real terminal."""
import argparse
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def command(action,backend,region):
    if action not in ('install','run','doctor') or backend not in ('auto','nix','native'):
        raise ValueError('Invalid action or backend')
    if region not in ('br','euw','eune','na','kr','jp','la1','la2','oc1','ru','tr'):
        raise ValueError('Invalid region')
    return ['python3',str(ROOT/'scripts/easy.py'),action,'--backend',backend,'--region',region]

def in_terminal(cmd):
    choices=[('konsole',['--hold','-e']),('gnome-terminal',['--wait','--']),
             ('xfce4-terminal',['--hold','--execute']),('xterm',['-hold','-e']),
             ('x-terminal-emulator',['-e'])]
    for binary,flags in choices:
        path=shutil.which(binary)
        if path:return [path,*flags,*cmd]
    raise RuntimeError('Nenhum terminal compatível encontrado. Instale Konsole, GNOME Terminal, xfce4-terminal ou xterm.')

def main():
    parser=argparse.ArgumentParser(description='RiftBridge Linux — interface de instalação')
    parser.add_argument('--print-command',choices=('install','run','doctor'))
    parser.add_argument('--backend',choices=('auto','nix','native'),default='auto')
    parser.add_argument('--region',default='br')
    args=parser.parse_args()
    if args.print_command:
        print(shlex.join(command(args.print_command,args.backend,args.region)));return 0
    try:
        import tkinter as tk
        from tkinter import ttk,messagebox
    except ImportError:
        print('Tkinter não instalado. Fedora: sudo dnf install python3-tkinter; Ubuntu/Debian: sudo apt install python3-tk; Arch: sudo pacman -S tk; openSUSE: sudo zypper install python3-tk. Ou use ./install.sh.',file=sys.stderr)
        # The installation wizard works without Tkinter and can install it through distro packages.
        try:return subprocess.call(in_terminal(command('install',args.backend,args.region)),cwd=ROOT)
        except (OSError,RuntimeError) as exc:print(str(exc),file=sys.stderr);return 1
    root=tk.Tk();root.title('RiftBridge Linux');root.geometry('760x650');root.minsize(680,630)
    root.configure(bg='#101b29')
    style=ttk.Style();style.theme_use('clam')
    style.configure('TFrame',background='#101b29');style.configure('TLabel',background='#101b29',foreground='#dce8f2',font=('Sans',11))
    style.configure('TButton',font=('Sans',11),padding=12,background='#1d3448',foreground='#e4f4fa',borderwidth=0)
    style.map('TButton',background=[('active','#28546a')])
    style.configure('Title.TLabel',font=('Sans',27,'bold'),foreground='#5ed9de')
    style.configure('Sub.TLabel',font=('Sans',12),foreground='#c5ab71')
    frame=ttk.Frame(root,padding=28);frame.pack(fill='both',expand=True)
    ttk.Label(frame,text='RiftBridge Linux',style='Title.TLabel').pack(anchor='w')
    ttk.Label(frame,text='League of Legends no Linux via Darling',style='Sub.TLabel').pack(anchor='w',pady=(4,20))
    ttk.Label(frame,text='Escolha a região e clique em Instalar. O modo auto escolhe o ambiente.\nOs prompts e erros ficam visíveis; a compilação pode demorar.',wraplength=680).pack(anchor='w')
    opts=ttk.Frame(frame);opts.pack(fill='x',pady=18)
    backend=tk.StringVar(value=args.backend);region=tk.StringVar(value=args.region)
    ttk.Label(opts,text='Região').pack(side='left',padx=(0,10))
    ttk.Combobox(opts,textvariable=region,values=('br','euw','eune','na','kr','jp','la1','la2','oc1','ru','tr'),state='readonly',width=10).pack(side='left')
    advanced=ttk.Frame(frame)
    ttk.Label(advanced,text='Modo de instalação').pack(side='left',padx=(0,10))
    ttk.Combobox(advanced,textvariable=backend,values=('auto','nix','native'),state='readonly',width=18).pack(side='left')
    show_advanced=tk.BooleanVar(value=False)
    def toggle_advanced():
        if show_advanced.get():advanced.pack(fill='x',after=opts,pady=8)
        else:advanced.pack_forget()
    ttk.Checkbutton(opts,text='Opções avançadas',variable=show_advanced,command=toggle_advanced).pack(side='right')
    status=tk.StringVar(value='Pronto. O modo auto prepara dependências nas distros reconhecidas.')
    buttons=ttk.Frame(frame);buttons.pack(fill='x',pady=8)
    children={}
    def start(action,preview=False):
        try:
            old=children.get(action)
            if old is not None and old.poll() is None:
                status.set('Esta etapa já está aberta. Confira o terminal.');return
            cmd=command(action,backend.get(),region.get())
            if preview:cmd.append('--dry-run')
            terminal_cmd=['python3',str(ROOT/'scripts/terminal-task.py'),*cmd[2:]]
            proc=subprocess.Popen(in_terminal(terminal_cmd),cwd=ROOT,start_new_session=True)
            children[action]=proc;status.set('Terminal aberto. Acompanhe os prompts e o resultado nessa janela.')
        except (OSError,RuntimeError,ValueError) as exc:messagebox.showerror('Não foi possível abrir',str(exc))
    for col,(label,action) in enumerate([('Instalar','install'),('Abrir Riot / LoL','run'),('Diagnosticar','doctor')]):
        ttk.Button(buttons,text=label,command=lambda a=action:start(a)).grid(row=0,column=col,padx=(0,8),sticky='ew');buttons.columnconfigure(col,weight=1)
    ttk.Button(frame,text='Ver comandos sem instalar',command=lambda:start('install',True)).pack(anchor='w',pady=(12,14))
    ttk.Label(frame,textvariable=status,wraplength=680).pack(anchor='w',pady=10)
    ttk.Label(frame,text='Experimental • Sem vínculo com a Riot\nHá relatos de suspensão por software de terceiros.\nNão há garantia de funcionamento em todas as distros.',wraplength=680,foreground='#e8b47c').pack(anchor='w',pady=10)
    def guide():
        opener=shutil.which('xdg-open')
        if opener:subprocess.Popen([opener,str(ROOT/'docs/INSTALACAO-FACIL.md')])
        else:messagebox.showinfo('Guia',str(ROOT/'docs/INSTALACAO-FACIL.md'))
    ttk.Button(frame,text='Abrir guia completo',command=guide).pack(anchor='w')
    root.mainloop();return 0
if __name__=='__main__':sys.exit(main())
