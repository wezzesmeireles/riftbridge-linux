#!/bin/sh
set -eu
repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if ! command -v python3 >/dev/null 2>&1; then
  for arg in "$@"; do
    case "$arg" in --dry-run|--help|-h) echo 'Python 3.10+ necessário. Nenhum pacote foi instalado.'; exit 1;; esac
  done
  echo 'Preparando Python 3 pelo gerenciador da distro. Confirme os pacotes quando solicitado.'
  if command -v dnf >/dev/null 2>&1; then sudo dnf install python3
  elif command -v apt-get >/dev/null 2>&1; then sudo apt-get update; sudo apt-get install python3
  elif command -v pacman >/dev/null 2>&1; then sudo pacman -Syu --needed python
  elif command -v zypper >/dev/null 2>&1; then sudo zypper install python3
  else echo 'Instale Python 3.10+ pelo gerenciador da distro e execute novamente.' >&2; exit 1
  fi
fi
exec python3 "$repo/scripts/easy.py" install "$@"
