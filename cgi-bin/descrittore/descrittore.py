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

    try:
        parms = util.FieldStorage(req)
        AGGRs = smart_str(parms.getfirst('aggr')).split('/')
        latA = float(parms.getfirst('lat'))
        lonA = float(parms.getfirst('long'))
        MAX = smart_str(parms.getfirst('max')).lower()
        DISTANZA = smart_str(parms.getfirst('distance')).lower()
    except:
        req.status = A.HTTP_NOT_ACCEPTABLE
        req.write('406: NOT ACCEPTABLE\r\n')
        req.write('parametri errati.')
        req.write('i parametri sono: lat: %s, long: %s[, max: %s, distance: %s]\r\nex: http://fattanza.no-ip.org/progettoTW/vicinoa/ltw1130-farmacie/params/44.500456/11.277643/10/5000\r\n' % (smart_str(parms.getfirst('lat')), smart_str(parms.getfirst('long')), smart_str(parms.getfirst('max')), smart_str(parms.getfirst('distance'))))
        raise A.SERVER_RETURN, A.DONE


#	radlatA = latA * (math.pi / 180.0)
#	radlonA = lonA * (math.pi / 180.0)
#	radlatB = latB * (math.pi / 180.0)
#	radlonB = lonB * (math.pi / 180.0)
#	a = RT * math.acos(math.sin(radlatA) * math.sin(radlatB) + math.cos(radlatA) * math.cos(radlatB) * math.cos(radlonA - radlonB))
#	listout.append((id, lat, long, category, name, opening, closing, address, tel, '', '', a))

SELECT *, 
FROM locations a
WHERE (
	6372 * acos(cos(radians(a.latitude)) * cos(radians(11) ) * 
	cos(radians(40) - radians(a.longitude)) + sin(radians(a.latitude)) * sin(radians(11)))
) < 1000
ORDER BY distance
LIMIT 10;



	flag = 0
	query = "SELECT * FROM locations a WHERE ("

	for aggr in AGGRs:
		if flag == 0:
			flag = 1
			query += "x.category = %s"
		query += " OR x.category = %s"

	query += ") "
	if DISTANZA != 'none':
		query += "AND (	6372 * acos(cos(radians(a.latitude)) * cos(radians(%s) ) * 	cos(radians(%s) - radians(a.longitude)) + sin(radians(a.latitude)) * sin(radians(%s)))) < 1000 " 
	if MAX != 'none':
		query += "LIMIT %s"
	query += ";"

    conn = psycopg2.connect("dbname='trovatutto' user='admin' password='admin'")
    cur = conn.cursor()
    AGGRs += (latA,lonA,latA,DISTANZA,MAX)
    cur.execute(query,AGGRs)
    results = cur.fetchall()
    req.write(tojson(results))
    conn.commit()
    cur.close()
    conn.close()
    raise A.SERVER_RETURN, A.DONE

    if 'application/json' in content_type:
        req.content_type = 'application/json; charset=utf-8'
        req.write(tojson(listout))
    elif 'application/xml' in content_type:
        req.content_type = 'application/xml; charset=utf-8'
        req.write(toxml(results))
    elif 'text/csv' in content_type:
        req.content_type = 'text/cvs; charset=utf-8'
        req.write(tocsv(listout))
    else:
        req.content_type = 'text/plain; charset=utf-8'
        req.write(toplain(listout))

    req.status = A.OK
    raise A.SERVER_RETURN, A.DONE

