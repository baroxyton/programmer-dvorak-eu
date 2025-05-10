#!/usr/bin/env python3

# Vibe coded btw

"""
Automates installation and uninstallation of the "Dvorak for Programmers with European Keys" keyboard layout on Ubuntu.

Features:
- install: appends layout to /usr/share/X11/xkb/symbols/us and updates evdev.xml
         with comments marking begin/end for easy uninstall.
- uninstall: removes appended sections and restores backups.
- backups: creates timestamped backups before install/uninstall.
- list-backups: shows available backup files.
- show-backup-location: prints backup directory.

Usage:
  sudo python3 install_dpe_keyboard.py install
  sudo python3 install_dpe_keyboard.py uninstall
  python3 install_dpe_keyboard.py list-backups
  python3 install_dpe_keyboard.py show-backup-location

Ensure `us-dpe` (layout definition) is in the same folder as this script.
"""
import os
import sys
import shutil
import argparse
import datetime
import xml.etree.ElementTree as ET

# File paths
SYMBOLS_FILE = '/usr/share/X11/xkb/symbols/us'
RULES_FILE = '/usr/share/X11/xkb/rules/evdev.xml'
BACKUP_DIR = '/var/backups/dpe_keyboard'
# Local layout file (must reside alongside this script)
LAYOUT_FILE = os.path.join(os.path.dirname(__file__), 'us-dpe')

BEGIN_COMMENT_SYM = '// DPE-BEGIN'
END_COMMENT_SYM = '// DPE-END'
BEGIN_COMMENT_XML = '<!-- DPE-BEGIN -->'
END_COMMENT_XML = '<!-- DPE-END -->'
VARIANT_NAME = 'dpe'


def ensure_root():
    if os.geteuid() != 0:
        sys.exit('This script must be run as root (use sudo).')


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def timestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


def backup_file(path):
    ensure_backup_dir()
    if os.path.exists(path):
        fname = os.path.basename(path)
        dest = os.path.join(BACKUP_DIR, f"{fname}.{timestamp()}.bak")
        shutil.copy2(path, dest)
        print(f"Backed up {path} to {dest}")
        return dest
    else:
        print(f"Warning: {path} does not exist to backup.")
        return None


def list_backups():
    ensure_backup_dir()
    files = sorted(os.listdir(BACKUP_DIR))
    for f in files:
        print(f)


def show_backup_location():
    print(BACKUP_DIR)


def install():
    ensure_root()
    # Backup originals
    backup_file(SYMBOLS_FILE)
    backup_file(RULES_FILE)

    # Append layout to symbols file
    with open(LAYOUT_FILE, 'r', encoding='utf-8') as src:
        layout_data = src.read()

    with open(SYMBOLS_FILE, 'a', encoding='utf-8') as sym:
        sym.write(f"\n{BEGIN_COMMENT_SYM}\n")
        sym.write(layout_data)
        sym.write(f"\n{END_COMMENT_SYM}\n")
    print(f"Appended layout to {SYMBOLS_FILE}")

    # Modify evdev.xml
    tree = ET.parse(RULES_FILE)
    root = tree.getroot()
    # Find <layout name="us"> element
    for layout in root.findall('layout'):
        name = layout.find('configItem/name')
        if name is not None and name.text == 'us':
            variantList = layout.find('variantList')
            # Insert comments and variant
            comment1 = ET.Comment(' DPE-BEGIN ')
            comment2 = ET.Comment(' DPE-END ')
            variant = ET.Element('variant')
            ci = ET.SubElement(variant, 'configItem')
            nm = ET.SubElement(ci, 'name'); nm.text = VARIANT_NAME
            desc = ET.SubElement(ci, 'description'); desc.text = 'English (Programmer Dvorak Eur. Keys)'
            variantList.insert(0, comment1)
            variantList.insert(1, variant)
            variantList.insert(2, comment2)
            break
    tree.write(RULES_FILE, encoding='utf-8', xml_declaration=True)
    print(f"Updated {RULES_FILE} with variant '{VARIANT_NAME}'")


def uninstall():
    ensure_root()
    # Backup originals
    backup_file(SYMBOLS_FILE)
    backup_file(RULES_FILE)

    # Remove appended layout in symbols file
    with open(SYMBOLS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    out = []
    skip = False
    for line in lines:
        if BEGIN_COMMENT_SYM in line:
            skip = True
            continue
        if END_COMMENT_SYM in line:
            skip = False
            continue
        if not skip:
            out.append(line)
    with open(SYMBOLS_FILE, 'w', encoding='utf-8') as f:
        f.writelines(out)
    print(f"Removed layout block from {SYMBOLS_FILE}")

    # Remove variant from evdev.xml
    tree = ET.parse(RULES_FILE)
    root = tree.getroot()
    for layout in root.findall('layout'):
        name = layout.find('configItem/name')
        if name is not None and name.text == 'us':
            variantList = layout.find('variantList')
            to_remove = []
            for elem in list(variantList):
                # remove comment blocks and variant
                if isinstance(elem, ET.Comment) and 'DPE-BEGIN' in elem.text:
                    # remove until DPE-END
                    idx = list(variantList).index(elem)
                    # find matching end comment
                    for j, e2 in enumerate(list(variantList)[idx+1:], start=idx+1):
                        if isinstance(e2, ET.Comment) and 'DPE-END' in e2.text:
                            # remove slice
                            for rem in list(variantList)[idx:j+1]:
                                variantList.remove(rem)
                            break
                    break
            break
    tree.write(RULES_FILE, encoding='utf-8', xml_declaration=True)
    print(f"Removed variant '{VARIANT_NAME}' from {RULES_FILE}")


def main():
    parser = argparse.ArgumentParser(description='Install/uninstall DPE keyboard layout')
    parser.add_argument('action', choices=['install', 'uninstall', 'list-backups', 'show-backup-location'],
                        help='Action to perform')
    args = parser.parse_args()

    if args.action == 'install':
        install()
    elif args.action == 'uninstall':
        uninstall()
    elif args.action == 'list-backups':
        list_backups()
    elif args.action == 'show-backup-location':
        show_backup_location()

if __name__ == '__main__':
    main()
```
