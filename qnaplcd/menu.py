#!/usr/bin/env python3
import sys
import os
import time
import platform
import subprocess
import socket
import threading
import json

from .driver import QnapLCD
from .default import PORT, PORT_SPEED, DISPLAY_TIMEOUT

_lcd = None

_lcd_timer = None
def _lcd_on():
    global _lcd_timer

    _lcd.backlight(True)

    if _lcd_timer:
        _lcd_timer.cancel()

    _lcd_timer = threading.Timer(DISPLAY_TIMEOUT, lambda: _lcd.backlight(False))
    _lcd_timer.start()

def _shell(cmd):
    return subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()

def _show_version():
    sys_name = platform.node()
    sys_vers = f'{platform.system()} ({platform.machine()})'
    _lcd.clear()
    _lcd.write(0, [sys_name, sys_vers])

def _show_truenas():
    truenas = _shell('cli -c \'system version\'')
    truenas = truenas.split('-')

    _lcd.clear()
    _lcd.write(0, ['-'.join(truenas[:-1]), truenas[-1]])

def _show_uptime():
    uptime = _shell('uptime').split(',')
    up = ' '.join(uptime[0].split()[2:]) + ' ' + uptime[1]
    load = os.getloadavg()
    _lcd.clear()
    _lcd.write(0, [f'Up  : {up}', f'Load: {load[0]} {load[1]}, {load[2]}'])

_ip_addresses = []
def _add_ips_to_menu():
    def get_kind(iface):
        if 'linkinfo' in iface:
            if 'info_kind' in iface['linkinfo']:
                return iface['linkinfo']['info_kind']

        return ''

    def get_ipv4(iface):
        if 'addr_info' in iface:
            for addr in iface['addr_info']:
                if addr['family'] == 'inet':
                    return addr['local']

        return '0.0.0.0'

    ip_json = json.loads(_shell('ip -details -json address show'))
    _ip_addresses.clear()
    for iface in ip_json:
        if iface['link_type'] == 'loopback':
            continue

        if get_kind(iface) not in ['', 'tun']:
                continue

        _ip_addresses.append(( iface['ifname'], get_ipv4(iface)))

    while _show_ip in _menu:
        _menu.remove(_show_ip)

    for _ in _ip_addresses:
        _menu.append(_show_ip)

def _show_ip():
    ip_index = 0
    for index in range(_menu_item):
        if _menu[index] == _show_ip:
            ip_index += 1

    _lcd.clear()
    _lcd.write(0, [f'{_ip_addresses[ip_index][0]}', f'{_ip_addresses[ip_index][1]}'])

_zfs_pools = []
def _add_zpools_to_menu():
    pools = _shell('zpool list').split('\n')

    _zfs_pools.clear()
    for pool in pools[1:]:
        _zfs_pools.append(pool.split())

    # remove existing zfs pool menu items
    while _show_zpool in _menu:
        _menu.remove(_show_zpool)

    # add zfs pool menu items for discovered pools
    for _ in _zfs_pools:
        _menu.append(_show_zpool)

def _show_zpool():
    pool_index = 0
    for index in range(_menu_item):
        if _menu[index] == _show_zpool:
            pool_index += 1

    pool = _zfs_pools[pool_index]

    _lcd.clear()
    _lcd.write(0, [f'{pool[0]} ({pool[7]})', f'{pool[2]} of {pool[1]}'])
    
#
# Menu
#
_menu_item = 0
_menu = [
    _show_truenas,
    _show_version,
    _show_uptime
]

def _response_handler(command, data):
    global _menu_item, lcd_timeout
    prev_menu = _menu_item

    #print(f'RECV: {command} - {data:#04x}')

    if command == 'Switch_Status':
        _lcd_on()

        if data == 0x01: # up
            _menu_item = (_menu_item - 1) % len(_menu)

        if data == 0x02: # down
            _menu_item = (_menu_item + 1) % len(_menu)

    if prev_menu != _menu_item:
        #print(f'SHOW: {menu_item}')
        _menu[_menu_item]()


def menu():
    "a Python script that will display a menu similar to the default QNAP menu, written for TrueNAS SCALE but may work with other TrueNAS and FreeNAS systems. This should take the place of the *postinit.py* script if you want the menu system active."
    global _lcd
    _lcd = QnapLCD(PORT, PORT_SPEED, _response_handler)
    _lcd_on()
    _lcd.reset()
    _lcd.clear()

    quit = False
    while not quit:
        _add_ips_to_menu()
        _add_zpools_to_menu()
        _menu[_menu_item]()

        print('sleep...')
        time.sleep(30)

    _lcd.backlight(False)
