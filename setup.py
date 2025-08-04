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

# Check if the script is run as root
def check_root():
    if os.geteuid() != 0:
        print("This script must be run as root (use sudo).")
        sys.exit(1)

# Update the system
def update_system():
    """Update the system packages."""
    print("Updating system...")
    subprocess.run(["apt", "update"], check=True)
    subprocess.run(["apt", "upgrade", "-y"], check=True)
    print("System update completed.\n")

# Check if a package is installed
def is_installed(package_name):
    result = subprocess.run(['which', package_name], stdout=subprocess.PIPE)
    return result.returncode == 0

# Install a package
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

# Remove a package
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

# Display the menu
MENU_OPTIONS = [
    "1. Install Nginx",
    "2. Install UFW (Uncomplicated Firewall)",
    "3. Install Fail2Ban",
    "4. Install All Packages",
    "5. Remove All Packages",
    "6. Exit"
]

def tui_menu(stdscr):
    """Display a simple text-based menu using curses."""
    curses.curs_set(0)  # Hide the cursor
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

# Main program logic
def main():
    check_root()
    update_system()

    selected = curses.wrapper(tui_menu)

    if selected[0]:  # Install Nginx
        install_package("nginx")
    if selected[1]:  # Install UFW
        install_package("ufw")
    if selected[2]:  # Install Fail2Ban
        install_package("fail2ban")
    if selected[3]:  # Install All Packages
        for pkg in ["nginx", "ufw", "fail2ban"]:
            install_package(pkg)
    if selected[4]:  # Remove All Packages
        for pkg in ["nginx", "ufw", "fail2ban"]:
            remove_package(pkg)

    print("Exiting...")

if __name__ == "__main__":
    main()