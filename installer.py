#!/usr/bin/env python3

# Vibe coded btw
"""
Automates installation and uninstallation of the "Dvorak for Programmers with European Keys" keyboard layout on Ubuntu.

Features:
- install: appends layout to /usr/share/X11/xkb/symbols/us and updates evdev.xml
           wrapped in markers so only installed once and easily removed.
- uninstall: removes injected sections and restores backups.
- backups: creates timestamped backups before install/uninstall.
- list-backups: shows existing backups.
"""

import os
import sys
import shutil
import argparse
import datetime
import re
import xml.etree.ElementTree as ET

# Constants (edit if your paths differ)
SYMBOLS_FILE = '/usr/share/X11/xkb/symbols/us'
RULES_FILE   = '/usr/share/X11/xkb/rules/evdev.xml'
BACKUP_DIR   = '/var/backups/dpe_keyboard'
LAYOUT_FILE  = os.path.join(os.path.dirname(__file__), 'us-dpe')

# Markers
SYMBOLS_START = '# DPE-START'
SYMBOLS_END   = '# DPE-END'
XML_START     = 'DPE-START'
XML_END       = 'DPE-END'


def ensure_backup_dir():
    os.makedirs(BACKUP_DIR, exist_ok=True)


def timestamp():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')


def backup(path):
    ensure_backup_dir()
    fname = os.path.basename(path) + '.' + timestamp() + '.bak'
    dest = os.path.join(BACKUP_DIR, fname)
    shutil.copy2(path, dest)
    print(f'Backup of {path} → {dest}')
    return dest


def list_backups():
    ensure_backup_dir()
    for f in sorted(os.listdir(BACKUP_DIR)):
        print(f)


def install_symbols():
    data = open(SYMBOLS_FILE).read()
    if SYMBOLS_START in data:
        print('Symbols file already contains DPE section; skipping.')
        return
    backup(SYMBOLS_FILE)

    layout = open(LAYOUT_FILE).read().rstrip()
    injected = (
        "\n" + SYMBOLS_START + "\n"
        + layout + "\n"
        + SYMBOLS_END + "\n"
    )
    with open(SYMBOLS_FILE, 'a') as f:
        f.write(injected)
    print('Injected layout into symbols file.')


def uninstall_symbols():
    text = open(SYMBOLS_FILE).read()
    if SYMBOLS_START not in text:
        print('No DPE markers in symbols file; skipping.')
        return
    backup(SYMBOLS_FILE)
    # remove block between markers inclusive
    new = re.sub(rf"{re.escape(SYMBOLS_START)}[\s\S]*?{re.escape(SYMBOLS_END)}\n?", '', text)
    with open(SYMBOLS_FILE, 'w') as f:
        f.write(new)
    print('Removed layout from symbols file.')


def install_variant():
    text = open(RULES_FILE).read()
    if f'<!--{XML_START}-->' in text:
        print('Variant already installed; skipping.')
        return
    backup(RULES_FILE)

    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(RULES_FILE, parser=parser)
    root = tree.getroot()

    us_layout = None
    for layout in root.findall('.//layout'):
        ci = layout.find('configItem')
        if ci is not None and (ci.find('name') is not None and ci.find('name').text == 'us'):
            # ensure shortDescription=en and countryList contains US
            sd = ci.find('shortDescription')
            if sd is not None and sd.text == 'en':
                us_layout = layout
                break
    if us_layout is None:
        print('Could not find US layout in rules file.')
        sys.exit(1)

    vlist = us_layout.find('variantList')
    if vlist is None:
        print('No <variantList> under US layout; cannot install.')
        sys.exit(1)

    variant = ET.Element('variant')
    ci = ET.SubElement(variant, 'configItem')
    nm = ET.SubElement(ci, 'name'); nm.text = 'dpe'
    desc = ET.SubElement(ci, 'description')
    desc.text = 'English (Programmer Dvorak Eur. Keys)'

    vlist.append(ET.Comment(XML_START))
    vlist.append(variant)
    vlist.append(ET.Comment(XML_END))

    tree.write(RULES_FILE, encoding='utf-8', xml_declaration=True)
    print('Injected variant into evdev.xml.')


def uninstall_variant():
    text = open(RULES_FILE).read()
    if f'<!--{XML_START}-->' not in text:
        print('No variant markers found in rules file.')
        return
    backup(RULES_FILE)
    # remove XML comment block inclusive
    new = re.sub(rf"<!--{XML_START}-->[\s\S]*?<!--{XML_END}-->", '', text)
    with open(RULES_FILE, 'w') as f:
        f.write(new)
    print('Removed variant from evdev.xml.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', choices=['install','uninstall','list-backups'])
    args = parser.parse_args()

    if args.cmd == 'list-backups':
        list_backups()
    elif args.cmd == 'install':
        install_symbols()
        install_variant()
    elif args.cmd == 'uninstall':
        uninstall_symbols()
        uninstall_variant()

if __name__ == '__main__':
    main()
