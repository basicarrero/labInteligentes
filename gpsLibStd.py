# -*- coding: utf-8 -*-
"""
Biblioteca estandar del programa.
"""
import heapq
import math
import time
from abc import ABCMeta, abstractmethod
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl


# Clase para almacenar un nodo geografico
class GeoNode:
    def __init__(self, Id, lon, lat, name=''):
            self.Id = Id
            self.lon = lon
            self.lat = lat
            self.adyList = []
            self.name = name

    def getId(self):
        return self.Id

    def getCoord(self):
        return (self.lon, self.lat)

    def getAdyList(self):
        return self.adyList

    def addAdyNode(self, node):
        self.adyList.append(node)

    def delAdyNode(self, node):
        self.adyList.remove(node)

    def __str__(self):
        if self.name == '':
            return "%d" % self.Id
        else:
            return u"%d (%s)" % (self.Id, self.name)


# Clase para almacenar los nodos de arbol de busqueda
class TreeNode:
    def __init__(self, priority, parent, geoNode, cost):
        self.data = geoNode
        self.parent = parent
        self.priority = priority
        if parent is None:
            self.cumcost = 0
            self.deep = 0
        else:
            self.cumcost = parent.cumcost + cost
            self.deep = parent.deep + 1

    def isFinal(self):
        if self.data.adyList:
            return False
        else:
            return True

    def getParent(self):
        return self.parent

    # Crea un TreeNode raiz a partir de un nodo
    @staticmethod
    def makeRoot(geonode):
        return TreeNode(0, None, geonode, 0)

    def getNode(self):
        return self.data

    def getCumcost(self):
        return self.cumcost

    def getPriority(self):
        return self.priority

    def getDeep(self):
        return self.deep

    def __str__(self):
        if self.info == '':
            return "%d" % self.Id
        else:
            return u"%d (%s)" % (self.Id, self.info)


# Clase frontera implementada con un monticulo
class Bound:
    def __init__(self, item):
            self.heap = []
            self.root = item
            self.add(item)

    def next(self):
        try:
            return heapq.heappop(self.heap)[1]
        except IndexError:
            raise StopIteration

    def add(self, item):
        if isinstance(item, TreeNode):
            heapq.heappush(self.heap, (item.priority, item))

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.heap)

    def clear(self):
        del self.heap[:]
        self.add(self.root)

    def __str__(self):
        return repr(self.heap)


# Clase Asbtracta
class Problem():
    __metaclass__ = ABCMeta

    def __init__(self, name, init, goal):
        self.name = name
        self.status = init
        self.start = init
        self.goal = goal

    @abstractmethod
    def isDone(self, status):
        pass

    @abstractmethod
    def successors(self, status):
        return []


# Implementacion del problema
class SearchProblem(Problem):
    def __init__(self, name, init, goal):
        Problem.__init__(self, name, init, goal)
        self.root = TreeNode.makeRoot(init)
        self.bound = Bound(self.root)

    # Comprueba si el estado actual es meta
    def isDone(self, status):
        if status.data == self.goal:
            return True
        else:
            return False

    # Explande la frontera aplicando la estrategia
    def successors(self, item):
        descendents = item.data.adyList
        if item.parent is not None:
            parent = item.parent.data
            descendents = [(n, p) for (n, p) in descendents if n is not parent]
        return descendents


# Representa una estrategia de busqueda
class Strategy():
    def __init__(self, stratStr, goal, maxDeep):
        self.mapTable = {"costouniforme": self.__strat_costoUniforme,
                         "anchura": self.__strat_anchura,
                         "profundidad": self.__strat_profundidad,
                         "voraz": self.__strat_voraz,
                         "aprima": self.__strat_aPrima}

        self.maxDeep = maxDeep
        self.strId = stratStr
        self.name = "%s%s" % (stratStr[0].upper(), stratStr[1:])
        self.__getPriority = self.mapTable[self.strId]
        self.goal = goal

    def apply(self, bound, treeParent, candidates):
        count = 0
        for node, cost in candidates:
            priority = self.__getPriority(treeParent, node)
            newTreeNode = TreeNode(priority, treeParent, node, cost)
            if newTreeNode.getDeep() < self.maxDeep:
                bound.add(newTreeNode)
                count += 1
        return count

    def __strat_costoUniforme(self, treeParent, node):
        return treeParent.getCumcost()

    def __strat_anchura(self, treeParent, node):
        return treeParent.priority + 1

    def __strat_profundidad(self, treeParent, node):
        return treeParent.priority - 1

    def __strat_voraz(self, treeParent, node):
        return distance(self.goal, node)

    def __strat_aPrima(self, treeParent, node):
        hn = distance(self.goal, node)
        gn = treeParent.getCumcost()
        return hn+gn


# Representa una estrategia de busqueda optimizada
class Strategy_Opt(Strategy):
    def __init__(self, stratStr, goal, maxDeep):
        Strategy.__init__(self, stratStr, goal, maxDeep)
        self.__getPriority = self.mapTable[self.strId]
        self.name = "%s_Opt" % self.name
        self.nodeTable = {}

    def apply(self, bound, treeParent, candidates):
        count = 0
        for node, cost in candidates:
            priority = self.__getPriority(treeParent, node)
            try:
                actualPriority = self.nodeTable[node.getId()]
            except KeyError:
                actualPriority = None
            if actualPriority is None or priority < actualPriority:
                newTreeNode = TreeNode(priority, treeParent, node, cost)
                if newTreeNode.getDeep() < self.maxDeep:
                    self.nodeTable[node.getId()] = priority
                    bound.add(newTreeNode)
                    count += 1
        return count


# Parser GPX
class GPXparser():
    def __init__(self, output, encoding):
        self.logger = XMLGenerator(output, encoding)
        self.logger.startDocument()
        header = {u'version': u'1.1',
                  u'creator': u'gps.py',
                  u'xmlns:xsi': u'"http://www.w3.org/2001/XMLSchema-instance"',
                  u'xmlns': u'"http://www.topografix.com/GPX/1/1"',
                  u'xsi:schemaLocation': u'"http://www.topografix.com/GPX/1/1 \
http://www.topografix.com/GPX/1/1/gpx.xsd"'}
        self.logger.startElement(u"gpx", AttributesImpl(header))
        self.output = output
        self.encoding = encoding

    def start(self, name, attDict=None):
        if attDict:
            attrs = AttributesImpl(attDict)
        else:
            attrs = AttributesImpl({})
        self.logger.startElement(name, attrs)

    def end(self, name):
        self.logger.endElement(name)

    def data(self, obj):
        self.logger.characters(obj)

    def newLine(self, ident):
        self.logger.characters("\n%s" % ('\t' * ident))

    def write_trkpt(self, node, ident=0):
        self.newLine(ident)
        pos = {u'lon': str(node.lon), u'lat': str(node.lat)}
        self.start(u"trkpt", pos)
        self.start(u"ele")
        self.data(str(node.Id))
        self.end(u"ele")
        self.end(u"trkpt")

    def write_desc(self, stats, ident=0):
        keys = sorted(stats)
        self.newLine(ident)
        self.start(u"desc")
        for k in keys:
            self.newLine(ident + 1)
            self.start(k)
            self.data(u"%s: %s" % (k, stats[k]))
            self.end(k)
        self.newLine(ident)
        self.end(u"desc")

    def write_wpt(self, name, pos, ident=0):
        self.newLine(ident)
        self.start(u"wpt", pos)
        self.start(u"name")
        self.data(name)
        self.end(u"name")
        self.end(u"wpt")

    def write_trkseg(self, route, ident=0):
        self.newLine(ident)
        self.start(u"trkseg")
        for node in route:
            self.write_trkpt(node, ident + 1)
        self.newLine(ident)
        self.end(u"trkseg")

    def write_route(self, route, stats, ident=0):
        if route:
            pos = {u'lon': str(route[0].lon), u'lat': str(route[0].lat)}
            self.write_wpt(u"Origen", pos, ident)
            pos = {u'lon': str(route[-1].lon), u'lat': str(route[-1].lat)}
            self.write_wpt(u"Destino", pos, ident)
            self.newLine(ident)
            name = u'Route from %d to %d' % (route[0].Id, route[1].Id)
            self.start(u"trk")
            self.start(u"name")
            self.logger.characters(name)
            self.end(u"name")
            if stats:
                self.write_desc(stats, ident + 1)
            self.write_trkseg(route, ident + 1)
            self.newLine(ident)
            self.end(u"trk")

    def close(self):
        self.newLine(0)
        self.end(u"gpx")
        self.logger.endDocument()
        return


# Algoritmo de busqueda
def search(problem, strategy):
    route = []
    cost = 0
    esp = 1  # La frontera contiene el elemento raiz
    t = time.clock()
    for item in problem.bound:
        if problem.isDone(item):
            # Crea la ruta desde el item a la raiz
            route = [item.data]
            parent = item.parent
            while parent.parent is not None:
                route.append(parent.data)
                parent = parent.parent
            route.append(parent.data)
            route = route[::-1]
            cost = item.getCumcost()
            break
        candidates = problem.successors(item)
        esp += strategy.apply(problem.bound, item, candidates)
    t = time.clock() - t
    stats = {u"Nodo_Origen": problem.start,
             u"Nodo_Destino": problem.goal,
             u"Estrategia": strategy.name,
             u"Prof.Máx": strategy.maxDeep,
             u"Coste_Solución": cost,
             u"Compl._Espacial": esp,
             u"Compl._Temporal": t}
    problem.bound.clear()
    return (route, stats)


# Crea un Dicionario representando el grafo a partir de la lista de
# elementos devuelta por OsmApi.py
def createGeoNodeDict(LE):
    LEnodes = (n for n in LE if n['type'] == 'node')
    nodeDict = {}
    for n in LEnodes:
        try:
            nodeDict[n['data']['id']] = GeoNode(n['data']['id'],
                                                n['data']['lon'],
                                                n['data']['lat'],
                                                n['data']['tag']['name'])
        except KeyError:
            nodeDict[n['data']['id']] = GeoNode(n['data']['id'],
                                                n['data']['lon'],
                                                n['data']['lat'])
    LEways = (n for n in LE if n['type'] == 'way')
    for way in LEways:
        try:
            if (way['data']['tag']['highway'] == 'residential' or
                    way['data']['tag']['highway'] == 'pedestrian' or
                    way['data']['tag']['highway'] == 'trunk'):
                wayNodes = way['data']['nd']
                for idx, nodeId in enumerate(wayNodes):
                    node = nodeDict[nodeId]
                    if way['data']['tag']['oneway'] == 'yes':
                        adyNode = nodeDict[wayNodes[idx + 1]]
                        node.addAdyNode((adyNode, distance(node, adyNode)))
                    elif idx > 0 and way['data']['tag']['oneway'] == '-1':
                        adyNode = nodeDict[wayNodes[idx - 1]]
                        node.addAdyNode((adyNode, distance(node, adyNode)))
                    else:
                        if idx > 0:
                            adyNode = nodeDict[wayNodes[idx - 1]]
                            node.addAdyNode((adyNode, distance(node, adyNode)))
                        adyNode = nodeDict[wayNodes[idx + 1]]
                        node.addAdyNode((adyNode, distance(node, adyNode)))
        except (KeyError, IndexError):
            pass
    return nodeDict


def merc_x(lon):
    r_major = 6378137.000
    return r_major * math.radians(lon)


def merc_y(lat):
    if lat > 89.5:
        lat = 89.5
    if lat < -89.5:
        lat = -89.5
    r_major = 6378137.000
    r_minor = 6356752.3142
    temp = r_minor / r_major
    eccent = math.sqrt(1 - temp ** 2)
    phi = math.radians(lat)
    sinphi = math.sin(phi)
    con = eccent * sinphi
    com = eccent / 2
    con = ((1.0 - con) / (1.0 + con)) ** com
    ts = math.tan((math.pi / 2 - phi) / 2) / con
    y = 0 - r_major * math.log(ts)
    return y


#Distancia entre dos punto geograficos.
#Se obtiene sus proyecciones Mercator
#y la distancia euclidea entre ellas
def distance(nA, nB):
    x1 = merc_x(nA.lon)
    x2 = merc_x(nB.lon)
    y1 = merc_y(nA.lat)
    y2 = merc_y(nB.lat)
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
