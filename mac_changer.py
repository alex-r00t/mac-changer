#!/usr/bin/env python3
# ==============================================================
#  MAC CHANGER TOOL
#  Author : alex-r00t
#  GitHub : https://github.com/alex-r00t
#  Description: Change your MAC address manually or randomly
# ==============================================================

import subprocess
import random
import re
import os
import pyfiglet   # pip install pyfiglet

# Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def banner():
    ascii_banner = pyfiglet.figlet_format("MAC CHANGER", font="slant")
    print(f"{CYAN}{ascii_banner}{RESET}")
    print(f"{YELLOW}Author:{RESET} alex-r00t   {YELLOW}|   GitHub:{RESET} github.com/alex-r00t\n")


def generate_random_mac():
    first_octet = random.randint(0x00, 0xff)
    first_octet = (first_octet & 0b11111110) | 0b00000010
    mac = [first_octet] + [random.randint(0x00, 0xff) for _ in range(5)]
    return ":".join("%02x" % x for x in mac)


def get_interfaces():
    result = subprocess.check_output(["ip", "-o", "link", "show"]).decode("utf-8")
    interfaces = [line.split(":")[1].strip() for line in result.split("\n") if line]
    return [i for i in interfaces if i != "lo"]


def change_mac(interface, new_mac):
    try:
        subprocess.check_call(["sudo", "ip", "link", "set", "dev", interface, "down"])
        subprocess.check_call(["sudo", "ip", "link", "set", "dev", interface, "address", new_mac])
        subprocess.check_call(["sudo", "ip", "link", "set", "dev", interface, "up"])
    except subprocess.CalledProcessError:
        print(f"{RED}[-] Failed to change MAC on {interface}{RESET}")
        subprocess.call(["sudo", "ip", "link", "set", "dev", interface, "up"])


def get_current_mac(interface):
    result = subprocess.check_output(["ip", "link", "show", interface]).decode("utf-8")
    mac_address_search = re.search(r"link/ether (\w\w:\w\w:\w\w:\w\w:\w\w:\w\w)", result)
    return mac_address_search.group(1) if mac_address_search else None


def is_valid_mac(mac):
    if not re.match(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$", mac):
        return False, "Invalid format! Example: 00:11:22:33:44:55"
    first_octet = int(mac.split(":")[0], 16)
    if first_octet & 1:
        return False, "Invalid MAC! First octet must be unicast (even number)."
    return True, ""


def manual_mode():
    interfaces = get_interfaces()
    print(f"\n{GREEN}[+] Available interfaces: {RESET}{', '.join(interfaces)}")

    while True:
        interface = input(f"{CYAN}>>> Choose interface: {RESET}").strip()
        if interface not in interfaces:
            print(f"{RED}[-] Invalid interface, try again.{RESET}")
            continue
        break

    old_mac = get_current_mac(interface)

    while True:
        new_mac = input(f"{CYAN}>>> Enter new MAC address: {RESET}").strip()
        valid, error = is_valid_mac(new_mac)
        if not valid:
            print(f"{RED}[-] {error}{RESET}")
            continue
        break

    change_mac(interface, new_mac)
    current_mac = get_current_mac(interface)
    if current_mac and current_mac.lower() == new_mac.lower():
        print(f"\n{GREEN}[✓] Success!{RESET}")
        print(f"    {YELLOW}{interface}{RESET}:  {CYAN}{old_mac}{RESET}  →  {GREEN}{current_mac}{RESET}")
    else:
        print(f"{RED}[-] MAC change failed!{RESET}")


def random_mode():
    interfaces = get_interfaces()
    print(f"\n{GREEN}[+] Available interfaces: {RESET}{', '.join(interfaces)}")

    while True:
        interface = input(f"{CYAN}>>> Choose interface: {RESET}").strip()
        if interface not in interfaces:
            print(f"{RED}[-] Invalid interface, try again.{RESET}")
            continue
        break

    old_mac = get_current_mac(interface)
    new_mac = generate_random_mac()

    change_mac(interface, new_mac)
    current_mac = get_current_mac(interface)
    if current_mac and current_mac.lower() == new_mac.lower():
        print(f"\n{GREEN}[✓] Success!{RESET}")
        print(f"    {YELLOW}{interface}{RESET}:  {CYAN}{old_mac}{RESET}  →  {GREEN}{current_mac}{RESET}")
    else:
        print(f"{RED}[-] MAC change failed!{RESET}")


def help_menu():
    clear_screen()
    banner()
    print(f"""{GREEN}{BOLD}
Help - MAC CHANGER
-------------------------------------------
[0] Manual Mode:
    - Choose the interface and enter your own MAC.
    - Format: 00:11:22:33:44:55
    - First octet must be unicast (even number).

[1] Random Mode:
    - Tool generates a valid random MAC.
    - You only choose the interface.

[q] Quit:
    - Exit the program.

Examples:
-------------------------------------------
 Correct: 02:1a:2b:3c:4d:5e
 Wrong:   11:aa:11:aa:11:aa (multicast)

Notes:
-------------------------------------------
 * Loopback (lo) cannot be changed.
 * NetworkManager may reset the MAC.
{RESET}""")
    input(f"\n{YELLOW}Press Enter to return to menu...{RESET}")


def main_menu():
    clear_screen()
    banner()
    print(f"{YELLOW}[0]{RESET} Manual MAC address")
    print(f"{YELLOW}[1]{RESET} Random MAC address")
    print(f"{YELLOW}[h]{RESET} Help")
    print(f"{YELLOW}[q]{RESET} Quit\n")
    choice = input(f"{CYAN}>>> Select option: {RESET}").strip()
    return choice


if __name__ == "__main__":
    while True:
        choice = main_menu()
        if choice == "0":
            manual_mode()
            input(f"\n{YELLOW}Press Enter to continue...{RESET}")
        elif choice == "1":
            random_mode()
            input(f"\n{YELLOW}Press Enter to continue...{RESET}")
        elif choice.lower() == "h":
            help_menu()
        elif choice.lower() == "q":
            print(f"{GREEN}[+] Exiting tool.{RESET}")
            break
        else:
            print(f"{RED}[-] Invalid option!{RESET}")
            input(f"\n{YELLOW}Press Enter to continue...{RESET}")
