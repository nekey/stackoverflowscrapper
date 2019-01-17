#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Nikolay Nezhevenko <nikolay.nezhevenko@gmail.com>"


""" A multithreaded proxy checker

Given a file containing proxies, per line, in the form of ip:port, will attempt
to establish a connection through each proxy to a provided URL. Duration of
connection attempts is governed by a passed in timeout value. Additionally,
spins off a number of daemon threads to speed up processing using a passed in
threads parameter. Proxies that passed the test are written out to a file
called results.txt

Usage:

    goodproxy.py [-h] -file FILE -url URL [-timeout TIMEOUT] [-threads THREADS]

Parameters:

    -file    -- filename containing a list of ip:port per line
    -url     -- URL to test connections against
    -timeout -- attempt time before marking that proxy as bad (default 1.0)
    -threads -- number of threads to spin off (default 16)

Functions:

    get_proxy_list_size  -- returns the current size of the proxy holdingQueue
    test_proxy            -- does the actual connecting to the URL via a proxy
    main                 -- creates daemon threads, write results to a file

"""
import argparse
import queue
import socket
import sys
import threading
import time
import urllib.request


def get_proxy_list_size(proxy_list):
    """ Return the current Queue size holding a list of proxy ip:ports """

    return proxy_list.qsize()


def test_proxy(url, url_timeout, proxy_list, lock, good_proxies, bad_proxies):
    """ Attempt to establish a connection to a passed in URL through a proxy.

    This function is used in a daemon thread and will loop continuously while
    waiting for available proxies in the proxy_list. Once proxy_list contains
    a proxy, this function will extract that proxy. This action automatically
    lock the queue until this thread is done with it. Builds a urllib.request
    opener and configures it with the proxy. Attempts to open the URL and if
    successsful then saves the good proxy into the good_proxies list. If an
    exception is thrown, writes the bad proxy to a bodproxies list. The call
    to task_done() at the end unlocks the queue for further processing.

    """

    while True:

        # take an item from the proxy list queue; get() auto locks the
        # queue for use by this thread
        proxy_ip = proxy_list.get()

        # configure urllib.request to use proxy
        proxy = urllib.request.ProxyHandler({'http': proxy_ip})
        opener = urllib.request.build_opener(proxy)
        urllib.request.install_opener(opener)

        # some sites block frequent querying from generic headers
        request = urllib.request.Request(
            url, headers={'User-Agent': 'Proxy Tester'})

        try:
            # attempt to establish a connection
            urllib.request.urlopen(request, timeout=float(url_timeout))

            # if all went well save the good proxy to the list
            with lock:
                good_proxies.append(proxy_ip)

        except (urllib.request.URLError,
                urllib.request.HTTPError,
                socket.error):

            # handle any error related to connectivity (timeouts, refused
            # connections, HTTPError, URLError, etc)
            with lock:
                bad_proxies.append(proxy_ip)

        finally:
            proxy_list.task_done()  # release the queue


def main(argv):
    """ Main Function

    Uses argparse to process input parameters. File and URL are required while
    the timeout and thread values are optional. Uses threading to create a
    number of daemon threads each of which monitors a Queue for available
    proxies to test. Once the Queue begins populating, the waiting daemon
    threads will start picking up the proxies and testing them. Successful
    results are written out to a results.txt file.

    """

    proxy_list = queue.Queue()  # Hold a list of proxy ip:ports
    lock = threading.Lock()  # locks good_proxies, bad_proxies lists
    good_proxies = []  # proxies that passed connectivity tests
    bad_proxies = []  # proxies that failed connectivity tests

    # Process input parameters
    parser = argparse.ArgumentParser(description='Proxy Checker')

    parser.add_argument(
        '-file', help='a text file with a list of proxy:port per line',
        required=True)
    parser.add_argument(
        '-url', help='URL for connection attempts', required=True)
    parser.add_argument(
        '-timeout',
        type=float, help='timeout in seconds (defaults to 1', default=1)
    parser.add_argument(
        '-threads', type=int, help='number of threads (defaults to 16)',
        default=16)

    args = parser.parse_args(argv)

    # setup daemons ^._.^
    for _ in range(args.threads):
        worker = threading.Thread(
            target=test_proxy,
            args=(
                args.url,
                args.timeout,
                proxy_list,
                lock,
                good_proxies,
                bad_proxies))
        worker.setDaemon(True)
        worker.start()

    start = time.time()

    # load a list of proxies from the proxy file
    with open(args.file) as proxyfile:
        for line in proxyfile:
            proxy_list.put(line.strip())

    # block main thread until the proxy list queue becomes empty
    proxy_list.join()

    # save results to file
    with open("result.txt", 'w') as result_file:
        result_file.write('\n'.join(good_proxies))

    # some metrics
    print("Runtime: {0:.2f}s".format(time.time() - start))


if __name__ == "__main__":
    main(sys.argv[1:])