#!/usr/bin/env python3
"""Compact, animated desktop front end for RiftBridge Linux."""
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
    route = 'auto · Nix' if shutil.which('nix') else ('auto · nativo' if family else 'auto · requer configuração')
    runtime = 'Darling disponível' if shutil.which('darling') else 'Darling será preparado'
    return easy.distro(), route, runtime


def rounded_shape(canvas, x1, y1, x2, y2, radius, fill, outline=''):
    radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    points = [x1 + radius, y1, x2 - radius, y1, x2, y1,
              x2, y1 + radius, x2, y2 - radius, x2, y2,
              x2 - radius, y2, x1 + radius, y2, x1, y2,
              x1, y2 - radius, x1, y1 + radius, x1, y1]
    return canvas.create_polygon(points, smooth=True, splinesteps=24, fill=fill, outline=outline, width=1)


def mix_color(start, end, amount):
    a = tuple(int(start[i:i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(end[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02x%02x%02x' % tuple(round(x + (y - x) * amount) for x, y in zip(a, b))


class RoundedPanel:
    """Rounded card with a regular Tk frame inset for its contents."""
    def __init__(self, parent, tk, background, outer, padding=14, radius=16):
        self.background, self.outer = background, outer
        self.padding, self.radius = padding, radius
        self.canvas = tk.Canvas(parent, bg=outer, highlightthickness=0, borderwidth=0)
        self.inner = tk.Frame(self.canvas, bg=background, borderwidth=0)
        self.window = self.canvas.create_window((padding, padding), anchor='nw', window=self.inner)
        self.shape = None
        self.canvas.bind('<Configure>', self.resize)
        self.inner.bind('<Configure>', self.resize)

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

    def resize(self, _event=None):
        width = self.canvas.winfo_width()
        if width < 4:
            return
        self.canvas.itemconfigure(self.window, width=max(1, width - 2 * self.padding))
        height = max(self.inner.winfo_reqheight() + 2 * self.padding, 42)
        self.canvas.configure(height=height)
        points = [1 + self.radius, 1, width - 2 - self.radius, 1, width - 2, 1,
                  width - 2, 1 + self.radius, width - 2, height - 2 - self.radius,
                  width - 2, height - 2, width - 2 - self.radius, height - 2,
                  1 + self.radius, height - 2, 1, height - 2, 1, height - 2 - self.radius,
                  1, 1 + self.radius, 1, 1]
        if self.shape is None:
            self.shape = self.canvas.create_polygon(points, smooth=True, splinesteps=24, fill=self.background, outline='')
            self.canvas.tag_lower(self.shape)
        else:
            self.canvas.coords(self.shape, *points)


class AnimatedButton:
    """Rounded canvas button with eased, brief hover and press transitions."""
    def __init__(self, parent, tk, text, callback, primary=False, background=None):
        self.tk, self.callback, self.text = tk, callback, text
        self.primary = primary
        self.background = background or COLORS['bg']
        self.base = COLORS['cyan_dark'] if primary else COLORS['panel_alt']
        self.hover = '#206174' if primary else '#243a52'
        self.current = self.base
        self.generation = 0
        self.height = 48 if primary else 40
        self.canvas = tk.Canvas(parent, height=self.height, bg=self.background, highlightthickness=0, borderwidth=0, cursor='hand2', takefocus=True)
        self.canvas.bind('<Configure>', self.draw)
        self.canvas.bind('<Enter>', lambda _event: self.animate(self.hover))
        self.canvas.bind('<Leave>', lambda _event: self.animate(self.base))
        self.canvas.bind('<ButtonPress-1>', self.press)
        self.canvas.bind('<ButtonRelease-1>', self.release)
        self.canvas.bind('<Return>', lambda _event: self.callback())
        self.canvas.bind('<space>', lambda _event: self.callback())
        self.canvas.bind('<FocusIn>', lambda _event: self.canvas.configure(highlightthickness=1, highlightbackground=COLORS['cyan']))
        self.canvas.bind('<FocusOut>', lambda _event: self.canvas.configure(highlightthickness=0))
        self.draw()

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

    def grid(self, **kwargs):
        self.canvas.grid(**kwargs)

    def draw(self, _event=None):
        width = max(self.canvas.winfo_width(), 10)
        self.canvas.delete('all')
        outline = COLORS['cyan'] if self.primary and self.current == self.hover else ''
        rounded_shape(self.canvas, 1, 1, width - 2, self.height - 2, 13, self.current, outline)
        self.canvas.create_text(width / 2, self.height / 2, text=self.text,
                                fill=COLORS['text'], font=('Sans', 12 if self.primary else 10, 'bold'))

    def animate(self, target):
        self.generation += 1
        token, start = self.generation, self.current
        for step in range(1, 7):
            self.canvas.after(step * 18, lambda n=step: self.step(token, start, target, n / 6))

    def step(self, token, start, target, amount):
        if token == self.generation:
            self.current = mix_color(start, target, amount)
            self.draw()

    def press(self, _event):
        self.animate('#123c4b' if self.primary else '#1c2c40')

    def release(self, event):
        inside = 0 <= event.x <= self.canvas.winfo_width() and 0 <= event.y <= self.height
        self.animate(self.hover if inside else self.base)
        if inside:
            self.callback()


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
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TCombobox', padding=6, fieldbackground=COLORS['panel_alt'], background=COLORS['panel_alt'], foreground=COLORS['text'], arrowcolor=COLORS['cyan'])
    style.map('TCombobox', fieldbackground=[('readonly', COLORS['panel_alt'])], foreground=[('readonly', COLORS['text'])])
    style.configure('TCheckbutton', background=COLORS['panel'], foreground=COLORS['muted'])
    style.map('TCheckbutton', background=[('active', COLORS['panel'])])

    page = tk.Frame(root, bg=COLORS['bg'])
    page.pack(fill='both', expand=True, padx=24, pady=17)
    header = tk.Frame(page, bg=COLORS['bg'])
    header.pack(fill='x')
    tk.Label(header, text='RiftBridge', bg=COLORS['bg'], fg=COLORS['cyan'], font=('Sans', 24, 'bold')).pack(anchor='w')
    tk.Label(header, text='LEAGUE OF LEGENDS  ·  LINUX VIA DARLING', bg=COLORS['bg'], fg=COLORS['gold'], font=('Sans', 9, 'bold')).pack(anchor='w', pady=(1, 0))
    tk.Label(header, text='Instale e abra pelo modo automático.', bg=COLORS['bg'], fg=COLORS['muted'], font=('Sans', 10)).pack(anchor='w', pady=(4, 0))

    distro, route, runtime = environment_summary()
    detected = RoundedPanel(page, tk, COLORS['panel_alt'], COLORS['bg'], padding=10, radius=15)
    detected.pack(fill='x', pady=(12, 12))
    tk.Label(detected.inner, text=f'{distro}   ·   {route}   ·   {runtime}', bg=COLORS['panel_alt'], fg=COLORS['text'], font=('Sans', 9), wraplength=650, justify='left').pack(anchor='w')

    install_card = RoundedPanel(page, tk, COLORS['panel'], COLORS['bg'], padding=16, radius=18)
    install_card.pack(fill='x')
    tk.Label(install_card.inner, text='PRONTO PARA JOGAR?', bg=COLORS['panel'], fg=COLORS['gold'], font=('Sans', 9, 'bold')).pack(anchor='w')
    tk.Label(install_card.inner, text='Comece com um clique', bg=COLORS['panel'], fg=COLORS['text'], font=('Sans', 17, 'bold')).pack(anchor='w', pady=(4, 1))
    tk.Label(install_card.inner, text='Confirmações de pacotes e permissões aparecem no terminal.', bg=COLORS['panel'], fg=COLORS['muted'], font=('Sans', 9), wraplength=630, justify='left').pack(anchor='w', pady=(0, 10))

    options = tk.Frame(install_card.inner, bg=COLORS['panel'])
    options.pack(fill='x', pady=(0, 10))
    tk.Label(options, text='Servidor', bg=COLORS['panel'], fg=COLORS['text'], font=('Sans', 10)).pack(side='left', padx=(0, 10))
    selected_region = next((label for label, code in REGIONS.items() if code == args.region), 'Brasil (BR)')
    region = tk.StringVar(value=selected_region)
    ttk.Combobox(options, textvariable=region, values=tuple(REGIONS), state='readonly', width=21).pack(side='left')

    state = tk.StringVar(value='Pronto · Brasil · instalação automática')
    children = {}
    action_labels = {'install': 'instalação', 'run': 'abertura do cliente', 'doctor': 'diagnóstico'}

    advanced_visible = tk.BooleanVar(value=False)
    backend = tk.StringVar(value=args.backend)
    advanced = tk.Frame(install_card.inner, bg=COLORS['panel'])
    tk.Label(advanced, text='Modo', bg=COLORS['panel'], fg=COLORS['text'], font=('Sans', 10)).pack(side='left', padx=(0, 10))
    ttk.Combobox(advanced, textvariable=backend, values=('auto', 'nix', 'native'), state='readonly', width=12).pack(side='left')

    def toggle_advanced():
        if advanced_visible.get():
            advanced.pack(fill='x', pady=(0, 10))
        else:
            advanced.pack_forget()

    ttk.Checkbutton(options, text='Avançado', variable=advanced_visible, command=toggle_advanced).pack(side='right')

    def start(action, preview=False):
        try:
            old = children.get(action)
            if old is not None and old.poll() is None:
                state.set('Essa ação já está aberta. Acompanhe o terminal iniciado.')
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

    AnimatedButton(install_card.inner, tk, 'Instalar RiftBridge', lambda: start('install'), primary=True, background=COLORS['panel']).pack(fill='x')
    tk.Label(install_card.inner, text='Auto escolhe Nix ou prepara as dependências da distro.', bg=COLORS['panel'], fg=COLORS['muted'], font=('Sans', 9), wraplength=630, justify='left').pack(anchor='w', pady=(7, 0))

    actions = tk.Frame(page, bg=COLORS['bg'])
    actions.pack(fill='x', pady=(11, 0))
    actions.columnconfigure((0, 1), weight=1, uniform='actions')
    AnimatedButton(actions, tk, 'Abrir Riot / LoL', lambda: start('run')).grid(row=0, column=0, sticky='ew', padx=(0, 5))
    AnimatedButton(actions, tk, 'Diagnosticar', lambda: start('doctor')).grid(row=0, column=1, sticky='ew', padx=(5, 0))

    links = tk.Frame(page, bg=COLORS['bg'])
    links.pack(fill='x', pady=(6, 0))

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

    link_font = ('Sans', 9, 'underline')
    preview = tk.Label(links, text='Prévia', bg=COLORS['bg'], fg=COLORS['cyan'], font=link_font, cursor='hand2')
    preview.pack(side='left')
    preview.bind('<Button-1>', lambda _event: start('install', True))
    guide = tk.Label(links, text='Guia', bg=COLORS['bg'], fg=COLORS['cyan'], font=link_font, cursor='hand2')
    guide.pack(side='left', padx=(14, 0))
    guide.bind('<Button-1>', lambda _event: open_guide())

    status_panel = RoundedPanel(page, tk, COLORS['panel_alt'], COLORS['bg'], padding=9, radius=12)
    status_panel.pack(fill='x', pady=(9, 6))
    indicator = tk.Canvas(status_panel.inner, width=12, height=12, bg=COLORS['panel_alt'], highlightthickness=0)
    dot = indicator.create_oval(2, 2, 10, 10, fill=COLORS['green'], outline='')
    indicator.pack(side='left', padx=(0, 8))
    tk.Label(status_panel.inner, textvariable=state, bg=COLORS['panel_alt'], fg=COLORS['text'], font=('Sans', 9), wraplength=620, justify='left').pack(side='left', fill='x', expand=True)
    tk.Label(page, text='Experimental · sem vínculo com a Riot. Clientes não oficiais podem levar a restrições de conta.', bg=COLORS['bg'], fg=COLORS['muted'], font=('Sans', 8), wraplength=660, justify='left').pack(anchor='w')

    def pulse(bright=True):
        indicator.itemconfigure(dot, fill=COLORS['cyan'] if bright else COLORS['green'])
        indicator.after(850, lambda: pulse(not bright))

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

    pulse()
    monitor_terminals()
    root.mainloop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
