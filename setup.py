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

def installed(package_name):
    try:
        dpkg_check = subprocess.run(
            ["dpkg", "-s", package_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return dpkg_check.returncode == 0
    except Exception:
        return False

def install_package(name):
    try:
        logging.info(f"Attempting to install {name}...")
        print(f"Installing {name}...")
        subprocess.run(["apt", "install", "-y", name], check=True)
        logging.info(f"{name} installed successfully.")
        print(f"{name} installed successfully.\n")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error occurred while installing {name}: {e}")
        print(f"Error occurred while installing {name}.\n")

def remove_package(name):
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

def all_installed(package_names):
    return all(installed(pkg) for pkg in package_names)

def menu_options():
    options = [
        ("Web Server (nginx, ufw, fail2ban, certbot)", ["nginx", "ufw", "fail2ban", "certbot"]),
        ("SSH Minimal (ufw, ssh, denyroot)", ["ufw", "ssh", "denyroot"]),
        ("Game Server (steamcmd, wine, screen)", ["steamcmd", "wine", "screen"]),
        ("Dev Environment (git, docker, zsh, neovim)", ["git", "docker.io", "zsh", "neovim"]),
        ("Install Nginx", ["nginx"]),
        ("Install UFW (Uncomplicated Firewall)", ["ufw"]),
        ("Install Fail2Ban", ["fail2ban"]),
        ("Install Certbot (for SSL)", ["certbot"]),
        ("Install Docker", ["docker.io"]),
        ("Install Git", ["git"]),
        ("Remove All Packages", []),
        ("Exit", [])
    ]

    max_len = max(len(label) for label, _ in options)
    updated_menu = []
    for label, packages in options:
        if packages:
            status = "[Installed]" if all_installed(packages) else ""
        else:
            status = ""
        padded_label = label.ljust(max_len + 2)
        updated_menu.append((f"{padded_label} {status}", packages))
    return updated_menu

def tui_menu(stdscr):
    curses.curs_set(0)
    current_row = 0
    selected = [False] * len(menu_options())

    while True:
        menu = menu_options()
        stdscr.clear()
        stdscr.addstr(0, 0, "Use ↑ ↓ to navigate. [Space] to select. [Enter] to confirm.\n\n")

        for i, (option, _) in enumerate(menu):
            mark = "[*]" if selected[i] else "[ ]"
            if i == current_row:
                stdscr.addstr(f">{mark} {option}\n", curses.A_REVERSE)
            else:
                stdscr.addstr(f" {mark} {option}\n")

        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu) - 1:
            current_row += 1
        elif key == ord(" "):
            selected[current_row] = not selected[current_row]
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return selected

def main():
    check_root()
    update_system()

    while True:
        selected = curses.wrapper(tui_menu)
        menu = menu_options()

        for i, (_, packages) in enumerate(menu):
            if selected[i]:
                if not packages and "Remove All" in menu[i][0]:
                    for pkg in [
                        "nginx", "ufw", "fail2ban", "certbot", "docker.io", 
                        "git", "steamcmd", "wine", "screen", "zsh", "neovim", 
                        "ssh", "denyroot"
                    ]:
                        remove_package(pkg)
                elif not packages and "Exit" in menu[i][0]:
                    print("Exiting...")
                    return
                else:
                    for pkg in packages:
                        install_package(pkg)

if __name__ == "__main__":
    main()
