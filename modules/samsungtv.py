#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cherrypy
import htpc
import logging
import socket
import base64
import ssdp
import xmltodict
import urllib2
import re
import itertools
import operator
from operator import itemgetter
from sqlobject import SQLObject, SQLObjectNotFound
from sqlobject.col import StringCol, IntCol
from cherrypy.lib.auth2 import require
#from uuid import getnode as get_mac

class Samsungtvs(SQLObject):
    """ SQLObject class for kodi_tvs table """
    name = StringCol(default=None)
    model = StringCol(default=None)
    # Need to be unique as udp sucks
    host = StringCol(default=None, unique=True)
    mac = StringCol(default=None)
    htpchost = StringCol(default=None)


class Samsungtv:
    def __init__(self):
        self.logger = logging.getLogger('modules.samsungtv')
        Samsungtvs.createTable(ifNotExists=True)
        self.mac = 'E8:E0:B7:D3:A4:62'
        htpc.MODULES.append({
            'name': 'Samsung Remote',
            'id': 'samsungtv',
            'fields': [
                {'type': 'bool', 'label': 'Enable', 'name': 'samsungtv_enable'},
                {'type': 'text', 'label': 'Menu name', 'name': 'samsungtv_name'},
                {'type': 'select',
                 'label': 'TVs',
                 'name': 'samsung_tv_id',
                 'options': [
                        {'name': 'Select', 'value': 0}
                    ],
                'fbutton': [htpc.WEBDIR + 'samsungtv/findtv2', 'Search for tvs', 'Discover']
                },
                {'type': 'text', 'label': 'Tv Name', 'name': 'samsungtv_name2', 'placeholder': 'Living Room'},
                {'type': 'text', 'label': 'IP / Host *', 'name': 'samsungtv_host'},
                {'type': 'text', 'label': 'Tv Model', 'name': 'samsungtv_model'},
                {'type': 'text', 'label': 'HTPC-Manager MAC', 'name': 'samsung_htpcmac'},
                {'type': 'text', 'label': 'HTPC-Manager IP', 'name': 'samsung_htpchost'}

            ]
        })

        tv = htpc.settings.get('samsung_current_tv', 0)
        self.changetv(tv)

    @cherrypy.expose()
    @require()
    def index(self):
        return htpc.LOOKUP.get_template('samsungtv.html').render(scriptname='samsungtv')

    @cherrypy.expose()
    @require()
    def sendkey(self, action):
        try:
            key = action
            if key == 'undefined':
                return
            else:

                src = self.current.htpchost
                mac = self.current.mac
                remote = 'HTPC-Manager remote'
                dst = self.current.host
                application = 'python'
                tv = self.current.model


                new = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                new.connect((dst, 55000))
                msg = chr(0x64) + chr(0x00) +\
                    chr(len(base64.b64encode(src)))    + chr(0x00) + base64.b64encode(src) +\
                    chr(len(base64.b64encode(mac)))    + chr(0x00) + base64.b64encode(mac) +\
                    chr(len(base64.b64encode(remote))) + chr(0x00) + base64.b64encode(remote)
                pkt = chr(0x00) +\
                    chr(len(application)) + chr(0x00) + application +\
                    chr(len(msg)) + chr(0x00) + msg
                new.send(pkt)
                msg = chr(0x00) + chr(0x00) + chr(0x00) +\
                chr(len(base64.b64encode(key))) + chr(0x00) + base64.b64encode(key)
                pkt = chr(0x00) +\
                    chr(len(tv))  + chr(0x00) + tv +\
                    chr(len(msg)) + chr(0x00) + msg
                new.send(pkt)
                new.close()
        except Exception as e:
            print e
            self.logger.debug('Failed to send %s to the tv' % key)

    def getIPfromString(self, string):
        try:
            return re.search("(\d{1,3}\.){3}\d{1,3}", string).group()
        except:
            return ''

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def settv(self, samsungtv_id, samsungtv_name2, samsungtv_host, samsungtv_model, samsungtv_htpcmac):
        """ Create a server if id=0, else update a server """
        if samsungtv_id == "0":
            self.logger.debug("Creating samsungtv in database")
            try:
                tv = Samsungtvs(name=samsungtv_name2,
                                host=samsungtv_host,
                                model=samsungtv_model,
                                htpchost=samsungtv_host,
                                mac=samsungtv_htpcmac)
                self.changetv(tv.id)
                return 1
            except Exception, e:
                self.logger.debug("Exception: " + str(e))
                self.logger.error("Unable to create kodi-Server in database")
                return 0
        else:
            self.logger.debug("Updating tv " + samsungtv_name2 + " in database")
            try:
                tv = Samsungtvs.selectBy(id=samsungtv_id).getOne()
                tv.name = samsungtv_name2
                tv.host = samsungtv_host
                tv.mac = samsungtv_htpcmac
                tv.htpchost = samsungtv_host
                return 1
            except SQLObjectNotFound, e:
                self.logger.error("Unable to update Samsung tv " + tv.name + " in database")
                return 0

    @cherrypy.expose()
    @require()
    def deltv(self, id):
        """ Delete a server """
        self.logger.debug("Deleting server " + str(id))
        Samsungtvs.delete(id)
        self.changetv()
        return

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def changetv(self, id=0):
        try:
            self.current = Samsungtvs.selectBy(id=id).getOne()
            htpc.settings.set('samsung_current_tv', str(id))
            self.logger.info("Selecting Samsung tv: %s", id)
            return "success"
        except SQLObjectNotFound:
            try:
                self.current = Samsungtvs.select(limit=1).getOne()
                self.logger.error("Invalid server. Selecting first Available.")
                return "success"
            except SQLObjectNotFound:
                self.current = None
                self.logger.warning("No configured Samsungtvs.")
                return "No valid servers"

    @cherrypy.expose()
    @require()
    @cherrypy.tools.json_out()
    def gettvs(self, id=None):
        if id:
            """ Get samsungtvs info """
            try:
                tv = Samsungtvs.selectBy(id=id).getOne()
                return dict((c, getattr(tv, c)) for c in tv.sqlmeta.columns)
            except SQLObjectNotFound:
                return

        """ Get a list of all tvs and the current tv """
        tvs = []
        for s in Samsungtvs.select():
            tvs.append({'id': s.id, 'name': s.name})
        if len(tvs) < 1:
            return
        try:
            current = self.current.name
        except AttributeError:
            current = None
        return {'current': current, 'tvs': tvs}

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    @require()
    def findtv2(self, id=None):
        print "findtv2"
        result_list = []
        r = []
        sr = 0

        # Find htpc.managers ip
        ip = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip.connect(('8.8.8.8', 80))
        local_ip = ip.getsockname()[0]

        # Tries to find the mac, this is likly to be the wrong one.. my tv accepts anything
        #mac = ':'.join(("%012X" % get_mac())[i:i+2] for i in range(0, 12, 2))
        # Fake the mac since my tv accepts anything
        mac = 'E8:E0:B7:D3:A4:62'

        # Since udp sucks balls
        while True:
            sr += 1
            search = ssdp.discover('ssdp:all')
            #search = ssdp.discover('urn:samsung.com:device:RemoteControlReceiver:1')
            r.append(search)
            if len(r) >= 2:
                break

        for i in r:
            for item in i:
                host = self.getIPfromString(item.location)
                if host:
                    try:
                        desc = urllib2.urlopen(item.location).read()
                        d = {}
                        xml = xmltodict.parse(desc)
                        if 'tv' in xml["root"]["device"]["friendlyName"].lower():
                            d["name"] = xml["root"]["device"]["friendlyName"]
                            d["host"] = host
                            #d["id"] = iid
                            d["model"] = xml["root"]["device"]["modelName"]
                            d["htpchost"] = local_ip
                            d["mac"] = mac
                            result_list.append(d)

                    except Exception as e:
                        pass

        # Remove dupe dicts from list
        getvals = operator.itemgetter('host')
        result_list.sort(key=getvals)
        result = []
        for k, g in itertools.groupby(result_list, getvals):
            result.append(g.next())

        for something in result:
            try:
                Samsungtvs(**something)
            except Exception as e:
                # Dont stop on dupe errors
                continue

        return result
