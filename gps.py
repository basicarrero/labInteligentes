#!/usr/bin/env python
# -*- coding: utf-8 -*-
u"""
Autor: Basilio Carrero Nevado, Sheila Bustos Jiménez.
Universidad: UCLM
Asignatura: Sistemas Inteligentes (Entrega Final_rev)
Ficheros: gps.py, gpsLibStd.py, OsmApi.py.
"""
import OsmApi
import pickle
import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from gpsLibStd import createGeoNodeDict
from gpsLibStd import SearchProblem
from gpsLibStd import search
from gpsLibStd import Strategy
from gpsLibStd import Strategy_Opt
from gpsLibStd import GPXparser

MAXDEEP = 100


def getCache():
    with open('cache', 'r') as f:
        return pickle.load(f)


def main(argv=None):
    ### Command line options.
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    try:
        # Setup argument parser
        parser = ArgumentParser(description=__doc__,
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-map",
                            dest="recuadro",
                            nargs=4,
                            type=float,
                            metavar=("minLon", "nimLat", "maxLong", "maxLat"),
                            help=u"Recupera de www.openstreetmap.org el \
                                recuadro definido por las coordenadas.")
        parser.add_argument("-clear",
                            action="store_true",
                            help=u"Purga la caché del mapa.")
        parser.add_argument("-path",
                            dest="ab",
                            nargs=2,
                            type=int,
                            metavar=("From", "To"),
                            help=u"Busca una ruta entre dos puntos.")
        parser.add_argument("-strategy",
                            dest="stratToUse",
                            nargs='+',
                            default=['anchura', 'profundidad',
                                     'costouniforme', 'voraz', 'aprima'],
                            metavar="stratName",
                            help=u"Selecciona la estrategia de búsqueda: \
[costouniforme | anchura | profundidad | voraz | aprima] (default: todas)")
        parser.add_argument("-maxdeep",
                            dest="maxdeep",
                            default=[MAXDEEP],
                            nargs=1,
                            type=int,
                            metavar="max",
                            help=u"Especifica una cota de profundidad. \
(default: 100)")
        parser.add_argument("-opt",
                            action="store_true",
                            help=u"Optimiza la selección de Nodos.")
        parser.add_argument("-v",
                            action="store_true",
                            help=u"Muestra mensajes de estado.")
        # Process arguments
        args = parser.parse_args()
        msg = ''
        if args.recuadro:
            with open('cache', 'w') as f:
                LE = OsmApi.OsmApi().Map(*args.recuadro)
                pickle.dump(LE, f)
                msg = "Done. %d items stored." % len(LE)
        if args.clear:
            os.remove('cache')
            msg = "Cache cleared."
        if args.ab:
            nodeDict = createGeoNodeDict(getCache())
            maxdeep = args.maxdeep[0]
            startNode = nodeDict[args.ab[0]]
            endNode = nodeDict[args.ab[1]]
            name = "Route From %d To %d" % (startNode.Id, endNode.Id)
            problem = SearchProblem(name, startNode, endNode)
            for stratStr in args.stratToUse:
                if args.opt:
                    strategy = Strategy_Opt(stratStr, problem.goal, maxdeep)
                else:
                    strategy = Strategy(stratStr, problem.goal, maxdeep)
                (route, stats) = search(problem, strategy)
                filename = "Route%s.gpx" % strategy.name
                with open(filename, 'wb') as f:
                    xl = GPXparser(f, 'utf-8')
                    xl.write_route(route, stats, ident=1)
                    xl.close()
                if args.v:
                    print "%s Done:" % filename
                    keys = sorted(stats)
                    for k in keys:
                        print u"\t%s: %s" % (k, stats[k])
                    print ''
        if args.v:
            print msg
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        sys.stderr.write("gps.py:" + repr(e) + "\n")
        return 2

if __name__ == "__main__":
    sys.exit(main())
