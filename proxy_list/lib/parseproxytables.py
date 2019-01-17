#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Nikolay Nezhevenko <nikolay.nezhevenko@gmail.com>"


def _read_file(path_to_file):
    with open(path_to_file, 'r') as fo:
        result = fo.read()
    return result


def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def parse_free_proxy_list_net(path_to_file):
    data_from_file = _read_file(path_to_file)
    proxies_list = list()
    for proxy_line in data_from_file.strip().split('\n'):
        proxy_info = proxy_line.split()
        if 'transparent' not in proxy_line:
            proxies_list.append("http://%s:%s" % (proxy_info[0], proxy_info[1]))
    return proxies_list


def parse_freeproxylists_net(path_to_file):
    data_from_file = _read_file(path_to_file)
    proxies_list = list()
    for proxy_line in data_from_file.strip().split('\n'):
        proxy_info = proxy_line.split()
        proxies_list.append("http://%s:%s" % (proxy_info[0], proxy_info[1]))
    return proxies_list


def parse_hidemy_name(path_to_file):
    data_from_file = _read_file(path_to_file)
    proxies_list = list()
    for chunk_with_proxy_info in _chunks(data_from_file.strip().split('\n'), 4):
        proxy_info_line = ' '.join(chunk_with_proxy_info)
        proxy_info = proxy_info_line.split()
        proxies_list.append("http://%s:%s" % (proxy_info[0], proxy_info[1]))
    return proxies_list


def parse_proxylist_hidemyass_com(path_to_file):
    data_from_file = _read_file(path_to_file)
    proxies_list = list()
    for chunk_with_proxy_info in _chunks(data_from_file.strip().split('\n'), 2):
        proxy_info_line = ' '.join(chunk_with_proxy_info)
        proxy_info = proxy_info_line.split('\t')
        proxies_list.append("http://%s:%s" % (proxy_info[1], proxy_info[2]))
    return proxies_list


def save_proxy_list(proxy_list, path_to_file):
    with open(path_to_file, 'w') as fo:
        for line in proxy_list:
            fo.write(line + '\n')





