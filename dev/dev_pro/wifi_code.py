#!/usr/bin/env python3
"""
RPI OS - Debian bookwoorm 64 bit

Raspberry Pi WiFi Network Changer using NetworkManager
This script uses nmcli to connect to a new WiFi network
"""
import platform
import subprocess
import time
import os

# WiFi network details
WIFI_SSID = ""
WIFI_PASSWORD = ""


def check_nmcli_installed():
    """Check if NetworkManager is installed"""
    try:
        subprocess.run(["nmcli", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def connect_to_wifi(ssid, password):
    """Connect to WiFi using nmcli"""
    print(f"Attempting to connect to {ssid}...")
    # if platform.system() != "Linux":
    #     print(f"[DEV MODE] Would connect to SSID: {ssid} with password: {password}")
    #     return True  # Simulate success on Windows/dev environments

    # Check if the connection already exists
    result = subprocess.run(
        ["nmcli", "connection", "show", ssid],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode == 0:
        # Connection exists, delete it to refresh settings
        print(f"Removing existing connection profile for {ssid}")
        subprocess.run(["nmcli", "connection", "delete", ssid], check=True)

    # Create a new connection
    print(f"Creating new connection for {ssid}")
    result = subprocess.run(
        ["nmcli", "device", "wifi", "connect", ssid, "password", password],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print(f"Failed to connect: {result.stderr}")
        return False

    print("Connection command successful")
    return True


def verify_connection(ssid, max_attempts=5, delay=2):
    """Verify that we're connected to the specified network"""
    print("Verifying connection...")

    for attempt in range(max_attempts):
        print(f"Check {attempt + 1}/{max_attempts}...")

        # Get current connection info
        result = subprocess.run(
            ["nmcli", "-t", "-f", "active,ssid", "device", "wifi"],
            stdout=subprocess.PIPE,
            text=True,
            check=False
        )

        for line in result.stdout.splitlines():
            if "yes:" + ssid in line:
                print(f"Successfully connected to {ssid}")
                return True

        print(f"Not connected to {ssid} yet. Waiting...")
        time.sleep(delay)

    print(f"Failed to confirm connection to {ssid}")
    return False


def main():
    """Main function"""
    # Check if script is run as root
    if os.geteuid() != 0:
        print("This script should be run with sudo privileges")
        return False

    # Check if NetworkManager is installed
    if not check_nmcli_installed():
        print("ERROR: NetworkManager (nmcli) is not installed.")
        print("Install it with: sudo apt-get install network-manager")
        print("Or use the wpa_supplicant method instead.")
        return False

    # Connect to WiFi
    if connect_to_wifi(WIFI_SSID, WIFI_PASSWORD):
        print(" in connect_to_wifi")
        # Verify connection
        # if platform.system() != "Linux":
        #     print(f"[DEV MODE] Would connect to SSID: {WIFI_SSID} with password: {WIFI_PASSWORD}")
        #     return True  # Simulate success

        verify_connection(WIFI_SSID)


if __name__ == "__main__":
    main()
