# NetBOM Firewall PoC

**Proof of Concept**  
Generate and apply firewall rules from a NetBOM JSON file on an OPNsense firewall.

## Overview

This PoC demonstrates how a device-specific [NetBOM](https://netbom.net) file — a machine-readable "bill of network materials" — can be used to automatically generate firewall rules that enforce **least-privilege communication** at the gateway.

It includes:
- A sample NetBOM file for an Ecobee thermostat
- A Python script that converts the NetBOM to PF firewall rules
- Logic to upload and apply those rules on an OPNsense firewall

## Files

| File | Description |
|------|-------------|
| `netbom_pf_tool_commented.py` | Python script to generate and push PF rules from a NetBOM file |
| `ecobee_netbom.json` | Sample NetBOM JSON for a smart thermostat |

## Requirements

- Python 3
- SSH access to an OPNsense firewall (with root or privileged user)
- `scp` and `ssh` available from the command line

## Usage

```bash
python3 netbom_pf_tool_commented.py <netbom_file.json> <opnsense_ip> <ssh_username>

## Example

```bash
python3 netbom_pf_tool_commented.py ecobee_netbom.json 192.168.120.1 root

Learn more about the NetBOM initiative: [netbom.net](https://netbom.net)
