from __future__ import print_function
import numpy as np
import os
from .moxml import *

# NAMESPACES
SVG_NS = '{http://www.w3.org/2000/svg}'
INX_NS = '{http://www.inkscape.org/namespaces/inkscape}'
SOZI_NS = "{http://sozi.baierouge.fr}"
VERBOSE = False

class Path(object):
    def __init__(self, node):
        self.node = node
        self.id = self.node.attrib['id']
        raw = self.node.attrib['d']
        sp = raw.split()
        self.mode = sp.pop(0)        
        xy_dxys = []
        for s in sp:
            ss = s.split(',')
            x = float(ss[0])
            y = float(ss[1])
            xy_dxys.append(np.array([x,y]))
        self.xys = []
        self.xys.append(xy_dxys.pop(0))
        for xy in xy_dxys:
            self.xys.append(self.xys[-1]+xy)
        return

class Rect(object):
    def __init__(self, node):
        self.node = node
        self.id = self.node.attrib['id']
        self.x = float(self.node.attrib['x'])
        self.y = float(self.node.attrib['y'])
        self.xy = np.array([self.x, self.y])        
        if 'transform' in self.node.attrib:
            raw = self.node.attrib['transform']
            if 'matrix' in raw:
                raw = raw[7:-1].split(',')
                t = [ float(r) for r in raw ]
                self.tf = np.array([ [t[0],t[2]], [t[1],t[3]] ])
                self.xy = np.dot(self.tf, self.xy)
                self.x = self.xy[0]
                self.y = self.xy[1]
            elif 'scale' in raw:
                raw = raw[6:-1].split(',')
                sx = float(raw[0])
                sy = float(raw[1])
                self.x *= sx
                self.y *= sy
                self.xy = np.array([self.x, self.y])
            elif 'translate' in raw:
                dr = list(map(float, raw.replace('translate','').replace('(','').replace(')','').split(',')))
                self.x = self.x + dr[0]
                self.y = self.y + dr[1]
                self.xy = np.array([self.x, self.y])
            else:
                pass

        self.h = float(self.node.attrib['height'])
        self.w = float(self.node.attrib['width'])
        if VERBOSE: log << "Frame @ %+03.4e %+03.4e" % (self.x, self.y) << endl
        return

class Text(object):
    def __init__(self, node):
        self.node = node
        self.x = float(self.node.attrib['x'])
        self.y = float(self.node.attrib['y'])
        self.xy = np.array([self.x, self.y])

        if 'transform' in self.node.attrib:
            raw = self.node.attrib['transform']
            if 'matrix' in raw:
                raw = raw[7:-1].split(',')
                t = [ float(r) for r in raw ]
                self.tf = np.array([ [t[0],t[2]], [t[1],t[3]] ])
                self.xy = np.dot(self.tf, self.xy)
                self.x = self.xy[0]
                self.y = self.xy[1]
            else:
                pass
        
        self.text = ''
        self.lines = []
        self.tspan = None
        for child in self.node:
            if child.tag == '%stspan' % SVG_NS:
                self.tspan = child
                if child.text != None:
                    if self.text != '': self.text+='\n'
                    self.text += child.text
                    self.lines.append(child.text)
        if VERBOSE: log << "Text %-4s @ %+03.4e %+03.4e" % ("'"+self.text+"'", self.x, self.y) << endl
        return
    def IsEmpty(self):
        return self.text == ''
    def IsNumber(self):
        try:
            int(self.text)
            return True
        except ValueError:
            return False
    def Set(self, text):
        self.tspan.text = text
        return

class Frame(object):
    def __init__(self, node, **kwargs):
        self.node = node
        self.rect = Rect(self.node)
        default_args = {\
            'id':None,
             'title':None,
             'refid':self.rect.node.attrib['id'],
             'sequence':None,
            'transition-path-hide':'true',
            'transition-profile':'accelerate-decelerate',
            'transition-zoom-percent':'0.0',
             'transition-duration-ms':"1000.0",
            'transition-path':None,
             'timeout-ms':"5000.0",
             'timeout-enable':"false",
             'show-in-frame-list':"true",
             'clip':"false",
             'hide':"true",
            'sozi_ns':"ns1"}
        for key in default_args.keys():
            if not key in kwargs:
                kwargs[key] = default_args[key]
        self.args = kwargs
        # Rank from text
        self.has_rank = False
        self.rank = None
        self.dist_to_rank = None
        # Transition from text
        self.has_transition = False
        self.transition = None
        self.dist_to_transition = None
        return
    def UpdateProperties(self, defaults):
        for key in defaults.keys():
            if not key in self.args:
                log << log.mr << "Invalid defaults key '%s'" % key << endl
            else:
                self.args[key] = defaults[key]
        return
    def SetTransition(self, transition, dist_to_transition):
        if self.has_transition:
            if self.dist_to_transition > dist_to_transition:
                self.dist_to_transition = dist_to_transition
                self.transition = transition
            else: pass
        else:
            self.has_transition = True
            self.transition = transition
            self.dist_to_transition = dist_to_transition
        self.args['transition_duration_ms'] = '%1.3f' % (float(self.transition)*1000.)
        return
    def SetRank(self, rank, dist_to_rank):
        if self.has_rank:
            if self.dist_to_rank > dist_to_rank:
                self.dist_to_rank = dist_to_rank
                self.rank = int(rank)
            else: pass
        else:
            self.has_rank = True
            self.rank = int(rank)
            self.dist_to_rank = dist_to_rank
        return
    def SetSequenceIndex(self, index):
        self.sequ_id = index
        self.args['sequence'] = '%d' % index
        self.args['title'] = '%d' % index
        self.args['id'] = '%d' % index
        return
    def ToElement(self):
        ns_args = {}
        for key in self.args:
            if key == 'id': ns_key = key
            else: ns_key = '%s%s' % (SOZI_NS, key)
            if self.args[key] != None:
                ns_args[ns_key] = self.args[key]
            else: pass
        par = etree.Element('svg', attrib={'%screator' % SOZI_NS : "creator"})
        child = etree.SubElement(par, '%sframe' % SOZI_NS, attrib=ns_args)
        # etree.Element('ns1:frame', nsmap={'ns1' : SOZI_NS})
        return par


def bin_objects_1d(value_list, object_list, n_bins=None, dv=None):
    """
    Groups objects from <object_list> according to their 
    respective values in <value_list> into <n_bins> bins
    """
    v_min = min(value_list)
    v_max = max(value_list)
    if dv == None:
        # Calculate bin width
        dv = (v_max-v_min)/(n_bins-1)
    else:
        # Calculate number of bins
        if n_bins != None: print("WARNING Overriding number of bins <n_bins> using <dv>")
        n_bins = int((v_max-v_min)/dv+0.5)+1
    v_min -= 0.5*dv
    v_max += 0.5*dv
    bin_loc = []
    bin_obj = []
    for i in range(n_bins):
        bin_obj.append([])
        bin_loc.append(v_min+(i+0.5)*dv)
    for v,o in zip(value_list, object_list):
        i = int((v-v_min)/dv)
        bin_obj[i].append(o)
    return n_bins, dv, bin_loc, bin_obj

