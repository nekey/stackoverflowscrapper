#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Nikolay Nezhevenko <nikolay.nezhevenko@gmail.com>"

import os

if __name__ == '__main__':
    os.remove('./comboquestion.jl')
    os.remove('./comboquestion.log')
    for filename in os.listdir('./tmp'):
        os.remove(os.path.join('./tmp', filename))
