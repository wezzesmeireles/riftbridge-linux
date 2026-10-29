"""Native x86_64 dependency plans; no sudo, network or mutation on import."""
import shlex
import subprocess
from pathlib import Path

def os_release(path='/etc/os-release'):
    values={}
    try:lines=Path(path).read_text().splitlines()
    except OSError:return values
    for line in lines:
        if '=' not in line or line.lstrip().startswith('#'):continue
        k,v=line.split('=',1)
        try:parts=shlex.split(v);values[k]=parts[0] if parts else ''
        except ValueError:continue
    return values

def family(info=None):
    info=os_release() if info is None else info
    ids=[info.get('ID',''),*info.get('ID_LIKE','').split()]
    # Do not assume immutable Fedora variants accept dnf host installs.
    if Path('/run/ostree-booted').exists():return None
    if any(i in ids for i in ('fedora',)):return 'fedora'
    if any(i in ids for i in ('ubuntu','debian','linuxmint')):return 'debian'
    if any(i in ids for i in ('arch','manjaro','endeavouros','cachyos')):return 'arch'
    return None

def rpm_installed(package):
    """Check one installed RPM without invoking a package transaction."""
    try:
        return subprocess.run(['rpm','-q',package],stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL,check=False).returncode == 0
    except OSError:
        return False

def fedora_ffmpeg_packages():
    # Fedora's codec-free development packages conflict with RPM Fusion's ffmpeg-libs.
    # Keep the host's existing provider and request its matching headers instead.
    if rpm_installed('ffmpeg-devel'):
        return []
    if rpm_installed('ffmpeg-libs'):
        return ['ffmpeg-devel']
    return ['libavcodec-free-devel','libavformat-free-devel','libswresample-free-devel']

def commands(kind):
    # Based on Darling build instructions, omitting i686 for TARGET_i386=OFF.
    if kind=='fedora':
        packages='make cmake clang clang-devel lld llvm llvm-devel bison flex xz fuse-devel systemd-devel elfutils-libelf-devel cairo-devel freetype-devel libjpeg-turbo-devel fontconfig-devel libglvnd-devel mesa-libGL-devel mesa-libEGL-devel mesa-libGLU-devel libtiff-devel libxml2-devel libbsd-devel git git-lfs libXcursor-devel libXrandr-devel libXext-devel libxcb-devel giflib-devel pulseaudio-libs-devel libxkbfile-devel openssl-devel libcap-devel libcurl-devel libedit-devel vulkan-headers vulkan-loader-devel vulkan-tools glx-utils xdpyinfo python3-pip python3-tkinter unzip curl pkgconf-pkg-config'.split()
        packages.extend(fedora_ffmpeg_packages())
        return [['sudo','dnf','install',*packages]]
    if kind=='debian':
        packages='build-essential cmake clang lld llvm-dev bison flex xz-utils libfuse-dev libudev-dev pkg-config libcap2-bin libcap-dev git git-lfs libglu1-mesa-dev libcairo2-dev libgl1-mesa-dev libtiff-dev libfreetype6-dev libxml2-dev libegl1-mesa-dev libfontconfig1-dev libbsd-dev libxrandr-dev libxcursor-dev libxext-dev libxcb-shm0-dev libx11-xcb-dev libgif-dev libpulse-dev libavformat-dev libavcodec-dev libswresample-dev libdbus-1-dev libxkbfile-dev libssl-dev libvulkan-dev libcurl4-openssl-dev libedit-dev vulkan-tools mesa-utils x11-utils python3-venv python3-pip python3-tk curl unzip'.split()
        return [['sudo','apt-get','update'],['sudo','apt-get','install',*packages]]
    if kind=='arch':
        packages='base-devel cmake clang lld llvm bison flex xz fuse systemd cairo freetype2 libjpeg-turbo fontconfig libglvnd mesa glu libtiff libxml2 libbsd git git-lfs libxcursor libxrandr libxext libxcb giflib libpulse libxkbfile openssl libcap ffmpeg curl libedit vulkan-headers vulkan-icd-loader vulkan-tools mesa-utils xorg-xdpyinfo python python-pip tk unzip pkgconf'.split()
        return [['sudo','pacman','-Syu','--needed',*packages]]
    return []
