#!/usr/bin/env python3

"""
netbom_pf_tool.py

This script reads a NetBOM JSON file and generates corresponding PF (Packet Filter) rules.
It uploads the rules to an OPNsense firewall and applies them using pfctl over SSH.

Usage:
    python3 netbom_pf_tool.py <netbom.json> <opnsense_ip> <opnsense_username>
"""

import json
import sys
import os
from datetime import datetime

def load_netbom(file_path):
    """Load and parse a NetBOM JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_rule_name(mac_addr):
    """Generate a rule label using MAC address and current date."""
    today = datetime.today().strftime("%d%m%Y")
    mac_clean = mac_addr.replace(":", "").lower()
    return f"netbom-{mac_clean}-{today}"

def generate_pf_rules(netbom, iface="em1"):
    """
    Generate PF firewall rules from NetBOM data.

    Parameters:
        netbom: Parsed NetBOM JSON object.
        iface: Network interface name to apply rules on (default: em1).

    Returns:
        String with PF rules.
    """
    mac = netbom["device"]["mac"]
    ip = netbom["device"]["ip"]
    name = generate_rule_name(mac)

    lines = [f"# PF RULES FOR {name}"]

    # Allow only specified endpoints
    for rule in netbom["connectivity"]["allowed_endpoints"]:
        proto = rule["protocol"].lower()
        dest_ip = rule["ip"]
        port = rule["port"]
        lines.append(
            f"pass out quick on {iface} inet proto {proto} from {ip} to {dest_ip} port = {port} label \"{name}\""
        )

    # Add default deny rule if specified
    if netbom["firewall_policy"].get("default_deny", True):
        lines.append(f"# Default deny for all other outbound traffic from {ip}")
        lines.append(
            f"block out quick on {iface} inet from {ip} label \"{name}-default-deny\""
        )

    return "\n".join(lines)

def main():
    """Main function to generate and apply PF rules to an OPNsense firewall."""
    if len(sys.argv) != 4:
        print("Usage: python3 netbom_pf_tool.py <netbom.json> <opnsense_ip> <opnsense_username>")
        sys.exit(1)

    netbom_file = sys.argv[1]
    firewall_ip = sys.argv[2]
    ssh_user = sys.argv[3]

    # Load NetBOM JSON and generate rules
    netbom = load_netbom(netbom_file)
    pf_rules = generate_pf_rules(netbom)

    local_file = "/tmp/netbom_pf.rules"
    remote_file = "/tmp/netbom_pf.rules"

    # Write rules to local temp file
    with open(local_file, "w") as f:
        f.write(pf_rules + "\n")

    print("✅ Generated PF rules:\n")
    print(pf_rules)
    print("\n🔐 Uploading to OPNsense...")

    # Upload rules file to OPNsense
    os.system(f"scp {local_file} {ssh_user}@{firewall_ip}:{remote_file}")

    print("🚀 Applying rules using pfctl...")
    os.system(f"ssh {ssh_user}@{firewall_ip} 'pfctl -a netbom -f {remote_file}'")
    print("✅ Done.")

if __name__ == "__main__":
    main()
