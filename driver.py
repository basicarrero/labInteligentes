#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Driver
    -getmap: Recupera el mapa.
'''
import sys
import time
from gps import main

nargs = len(sys.argv)
if nargs > 1:
    if sys.argv[1] == '-getmap':
        sys.argv.pop()
        args = "-map -3.9349500 38.9792300 -3.9192900 38.9964400"
        print args
        main(args.split())
        print "Mapa Recuperado."
else:
    t = time.clock()
    args = "-path 368287515 806369190 -v"
    print args
    main(args.split())
    args = "-path 368287515 806369190 -v -opt"
    print args
    main(args.split())
    print "Todo Completado en %f segundos!" % (time.clock() - t)
