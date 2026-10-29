#!/usr/bin/env python3
"""Compact desktop front end; privileged prompts stay in a real terminal."""
import argparse
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import dependencies
import easy

REGIONS = {
    'Brasil (BR)': 'br', 'Europa Oeste (EUW)': 'euw',
    'Europa Norte/Leste (EUNE)': 'eune', 'América do Norte (NA)': 'na',
    'Coreia (KR)': 'kr', 'Japão (JP)': 'jp', 'América Latina Norte (LAN)': 'la1',
    'América Latina Sul (LAS)': 'la2', 'Oceania (OCE)': 'oc1',
    'Rússia (RU)': 'ru', 'Turquia (TR)': 'tr',
}
COLORS = {
    'bg': '#0b1220', 'panel': '#121e30', 'panel_alt': '#17263a',
    'text': '#edf4fb', 'muted': '#9aadc2', 'cyan': '#61d9dc',
    'cyan_dark': '#164958', 'gold': '#d6b36d', 'green': '#83d6a8',
}


def command(action, backend, region):
    if action not in ('install', 'run', 'doctor') or backend not in ('auto', 'nix', 'native'):
        raise ValueError('Ação ou modo de instalação inválido')
    if region not in ('br', 'euw', 'eune', 'na', 'kr', 'jp', 'la1', 'la2', 'oc1', 'ru', 'tr'):
        raise ValueError('Região inválida')
    return ['python3', str(ROOT / 'scripts/easy.py'), action, '--backend', backend, '--region', region]


def in_terminal(cmd):
    choices = [
        ('konsole', ['--hold', '-e']), ('gnome-terminal', ['--wait', '--']),
        ('xfce4-terminal', ['--hold', '--execute']), ('xterm', ['-hold', '-e']),
        ('x-terminal-emulator', ['-e']),
    ]
    for binary, flags in choices:
        path = shutil.which(binary)
        if path:
            return [path, *flags, *cmd]
    raise RuntimeError('Não encontrei terminal compatível: Konsole, GNOME Terminal, xfce4-terminal ou xterm.')


def environment_summary():
    family = dependencies.family()
    if shutil.which('nix'):
        route = 'auto · Nix'
    elif family:
        route = 'auto · nativo'
    else:
        route = 'auto · requer configuração'
    runtime = 'Darling disponível' if shutil.which('darling') else 'Darling será preparado'
    return easy.distro(), route, runtime


def main():
    parser = argparse.ArgumentParser(description='RiftBridge Linux — interface gráfica')
    parser.add_argument('--print-command', choices=('install', 'run', 'doctor'))
    parser.add_argument('--backend', choices=('auto', 'nix', 'native'), default='auto')
    parser.add_argument('--region', default='br')
    args = parser.parse_args()
    if args.print_command:
        print(shlex.join(command(args.print_command, args.backend, args.region)))
        return 0

    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ImportError:
        print('Tkinter não está instalado. O assistente continuará no terminal.', file=sys.stderr)
        try:
            return subprocess.call(in_terminal(command('install', args.backend, args.region)), cwd=ROOT)
        except (OSError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            return 1

    root = tk.Tk()
    root.title('RiftBridge Linux')
    root.geometry('720x610')
    root.minsize(600, 520)
    root.configure(bg=COLORS['bg'])
    root.option_add('*Font', 'Sans 10')

    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background=COLORS['bg'], foreground=COLORS['text'], font=('Sans', 10))
    style.configure('TFrame', background=COLORS['bg'])
    style.configure('Panel.TFrame', background=COLORS['panel'])
    style.configure('Inset.TFrame', background=COLORS['panel_alt'])
    style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['text'])
    style.configure('Muted.TLabel', background=COLORS['bg'], foreground=COLORS['muted'])
    style.configure('Panel.TLabel', background=COLORS['panel'], foreground=COLORS['text'])
    style.configure('PanelMuted.TLabel', background=COLORS['panel'], foreground=COLORS['muted'])
    style.configure('Inset.TLabel', background=COLORS['panel_alt'], foreground=COLORS['text'])
    style.configure('Brand.TLabel', background=COLORS['bg'], foreground=COLORS['cyan'], font=('Sans', 23, 'bold'))
    style.configure('Eyebrow.TLabel', background=COLORS['bg'], foreground=COLORS['gold'], font=('Sans', 9, 'bold'))
    style.configure('PanelEyebrow.TLabel', background=COLORS['panel'], foreground=COLORS['gold'], font=('Sans', 9, 'bold'))
    style.configure('Primary.TButton', font=('Sans', 13, 'bold'), padding=(16, 13), background=COLORS['cyan_dark'], foreground=COLORS['text'], borderwidth=0, relief='flat')
    style.map('Primary.TButton', background=[('active', '#206174'), ('disabled', '#263546')])
    style.configure('Action.TButton', font=('Sans', 10, 'bold'), padding=(11, 9), background=COLORS['panel_alt'], foreground=COLORS['text'], borderwidth=0, relief='flat')
    style.map('Action.TButton', background=[('active', '#243a52')])
    style.configure('TCombobox', padding=6, fieldbackground=COLORS['panel_alt'], background=COLORS['panel_alt'], foreground=COLORS['text'], arrowcolor=COLORS['cyan'])
    style.map('TCombobox', fieldbackground=[('readonly', COLORS['panel_alt'])], foreground=[('readonly', COLORS['text'])])
    style.configure('TCheckbutton', background=COLORS['panel'], foreground=COLORS['muted'])
    style.map('TCheckbutton', background=[('active', COLORS['panel'])])

    page = ttk.Frame(root, padding=(24, 18))
    page.pack(fill='both', expand=True)

    header = ttk.Frame(page)
    header.pack(fill='x')
    ttk.Label(header, text='RiftBridge', style='Brand.TLabel').pack(anchor='w')
    ttk.Label(header, text='LEAGUE OF LEGENDS  ·  LINUX VIA DARLING', style='Eyebrow.TLabel').pack(anchor='w', pady=(1, 0))
    ttk.Label(header, text='Instale e abra pelo modo automático.', style='Muted.TLabel').pack(anchor='w', pady=(5, 0))

    distro, route, runtime = environment_summary()
    status_pill = ttk.Frame(page, style='Inset.TFrame', padding=(11, 8))
    status_pill.pack(fill='x', pady=(13, 13))
    ttk.Label(status_pill, text=f'{distro}   ·   {route}   ·   {runtime}', style='Inset.TLabel', wraplength=650).pack(anchor='w')

    install_card = ttk.Frame(page, style='Panel.TFrame', padding=(17, 15))
    install_card.pack(fill='x')
    ttk.Label(install_card, text='PRONTO PARA JOGAR?', style='PanelEyebrow.TLabel').pack(anchor='w')
    ttk.Label(install_card, text='Comece com um clique', style='Panel.TLabel', font=('Sans', 17, 'bold')).pack(anchor='w', pady=(4, 1))
    ttk.Label(install_card, text='A instalação abre no terminal para você confirmar pacotes e permissões.', style='PanelMuted.TLabel', wraplength=630).pack(anchor='w', pady=(0, 12))

    options = ttk.Frame(install_card, style='Panel.TFrame')
    options.pack(fill='x', pady=(0, 11))
    ttk.Label(options, text='Servidor', style='Panel.TLabel').pack(side='left', padx=(0, 10))
    selected_region = next((label for label, code in REGIONS.items() if code == args.region), 'Brasil (BR)')
    region = tk.StringVar(value=selected_region)
    ttk.Combobox(options, textvariable=region, values=tuple(REGIONS), state='readonly', width=22).pack(side='left')

    advanced_visible = tk.BooleanVar(value=False)
    backend = tk.StringVar(value=args.backend)
    advanced = ttk.Frame(install_card, style='Panel.TFrame')
    ttk.Label(advanced, text='Modo', style='Panel.TLabel').pack(side='left', padx=(0, 10))
    ttk.Combobox(advanced, textvariable=backend, values=('auto', 'nix', 'native'), state='readonly', width=12).pack(side='left')

    def toggle_advanced():
        if advanced_visible.get():
            advanced.pack(fill='x', pady=(0, 10))
        else:
            advanced.pack_forget()

    ttk.Checkbutton(options, text='Avançado', variable=advanced_visible, command=toggle_advanced).pack(side='right')

    state = tk.StringVar(value='Pronto · Brasil · instalação automática')
    children = {}
    action_labels = {'install': 'instalação', 'run': 'abertura do cliente', 'doctor': 'diagnóstico'}

    def start(action, preview=False):
        try:
            old = children.get(action)
            if old is not None and old.poll() is None:
                state.set('Esta ação já está aberta. Acompanhe o terminal iniciado.')
                return
            code = REGIONS.get(region.get())
            cmd = command(action, backend.get(), code)
            if preview:
                cmd.append('--dry-run')
            terminal = ['python3', str(ROOT / 'scripts/terminal-task.py'), *cmd[2:]]
            children[action] = subprocess.Popen(in_terminal(terminal), cwd=ROOT, start_new_session=True)
            state.set(f'{action_labels[action].capitalize()} em andamento · confira o terminal para confirmações e detalhes.')
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror('Não foi possível iniciar', str(exc))
            state.set('Não foi possível iniciar. Confira a mensagem exibida.')

    ttk.Button(install_card, text='Instalar RiftBridge', style='Primary.TButton', command=lambda: start('install')).pack(fill='x')
    ttk.Label(install_card, text='O modo automático escolhe Nix ou prepara as dependências da distro.', style='PanelMuted.TLabel', wraplength=630).pack(anchor='w', pady=(8, 0))

    actions = ttk.Frame(page)
    actions.pack(fill='x', pady=(12, 0))
    actions.columnconfigure((0, 1), weight=1, uniform='actions')
    ttk.Button(actions, text='Abrir Riot / LoL', style='Action.TButton', command=lambda: start('run')).grid(row=0, column=0, sticky='ew', padx=(0, 5))
    ttk.Button(actions, text='Diagnosticar', style='Action.TButton', command=lambda: start('doctor')).grid(row=0, column=1, sticky='ew', padx=(5, 0))

    links = ttk.Frame(page)
    links.pack(fill='x', pady=(6, 0))
    ttk.Button(links, text='Prévia', style='Action.TButton', command=lambda: start('install', True)).pack(side='left')

    def open_guide():
        guide = ROOT / 'docs/INSTALACAO-FACIL.md'
        opener = shutil.which('xdg-open')
        try:
            if opener:
                subprocess.Popen([opener, str(guide)], cwd=ROOT)
            else:
                messagebox.showinfo('Guia de instalação', str(guide))
        except OSError as exc:
            messagebox.showerror('Não foi possível abrir o guia', str(exc))

    ttk.Button(links, text='Guia', style='Action.TButton', command=open_guide).pack(side='left', padx=(6, 0))

    status_line = ttk.Frame(page, style='Inset.TFrame', padding=(10, 8))
    status_line.pack(fill='x', pady=(10, 7))
    ttk.Label(status_line, textvariable=state, style='Inset.TLabel', wraplength=640).pack(anchor='w')
    ttk.Label(page, text='Experimental · sem vínculo com a Riot. Clientes não oficiais podem levar a restrições de conta.', style='Muted.TLabel', wraplength=660, justify='left', font=('Sans', 8)).pack(anchor='w')

    def monitor_terminals():
        for action, proc in tuple(children.items()):
            result = proc.poll()
            if result is not None:
                del children[action]
                if result == 0:
                    state.set(f'{action_labels[action].capitalize()} concluída · o terminal mostra o resultado final.')
                else:
                    state.set(f'{action_labels[action].capitalize()} terminou com erro · veja a etapa no terminal.')
        root.after(900, monitor_terminals)

    monitor_terminals()
    root.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
