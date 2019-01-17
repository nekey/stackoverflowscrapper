#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Nikolay Nezhevenko <nikolay.nezhevenko@gmail.com>"


import os

from lib.parseproxytables import parse_free_proxy_list_net, parse_freeproxylists_net,\
    parse_hidemy_name, parse_proxylist_hidemyass_com, save_proxy_list
from lib.check_proxies import main as check_proxies_main


CONFIG = {
    'data_path': './data',
    'storage_path': './storage',
    'temp_file_with_all_proxies': 'all_proxies.txt',
    'free_proxy_list_net_file': 'new_proxies.free-proxy-list.net.txt',
    'freeproxylists_net_file': 'new_proxies.freeproxylists.net.txt',
    'hidemy_name_file': 'new_proxies.hidemy.name.txt',
    'proxylist_hidemyass_com_file': 'new_proxies.proxylist.hidemyass.com.txt',
    'url_for_check': "http://stackoverflow.com/questions",
    'timeout': "5",
    'threads': "16"
}


def get_total_proxy_list():
    all_proxies = list()
    all_proxies.extend(parse_free_proxy_list_net(os.path.join(CONFIG['data_path'], CONFIG['free_proxy_list_net_file'])))
    all_proxies.extend(parse_freeproxylists_net(os.path.join(CONFIG['data_path'], CONFIG['freeproxylists_net_file'])))
    all_proxies.extend(parse_hidemy_name(os.path.join(CONFIG['data_path'], CONFIG['hidemy_name_file'])))
    all_proxies.extend(parse_proxylist_hidemyass_com(os.path.join(CONFIG['data_path'], CONFIG['proxylist_hidemyass_com_file'])))

    return sorted(list(set(all_proxies)))


def print_total_proxy_list(proxies):
    for proxy in proxies:
        print(proxy)


if __name__ == '__main__':
    proxies = get_total_proxy_list()
    print('Total proxy count to validate: %s' % len(proxies))
    save_proxy_list(proxies, os.path.join(CONFIG['storage_path'], CONFIG['temp_file_with_all_proxies']))
    check_proxies_main(["-file", os.path.join(CONFIG['storage_path'], CONFIG['temp_file_with_all_proxies']),
                        "-url", CONFIG['url_for_check'],
                        "-timeout", CONFIG['timeout'],
                        "-threads", CONFIG['threads']
                        ])
    print("See result.txt for check new proxy list")
