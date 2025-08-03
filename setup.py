#!/usr/bin/env python3

import os
import subprocess
import sys
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
def show_menu():
    print("""
========= MENU =========
1. Install nginx
2. Install ufw
3. Install fail2ban
4. Install all
5. Remove all packages
6. Exit
""")

# Main program logic
def main():
    check_root()
    update_system()

    while True:
        show_menu()
        choice = input("Enter your option number: ").strip()

        if choice == "1":
            install_package("nginx")
        elif choice == "2":
            install_package("ufw")
        elif choice == "3":
            install_package("fail2ban")
        elif choice == "4":
            for pkg in ["nginx", "ufw", "fail2ban"]:
                install_package(pkg)
        elif choice == "5":
            for pkg in ["nginx", "ufw", "fail2ban"]:
                remove_package(pkg)
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()