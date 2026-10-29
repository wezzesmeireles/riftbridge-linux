#!/usr/bin/env python3
"""Friendly desktop front end; installation prompts stay in a real terminal."""
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
    'edge': '#263a50', 'text': '#edf4fb', 'muted': '#9aadc2',
    'cyan': '#61d9dc', 'cyan_dark': '#163f4d', 'gold': '#d6b36d',
    'green': '#83d6a8', 'red': '#f0a18f',
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
    raise RuntimeError('Não encontrei um terminal compatível. Instale Konsole, GNOME Terminal, xfce4-terminal ou xterm.')


def environment_cards():
    """Return honest, read-only environment hints for the dashboard."""
    family = dependencies.family()
    distro = easy.distro()
    if shutil.which('nix'):
        backend = 'Nix instalado'
        backend_note = 'O modo automático usará Nix'
    elif family:
        backend = 'Instalação nativa'
        backend_note = 'Dependências serão preparadas com confirmação'
    else:
        backend = 'Precisa de configuração'
        backend_note = 'Use Nix ou configure dependências manualmente'
    darling = shutil.which('darling')
    runtime = 'Darling encontrado' if darling else 'Será preparado na instalação'
    return (distro, backend, backend_note, runtime)


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
    root.geometry('900x790')
    root.minsize(720, 690)
    root.configure(bg=COLORS['bg'])
    root.option_add('*Font', 'Sans 10')

    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('.', background=COLORS['bg'], foreground=COLORS['text'], font=('Sans', 10))
    style.configure('TFrame', background=COLORS['bg'])
    style.configure('Card.TFrame', background=COLORS['panel'])
    style.configure('Inset.TFrame', background=COLORS['panel_alt'])
    style.configure('TLabel', background=COLORS['bg'], foreground=COLORS['text'])
    style.configure('Card.TLabel', background=COLORS['panel'], foreground=COLORS['text'])
    style.configure('Inset.TLabel', background=COLORS['panel_alt'], foreground=COLORS['text'])
    style.configure('Muted.TLabel', foreground=COLORS['muted'])
    style.configure('CardMuted.TLabel', background=COLORS['panel'], foreground=COLORS['muted'])
    style.configure('Brand.TLabel', font=('Sans', 27, 'bold'), foreground=COLORS['cyan'])
    style.configure('Subtitle.TLabel', font=('Sans', 12), foreground=COLORS['gold'])
    style.configure('Section.TLabel', font=('Sans', 14, 'bold'))
    style.configure('CardTitle.TLabel', background=COLORS['panel'], foreground=COLORS['muted'], font=('Sans', 9, 'bold'))
    style.configure('CardValue.TLabel', background=COLORS['panel'], foreground=COLORS['text'], font=('Sans', 12, 'bold'))
    style.configure('Primary.TButton', font=('Sans', 12, 'bold'), padding=(18, 14), background=COLORS['cyan_dark'], foreground=COLORS['text'], borderwidth=1, relief='flat')
    style.map('Primary.TButton', background=[('active', '#20586a'), ('disabled', '#263546')], foreground=[('disabled', '#7f91a4')])
    style.configure('Action.TButton', font=('Sans', 10, 'bold'), padding=(12, 11), background=COLORS['panel_alt'], foreground=COLORS['text'], borderwidth=0, relief='flat')
    style.map('Action.TButton', background=[('active', '#243a52')])
    style.configure('TCombobox', padding=7, fieldbackground=COLORS['panel_alt'], background=COLORS['panel_alt'], foreground=COLORS['text'], arrowcolor=COLORS['cyan'])
    style.map('TCombobox', fieldbackground=[('readonly', COLORS['panel_alt'])], foreground=[('readonly', COLORS['text'])])
    style.configure('TCheckbutton', background=COLORS['panel'], foreground=COLORS['muted'])
    style.map('TCheckbutton', background=[('active', COLORS['panel'])])

    page = ttk.Frame(root, padding=(30, 24))
    page.pack(fill='both', expand=True)
    page.columnconfigure(0, weight=1)

    header = ttk.Frame(page)
    header.grid(row=0, column=0, sticky='ew')
    ttk.Label(header, text='RiftBridge', style='Brand.TLabel').pack(anchor='w')
    ttk.Label(header, text='LEAGUE OF LEGENDS  ·  LINUX VIA DARLING', style='Subtitle.TLabel').pack(anchor='w', pady=(2, 0))
    ttk.Label(header, text='Assistente comunitário para preparar, abrir e diagnosticar o cliente.', style='Muted.TLabel').pack(anchor='w', pady=(9, 0))

    distro, backend_label, backend_note, runtime_label = environment_cards()
    cards = ttk.Frame(page)
    cards.grid(row=1, column=0, sticky='ew', pady=(20, 18))
    for col in range(3):
        cards.columnconfigure(col, weight=1, uniform='cards')
    for col, (title, value, note) in enumerate((
        ('SISTEMA DETECTADO', distro, 'Linux x86_64'),
        ('MODO AUTOMÁTICO', backend_label, backend_note),
        ('RUNTIME', runtime_label, 'Estado informativo; sem alterações'),
    )):
        card = ttk.Frame(cards, style='Card.TFrame', padding=(15, 13))
        card.grid(row=0, column=col, sticky='nsew', padx=(0 if col == 0 else 7, 0 if col == 2 else 7))
        ttk.Label(card, text=title, style='CardTitle.TLabel').pack(anchor='w')
        ttk.Label(card, text=value, style='CardValue.TLabel', wraplength=220).pack(anchor='w', pady=(8, 4))
        ttk.Label(card, text=note, style='CardMuted.TLabel', wraplength=220).pack(anchor='w')

    setup = ttk.Frame(page, style='Card.TFrame', padding=(20, 18))
    setup.grid(row=2, column=0, sticky='ew')
    setup.columnconfigure(0, weight=1)
    ttk.Label(setup, text='Comece por aqui', style='Section.TLabel').pack(anchor='w')
    ttk.Label(setup, text='A instalação guiada escolhe o caminho adequado e mostra cada confirmação no terminal.', style='CardMuted.TLabel', wraplength=780).pack(anchor='w', pady=(5, 13))

    settings = ttk.Frame(setup, style='Card.TFrame')
    settings.pack(fill='x')
    ttk.Label(settings, text='Região do servidor', style='Card.TLabel').pack(side='left', padx=(0, 12))
    selected_region = next((label for label, code in REGIONS.items() if code == args.region), 'Brasil (BR)')
    region = tk.StringVar(value=selected_region)
    ttk.Combobox(settings, textvariable=region, values=tuple(REGIONS), state='readonly', width=27).pack(side='left')

    advanced_row = ttk.Frame(setup, style='Card.TFrame')
    advanced_row.pack(fill='x', pady=(10, 0))
    show_advanced = tk.BooleanVar(value=False)
    advanced = ttk.Frame(setup, style='Inset.TFrame', padding=(12, 10))
    backend = tk.StringVar(value=args.backend)
    ttk.Label(advanced, text='Forçar modo', style='Inset.TLabel').pack(side='left', padx=(0, 12))
    ttk.Combobox(advanced, textvariable=backend, values=('auto', 'nix', 'native'), state='readonly', width=14).pack(side='left')
    ttk.Label(advanced, text='Auto é recomendado para a maioria das pessoas.', style='Inset.TLabel').pack(side='left', padx=(12, 0))

    def toggle_advanced():
        if show_advanced.get():
            advanced.pack(fill='x', pady=(10, 0))
        else:
            advanced.pack_forget()

    ttk.Checkbutton(advanced_row, text='Mostrar opções avançadas', variable=show_advanced, command=toggle_advanced).pack(anchor='w')

    steps = ttk.Frame(page, style='Card.TFrame', padding=(20, 16))
    steps.grid(row=3, column=0, sticky='ew', pady=(14, 0))
    ttk.Label(steps, text='O que vai acontecer', style='Section.TLabel').pack(anchor='w', pady=(0, 11))
    for number, title, detail in (
        ('1', 'Preparar o ambiente', 'Detecta sua distro e instala dependências após sua confirmação.'),
        ('2', 'Compilar e configurar', 'Constrói o Darling e configura o cliente no seu usuário.'),
        ('3', 'Abrir o cliente', 'Depois da instalação, use Abrir Riot / LoL para iniciar.'),
    ):
        line = ttk.Frame(steps, style='Card.TFrame')
        line.pack(fill='x', pady=4)
        badge = tk.Label(line, text=number, bg=COLORS['cyan_dark'], fg=COLORS['cyan'], font=('Sans', 10, 'bold'), width=3, height=1, padx=3, pady=4)
        badge.pack(side='left', padx=(0, 11))
        textcol = ttk.Frame(line, style='Card.TFrame')
        textcol.pack(side='left', fill='x', expand=True)
        ttk.Label(textcol, text=title, style='Card.TLabel', font=('Sans', 10, 'bold')).pack(anchor='w')
        ttk.Label(textcol, text=detail, style='CardMuted.TLabel', wraplength=720).pack(anchor='w', pady=(2, 0))

    status_card = ttk.Frame(page, style='Inset.TFrame', padding=(14, 11))
    status_card.grid(row=4, column=0, sticky='ew', pady=(14, 9))
    status_card.columnconfigure(0, weight=1)
    status = tk.StringVar(value='Pronto para começar · modo automático · região Brasil')
    ttk.Label(status_card, text='STATUS', style='Inset.TLabel', foreground=COLORS['cyan'], font=('Sans', 8, 'bold')).grid(row=0, column=0, sticky='w')
    ttk.Label(status_card, textvariable=status, style='Inset.TLabel', wraplength=780).grid(row=1, column=0, sticky='w', pady=(3, 0))

    button_area = ttk.Frame(page)
    button_area.grid(row=5, column=0, sticky='ew')
    button_area.columnconfigure(0, weight=2)
    button_area.columnconfigure(1, weight=1)
    button_area.columnconfigure(2, weight=1)
    children = {}
    primary = ttk.Button(button_area, text='Instalar RiftBridge', style='Primary.TButton')
    primary.grid(row=0, column=0, sticky='ew', padx=(0, 8))

    def start(action, preview=False):
        try:
            old = children.get(action)
            if old is not None and old.poll() is None:
                status.set('Essa ação já está aberta. Confira o terminal que iniciou.')
                return
            code = REGIONS.get(region.get())
            cmd = command(action, backend.get(), code)
            if preview:
                cmd.append('--dry-run')
            terminal_cmd = ['python3', str(ROOT / 'scripts/terminal-task.py'), *cmd[2:]]
            proc = subprocess.Popen(in_terminal(terminal_cmd), cwd=ROOT, start_new_session=True)
            children[action] = proc
            status.set(f'Em andamento: {action_labels[action]}. Acompanhe os detalhes e confirmações no terminal.')
        except (OSError, RuntimeError, ValueError) as exc:
            messagebox.showerror('Não foi possível iniciar', str(exc))
            status.set('Não foi possível abrir o terminal. Veja a mensagem para corrigir.')

    action_labels = {'install': 'instalação', 'run': 'abertura do cliente', 'doctor': 'diagnóstico'}
    primary.configure(command=lambda: start('install'))
    ttk.Button(button_area, text='Abrir Riot / LoL', style='Action.TButton', command=lambda: start('run')).grid(row=0, column=1, sticky='ew', padx=4)
    ttk.Button(button_area, text='Diagnosticar', style='Action.TButton', command=lambda: start('doctor')).grid(row=0, column=2, sticky='ew', padx=(8, 0))

    secondary = ttk.Frame(page)
    secondary.grid(row=6, column=0, sticky='ew', pady=(8, 0))
    ttk.Button(secondary, text='Prévia dos comandos', style='Action.TButton', command=lambda: start('install', True)).pack(side='left')
    ttk.Button(secondary, text='Abrir guia de instalação', style='Action.TButton', command=lambda: open_guide(messagebox)).pack(side='left', padx=8)

    risk = ttk.Label(page, text='Projeto comunitário experimental e sem vínculo com a Riot. A Riot pode restringir o acesso a clientes não oficiais; não há garantia de funcionamento ou de ausência de suspensão.', style='Muted.TLabel', wraplength=810, justify='left')
    risk.grid(row=7, column=0, sticky='ew', pady=(12, 0))

    def monitor_terminals():
        for action, proc in tuple(children.items()):
            result = proc.poll()
            if result is not None:
                del children[action]
                if result == 0:
                    status.set(f'{action_labels[action].capitalize()} encerrada. O terminal mostra o resultado final.')
                else:
                    status.set(f'{action_labels[action].capitalize()} terminou com erro. Veja a etapa indicada no terminal e tente novamente após corrigir.')
        root.after(900, monitor_terminals)

    def open_guide(dialog):
        guide = ROOT / 'docs/INSTALACAO-FACIL.md'
        opener = shutil.which('xdg-open')
        try:
            if opener:
                subprocess.Popen([opener, str(guide)], cwd=ROOT)
            else:
                dialog.showinfo('Guia de instalação', str(guide))
        except OSError as exc:
            dialog.showerror('Não foi possível abrir o guia', str(exc))

    monitor_terminals()
    root.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
