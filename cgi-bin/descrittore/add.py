#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  vicinoa.py
#
#  Copyright 2011 soncio <soncio@SONCIO-EEEPC>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


import sys
sys.path.append('/var/www/progettoTW/cgi-bin/descrittore/')
from mod_python import apache as A, util
from encoding import smart_str
from operator import itemgetter as IG
import json, urllib2, math, csv, codecs, psycopg2, pprint

def index(req):
    req.content_type = 'text/plain; charset="UTF-8"'
    req.headers_out.add("Access-Control-Allow-Origin","*")
    if req.method != 'GET':
        req.status = A.HTTP_METHOD_NOT_ALLOWED
        req.write('405: METHOD NOT ALLOWED\r\n')
        req.write('metodo %s non permesso.\r\n' % req.method)
        raise A.SERVER_RETURN, A.DONE

    try:
        parms = util.FieldStorage(req)
        category = smart_str(parms.getfirst('category'))
        lat = float(parms.getfirst('lat'))
        long = float(parms.getfirst('long'))
        name = smart_str(parms.getfirst('name'))
        address = smart_str(parms.getfirst('address'))
        subcategory = smart_str(parms.getfirst('subcategory'))
        opening = smart_str(parms.getfirst('opening'))
        note = smart_str(parms.getfirst('note'))
        tel = smart_str(parms.getfirst('tel'))
        closing = smart_str(parms.getfirst('closing'))
    except:
        req.status = A.HTTP_NOT_ACCEPTABLE
        req.write('406: NOT ACCEPTABLE\r\n')
        req.write('parametri errati.')
        raise A.SERVER_RETURN, A.DONE

    conn = psycopg2.connect("dbname='trovatutto' user='admin' password='admin'")
    cur = conn.cursor()
    cur.execute("INSERT INTO waiting(name,category,address,latitude,longitude,opening,closing,tel,note,subcategory) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);\n", (name,category,address,lat,long,opening,closing,tel,note,subcategory))
    conn.commit()
    cur.close()
    conn.close()
    req.write('Richiesta ricevuta, verrà valutata nelle prossime ore. GRAZIE per la segnalazione!')
    req.status = A.OK
    raise A.SERVER_RETURN, A.DONE

