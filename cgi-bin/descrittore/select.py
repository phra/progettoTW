#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  vicinoa.py
#
#  Copyright 2013 phra <phra@phb0x>
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

RT = 6372795.477598

def toplain(listout):
    s = '\n'.join('RESULT|||V') + '\n'
    for tupla in listout:
        s += 'ID: ' + smart_str(tupla[0]) + ', NAME: ' + smart_str(tupla[1]) + ', LAT: ' + smart_str(tupla[4]) + ', LONG: ' + smart_str(tupla[5]) + '.\n'
    return s

def tojson(listout):
    dictoutjson = {}
    dictout = {}
    meta = [('creator', 'phra'), ('created', '20/12/2011'), ('version', '1.1')]
    metadata = dict(meta)
    for t in listout:
        dictout[t[0]] = {'lat': t[4], 'long': t[5], 'category': smart_str(t[2]), 'name': t[1], 'opening': t[7], 'closing': t[8], 'address': t[6], 'tel': t[9], 'subcategory': t[3], 'note': t[10]}
    dictoutjson['metadata'] = metadata
    dictoutjson['locations'] = dictout
    return json.dumps(dictoutjson)

def toxml(listout):
    s = '''<?xml version="1.0" encoding="UTF-8"?>
<locations>
    <metadata>
        <creator>phra</creator>
        <created>12/20/2011</created>
        <version>1.2</version>
        <note>Le date sono in formato americano: MM/GG/AAAA</note>
    </metadata>
'''
    for t in listout:
        s += '''<location id="%s" lat="%s" long="%s">
        <category> %s </category>
        <subcategory> %s </subcategory>
        <name> %s </name>
        <address> %s </address>
        <tel> %s </tel>
        <opening> %s </opening>
        <closing> %s </closing>
        <note> %s </note>
        </location>''' % (smart_str(t[0]),smart_str(t[4]),smart_str(t[5]),smart_str(t[2]),smart_str(t[3]),smart_str(t[1]),smart_str(t[6]),smart_str(t[9]),smart_str(t[7]),smart_str(t[8]),smart_str(t[10]))
    s += '</locations>'
    return s

def tocsv(listout):
    s = '"id","category","name","address","lat","long","subcategory","note","opening","closing"'
    for t in listout:
        s += '"%s","%s","%s","%s","%s","%s","%s","%s","%s,"%s","%s","%s","%s","%s","%s","Working Group LTW 2011/2012","2011-12-20","2012-10-01","1.1","Unknown"\r\n' % (t[0],t[2],t[1],t[6],t[4],t[5],t[3],t[10],t[7],t[8])
    return s


def index(req):
    listout = []
    if not (('application/json' in req.headers_in['Accept']) or ('application/xml' in req.headers_in['Accept']) or ('text/csv' in req.headers_in['Accept'])):
        req.content_type = 'text/plain; charset="UTF-8"'
        req.headers_out.add("Access-Control-Allow-Origin","*")
        req.status = A.HTTP_NOT_ACCEPTABLE
        req.write('406: NOT ACCEPTABLE\r\n')
        req.write('intersezione tra content-type vuota.\r\n')
        raise A.SERVER_RETURN, A.DONE

    content_type = req.headers_in['Accept']
    req.content_type = 'text/plain; charset="UTF-8"'
    req.headers_out.add("Access-Control-Allow-Origin","*")
    if req.method != 'GET':
        req.status = A.HTTP_METHOD_NOT_ALLOWED
        req.write('405: METHOD NOT ALLOWED\r\n')
        req.write('metodo %s non permesso.\r\n' % req.method)
        raise A.SERVER_RETURN, A.DONE
    parms = util.FieldStorage(req)
    name = smart_str(parms.getfirst('name')).lower()
    id = smart_str(parms.getfirst('id')).lower()
    category = smart_str(parms.getfirst('category')).lower()
    address = smart_str(parms.getfirst('address')).lower()
    conn = psycopg2.connect("dbname='trovatutto' user='admin' password='admin'")
    cur = conn.cursor()
    if id != 'none':
        cur.execute("SELECT * FROM locations a WHERE a.id = %s;", (id,))
    elif name != 'none':
        if category != 'none':
            if address != 'none':
                cur.execute("SELECT * FROM locations WHERE POSITION(%s IN LOWER(name)) > 0 AND category = %s AND POSITION(%s IN LOWER(address)) > 0 UNION ALL SELECT * FROM waiting WHERE POSITION(%s IN LOWER(name)) > 0 AND category = %s AND POSITION(%s IN LOWER(address)) > 0 ;",(name,category,address,name,category,address))
            else:
                cur.execute("SELECT * FROM locations WHERE POSITION(%s IN LOWER(name)) > 0 AND category = %s UNION ALL SELECT * FROM waiting WHERE POSITION(%s IN LOWER(name)) > 0 AND category = %s;",(name,category,name,category))
        else:
            if address != 'none':
                cur.execute("SELECT * FROM locations WHERE POSITION(%s IN LOWER(name)) > 0 AND POSITION(%s IN LOWER(address)) > 0 UNION ALL SELECT * FROM waiting WHERE POSITION(%s IN LOWER(name)) > 0 AND POSITION(%s IN LOWER(address)) > 0;",(name,address,name,address))
            else:
                cur.execute("SELECT * FROM locations WHERE POSITION(%s IN LOWER(name)) > 0 UNION ALL SELECT * FROM waiting WHERE POSITION(%s IN LOWER(name)) > 0;",(name,name))
    else:
        if category != 'none':
            if address != 'none':
                cur.execute("SELECT * FROM locations WHERE category = %s AND POSITION(%s IN LOWER(address)) > 0 UNION ALL SELECT * FROM waiting WHERE category = %s AND POSITION(%s IN LOWER(address)) > 0;",(category,address,category,address))
            else:
                cur.execute("SELECT * FROM locations WHERE category = %s UNION ALL SELECT * FROM waiting WHERE category = %s;",(category,category))
        else:
            if address != 'none':
                cur.execute("SELECT * FROM locations WHERE POSITION(%s in LOWER(address)) > 0 UNION ALL SELECT * FROM waiting WHERE POSITION(%s in LOWER(address)) > 0;",(address,address))
            else:
                cur.execute("SELECT * FROM locations UNION ALL SELECT * FROM waiting;")
    results = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

    if 'application/json' in content_type:
        req.content_type = 'application/json; charset=utf-8'
        req.write(tojson(results))
    elif 'application/xml' in content_type:
        req.content_type = 'application/xml; charset=utf-8'
        req.write(toxml(results))
    elif 'text/csv' in content_type:
        req.content_type = 'text/cvs; charset=utf-8'
        req.write(tocsv(results))
    else:
        req.content_type = 'text/plain; charset=utf-8'
        req.write(toplain(results))

    req.status = A.OK
    raise A.SERVER_RETURN, A.DONE

