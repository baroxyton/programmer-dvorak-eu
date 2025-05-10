#!/usr/bin/env python3
"""
Automates installation and uninstallation of the "Dvorak for Programmers with European Keys" keyboard layout on Ubuntu.

Features:
- install: appends layout to /usr/share/X11/xkb/symbols/us and updates evdev.xml
           wrapped in markers so only inserted once and easily removed.
- uninstall: removes injected sections and restores backups.
- backups: creates timestamped backups before install/uninstall.
- list-backups: show available backups.
- show-backup: display path to a specific backup.
"""

# Vibe coded btw

import os
import sys
import shutil
import argparse
import datetime

# Paths
SYMBOLS_FILE = '/usr/share/X11/xkb/symbols/us'
RULES_FILE = '/usr/share/X11/xkb/rules/evdev.xml'
BACKUP_DIR = '/var/backups/dpe_keyboard'
LAYOUT_FILE = os.path.join(os.path.dirname(__file__), 'us-dpe')

# Markers
SYMBOLS_START = '# DPE-START'
SYMBOLS_END = '# DPE-END'
VARIANT_START = '<!--DPE-START-->'
VARIANT_END = '<!--DPE-END-->'


def backup(file_path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    fname = f"{os.path.basename(file_path)}.{ts}.bak"
    dest = os.path.join(BACKUP_DIR, fname)
    shutil.copy2(file_path, dest)
    print(f"Backup of {file_path} -> {dest}")
    return dest


def install_symbols():
    # read symbols file and ensure not already installed
    with open(SYMBOLS_FILE) as f:
        text = f.read()
    if SYMBOLS_START in text:
        print("Symbols file already contains DPE layout; skipping.")
        return
    backup(SYMBOLS_FILE)
    content = open(LAYOUT_FILE).read()
    to_add = f"\n{SYMBOLS_START}\n{content}\n{SYMBOLS_END}\n"
    with open(SYMBOLS_FILE, 'a') as f:
        f.write(to_add)
    print("Added layout to symbols file.")


def uninstall_symbols():
    with open(SYMBOLS_FILE) as f:
        text = f.read()
    if SYMBOLS_START not in text:
        print("No symbols markers found; nothing to remove.")
        return
    backup(SYMBOLS_FILE)
    before, rest = text.split(SYMBOLS_START, 1)
    _, after = rest.split(SYMBOLS_END, 1)
    with open(SYMBOLS_FILE, 'w') as f:
        f.write(before + after)
    print("Removed layout from symbols file.")


def install_variant():
    with open(RULES_FILE) as f:
        text = f.read()
    if VARIANT_START in text:
        print("Variant already installed; skipping.")
        return
    backup(RULES_FILE)
    # insert into variantList of us
    insert = f"{VARIANT_START}<variant>\n  <configItem>\n    <name>dpe</name>\n    <description>English (Programmer Dvorak Eur. Keys)</description>\n  </configItem>\n</variant>{VARIANT_END}"
    # find </variantList> after us layout
    marker = '<layout>'
    idx = text.find('<name>us</name>')
    if idx == -1:
        print("Could not find us layout in rules file.")
        sys.exit(1)
    # find next </variantList> after idx
    vl_end = text.find('</variantList>', idx)
    if vl_end == -1:
        print("Could not find variantList end.")
        sys.exit(1)
    # insert before </variantList>
    new_text = text[:vl_end] + insert + text[vl_end:]
    with open(RULES_FILE, 'w') as f:
        f.write(new_text)
    print("Added variant to rules file.")


def uninstall_variant():
    with open(RULES_FILE) as f:
        text = f.read()
    if VARIANT_START not in text:
        print("No variant markers found in rules file.")
        return
    backup(RULES_FILE)
    # remove block between markers
    before, rest = text.split(VARIANT_START, 1)
    _, after = rest.split(VARIANT_END, 1)
    with open(RULES_FILE, 'w') as f:
        f.write(before + after)
    print("Removed variant from rules file.")


def list_backups():
    for fn in sorted(os.listdir(BACKUP_DIR)):
        print(fn)


def show_backup(name):
    path = os.path.join(BACKUP_DIR, name)
    if os.path.exists(path):
        print(path)
    else:
        print(f"Backup {name} not found.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=['install', 'uninstall', 'list-backups', 'show-backup'])
    p.add_argument('--backup', help='show specific backup file name for show-backup')
    args = p.parse_args()

    if args.action == 'install':
        install_symbols()
        install_variant()
    elif args.action == 'uninstall':
        uninstall_symbols()
        uninstall_variant()
    elif args.action == 'list-backups':
        list_backups()
    elif args.action == 'show-backup':
        if not args.backup:
            print("Please provide --backup filename to show.")
        else:
            show_backup(args.backup)

if __name__ == '__main__':
    main()

