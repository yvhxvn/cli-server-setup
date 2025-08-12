#!/usr/bin/env python3

import os
import subprocess
import sys
import curses
import logging

logging.basicConfig(
    filename='server-setup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_root():
    if os.geteuid() != 0:
        print("This script must be run as root (use sudo).")
        sys.exit(1)

def update_system():
    print("Updating system...")
    subprocess.run(["apt", "update"], check=True)
    subprocess.run(["apt", "upgrade", "-y"], check=True)
    print("System update completed.\n")

def installed_pkg(package_name):
    try:
        dpkg_check = subprocess.run(
            ["dpkg", "-s", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return dpkg_check.returncode == 0
    except Exception:
        return False

def install_pkg(name):
    try:
        logging.info(f"Attempting to install {name}...")
        print(f"Installing {name}...")
        subprocess.run(["apt", "install", "-y", name], check=True)
        logging.info(f"{name} installed successfully.")
        print(f"{name} installed successfully.\n")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while installing {name}: {e}")
        print(f"Error occurred while installing {name}.\n")

def remove_pkg(name):
    try:
        logging.info(f"Attempting to remove {name}...")
        print(f"Removing {name}...")
        subprocess.run(["apt", "remove", "-y", name], check=True)
        subprocess.run(["apt", "autoremove", "-y"], check=True)
        logging.info(f"{name} removed successfully.")
        print(f"{name} removed successfully.\n")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while removing {name}: {e}")
        print(f"Error occurred while removing {name}.\n")

MENU_OPTIONS = [
    "1.  Web Server (nginx, ufw, fail2ban, certbot)",
    "2.  SSH Minimal (ufw, ssh, sshguard)",
    "3.  LAMP Stack (nginx, mariadb, php)",
    "4.  Containers and virtualization (docker, podman, lxc, vagrant)",
    "5.  Dev Environment (git, docker, zsh, neovim)",
    "6.  Game Server (steamcmd, wine, screen)",
    "7.  Install Docker",
    "8.  Install Nginx",
    "9.  Install UFW (Uncomplicated Firewall)",
    "10. Install Fail2Ban",
    "11. Install All Packages",
    "12. Remove All Packages",
    "13. Exit"
]

def tui_menu(stdscr):
    curses.curs_set(0)
    current_row = 0
    stdscr_row = 0
    stdscr.addstr(stdscr_row, 0, "Server Setup Menu", curses.A_BOLD)
    selected = [False] * len(MENU_OPTIONS)

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Use ↑ ↓ to navigate. [Space] to select. [Enter] to confirm.\n\n")

        for i, option in enumerate(MENU_OPTIONS):
            mark = "[*]" if selected[i] else "[ ]"
            if i == current_row:
                stdscr.addstr(f">{mark} {option}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f" {mark} {option}\n")

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(MENU_OPTIONS) - 1:
            current_row += 1
        elif key == ord(" "):
            selected[current_row] = not selected[current_row]
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return selected

def main():
    check_root()
    update_system()

    selected = curses.wrapper(tui_menu)

    if selected[0]:
        for pkg in ["nginx", "ufw", "fail2ban", "certbot"]:
            install_pkg(pkg)
    if selected[1]:
        for pkg in ["ufw", "ssh", "sshguard"]:
            install_pkg(pkg)
    if selected[2]:
        for pkg in ["nginx", "mariadb-server", "php-fpm"]:
            install_pkg(pkg)
    if selected[3]:
        for pkg in ["docker.io", "podman", "lxc", "vagrant"]:
            install_pkg(pkg)
    if selected[4]:
        for pkg in ["git", "docker.io", "zsh", "neovim"]:
            install_pkg(pkg)
    if selected[5]:
        for pkg in ["steamcmd", "wine", "screen"]:
            install_pkg(pkg)
    if selected[6]:
        install_pkg("docker.io")
    if selected[7]:
        install_pkg("nginx")
    if selected[8]:
        install_pkg("ufw")
    if selected[9]:
        install_pkg("fail2ban")
    if selected[10]:    
        for pkg in ["nginx", "ufw", "fail2ban", "certbot", "ssh", "sshguard", "mariadb-server", "php-fpm", "docker.io", "podman", "lxc", "vagrant", "git", "zsh", "neovim", "steamcmd", "wine", "screen"]:
            install_pkg(pkg)
    if selected[11]:
        for pkg in ["nginx", "ufw", "fail2ban", "certbot", "ssh", "sshguard", "mariadb-server", "php-fpm", "docker.io", "podman", "lxc", "vagrant", "git", "zsh", "neovim", "steamcmd", "wine", "screen"]:
            remove_pkg(pkg)

    print("Exiting...")

if __name__ == "__main__":
    main()
    