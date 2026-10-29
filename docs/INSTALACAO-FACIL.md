# Instalação fácil — Linux x86_64

## O que foi validado

Em 29/10/2026, uma instalação existente em Fedora 44 KDE, Radeon RX 6600,
Darling compilado por fonte, abriu o Riot 141.0.7.5129 até a tela de login.
A confirmação foi visual pelo usuário. Houve um aviso sobre software de terceiros.
Não foi validada nesta sessão a instalação limpa, o backend Nix, outras distros
ou uma partida. Os scripts novos tiveram testes offline e de prévia; isso não
substitui um teste completo de instalação.

## Requisitos

- Linux x86_64, kernel 5.14+, Vulkan 1.3+ com timeline semaphores e driver funcional.
- Sessão X11 ou Wayland com Xwayland; executar no desktop local.
- Python 3.10+, Git; ao menos 50 GB livres, possivelmente mais durante o build.
- Rede estável. O tempo de compilação depende do processador e da RAM.
- Conta secundária se decidir assumir os riscos. Não é uma solução oficial da Riot.

## Comece com um comando

Depois de baixar e extrair o repositório, execute `./install.sh` em um terminal.
O script prepara Python se necessário, escolhe o ambiente e apresenta as etapas.
Você só confirma a instalação de pacotes e os prompts do runtime. O padrão é Brasil.

- Nix já instalado: usa o ambiente Nix.
- Sem Nix: prepara dependências nativas em Fedora, Debian/Ubuntu/Mint ou Arch/derivadas.
- Distro desconhecida ou Fedora imutável: interrompe com orientação; não modifica o host por suposição.
- `./install.sh --dry-run`: mostra os comandos. Não instala pacotes quando Python já está disponível.

A lista de pacotes segue as dependências oficiais do Darling, ajustadas para build
x86_64. A disponibilidade dos pacotes do Fedora foi consultada nesta máquina;
Debian e Arch não tiveram instalação completa validada. O gerenciador sempre pode
interromper por pacote indisponível ou configuração de repositórios. Não há `-y`,
`--noconfirm`, desativação de SELinux ou execução de instaladores remotos.

## Caminho comum entre distros: Nix (opcional)

Fedora, Ubuntu, Debian, Mint, Arch, EndeavourOS, Manjaro e openSUSE podem usar
Nix sem trocar de distro. Isso descreve um caminho de dependências, não uma
certificação de funcionamento do jogo. Siga as condições da versão do Nix para
sua distro em [nixos.org/download](https://nixos.org/download/).
Não desative SELinux, AppArmor, TLS ou outras proteções para instalar.

Instale apenas o necessário para obter este repositório, se estiver faltando:

| Família | Comando inicial |
|---|---|
| Fedora | `sudo dnf install git python3` |
| Debian/Ubuntu/Mint | `sudo apt update` e `sudo apt install git python3` |
| Arch/EndeavourOS/Manjaro | `sudo pacman -Syu git python` |
| openSUSE | `sudo zypper install git python3` |
| NixOS | Configure Git/Python e flakes conforme sua configuração NixOS |
| Outras | Instale Git/Python pelo gerenciador da distro e confirme se Nix a suporta |

Esses comandos **não** instalam todas as dependências do build nativo. O backend
Nix é uma alternativa, não uma exigência para as famílias com preparação nativa. Alpine/musl, ARM e sistemas imutáveis não foram validados;
não tente resolver isso executando o instalador inteiro como root.

Depois de instalar Nix e abrir um novo terminal:

```bash
git clone https://github.com/wezzesmeireles/riftbridge-linux.git
cd riftbridge-linux
./install.sh --region br
```

O comando imprime o plano, escolhe o backend disponível e inicia o fluxo upstream e mantém os prompts visíveis.
No prompt de região, Enter aceita `br`. O download do LoL é feito pelo cliente
Riot; o repositório não distribui o jogo, contas ou tokens. Depois:

```bash
./play.sh --region br
```

## Build nativo sem Nix

Este modo prepara as dependências das famílias reconhecidas antes do build. Para
um ambiente já preparado, use `--skip-deps`. Consulte a [documentação de build do Darling](https://docs.darlinghq.org/build-instructions.html)
e os [detalhes do runtime](SETUP.md). Nomes de pacotes variam entre versões:
o script usa listas por família e não habilita repositórios extras. Se algum pacote
não estiver disponível, interrompe sem iniciar o build.

```bash
./install.sh --backend native --region br --jobs 2 --dry-run
./install.sh --backend native --region br --jobs 2
./play.sh --backend native --region br
```

Execute como usuário normal. Apenas `cmake --install` pede sudo. Feche o jogo,
os clientes e encerre o runtime antes de reinstalar. O wrapper recusa um runtime
vivo; não mata processos nem apaga seu prefixo. Não use `pkill -f darlingserver`.

## Diagnóstico e retomada

```bash
python3 scripts/easy.py doctor --backend native
python3 scripts/easy.py doctor --backend nix
./install.sh --help
```

Prévia funciona sem Nix instalado. Um erro interrompe a sequência: corrija a etapa
e execute novamente. O build upstream reaproveita artefatos; isso não significa que
todas as etapas são transações ou que se deve reinstalar sobre um cliente aberto.
Não publique logs brutos: podem conter tokens, identificadores de conta e máquina.

## Cliente 142 e recuperação

A [issue upstream #154](https://github.com/lucannez64/darling-lol/issues/154)
relata quebra após a atualização 142/Electron 43 em várias máquinas. Um desligamento
não é a única explicação para o cliente deixar de abrir. A mesma discussão contém
um procedimento comunitário para reconstruir o 141.0.7.5129 de pacotes da CDN Riot,
com o manifest `42E1358C87FB3ABC`, e desativar a autoatualização em `system.yaml`.

Esse procedimento abriu o login na máquina Fedora desta sessão. Ainda depende de
arquivos na CDN e da aceitação da versão anterior pelos servidores. O instalador
fácil **não faz downgrade automaticamente** nem garante que o cliente 142 funcione.
Se o cliente atual falhar, pare nessa etapa e consulte a issue; não reinstale em loop.
Preserve o `.app` atual e os metadados antes de qualquer substituição. O jogo e os
binários da Riot não devem ser adicionados ao fork.

As alterações experimentais locais feitas ao tentar portar Electron 43 não estão
neste fork: não foram validadas em uma instalação limpa e não têm
validação suficiente para distribuição como correção universal.

## Escopo dos atalhos

O projeto upstream oferece `sh scripts/create-desktop-entry.sh`. Os ícones
originais do Riot/LoL vêm da instalação do usuário, não deste repositório.
Fixar um atalho na barra depende do KDE/GNOME/outro desktop; isso não altera a
política da Riot e não remove avisos sobre software de terceiros.

## Interface gráfica

Execute `./riftbridge.sh`. A tela mostra a distro reconhecida, a escolha prevista pelo
modo automático e um resumo do Darling encontrado no PATH. Escolha a região e use
**Instalar RiftBridge** para iniciar o fluxo principal. **Abrir Riot / LoL**,
**Diagnosticar** e **Prévia dos comandos** ficam na mesma tela; Nix/native só aparecem
ao abrir as opções avançadas. Cada ação abre um terminal e o painel indica quando
ela terminou. Os prompts do sudo permanecem visíveis nesse terminal.

A tela de status descreve apenas o que foi detectado no sistema; não valida o driver,
a instalação do jogo ou a compatibilidade da conta. A interface não é um novo backend
e não remove as limitações descritas acima.

Sem Tkinter, o assistente abre no terminal e prepara as dependências. Para instalar
somente a interface: Fedora `sudo dnf install python3-tkinter`; Debian/Ubuntu
`sudo apt install python3-tk`; Arch `sudo pacman -S tk`; openSUSE
`sudo zypper install python3-tk`. Alternativa sem Tkinter: `./install.sh`.

## Manter um cliente funcional e restaurar um backup

O upstream agora inclui uma ferramenta com staging e validação de YAML. Prefira-a
a editar manualmente a configuração. Com o jogo e o runtime encerrados:

```bash
python3 tools/riot-client-pin.py --status
python3 tools/riot-client-pin.py --pin --dry-run
python3 tools/riot-client-pin.py --pin
python3 tools/riot-client-pin.py --backup "$HOME/riot-client-backups"
```

O backup guarda o cliente **atualmente instalado**; não baixa uma versão anterior.
`--restore` recebe o diretório de uma versão previamente salva por essa ferramenta.
Para usar a instalação de outra máquina, ainda é preciso respeitar o fluxo de
obtenção oficial da Riot. Não compartilhe contas, tokens nem o prefixo inteiro.
