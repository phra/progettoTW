#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       aggregatoreJSON v1.0
#
#       Copyright 2011 indieCODE <fattanza.no-ip.org/progettoTW>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#


from encoding import smart_str
import codecs, json, urllib2

output = ""
hosts = ["ltw1129-palestrern", "ltw1129-super", "ltw1129-superrn", "ltw1129-farmacie", "ltw-1129-farmaciern", "ltw1129-scuole", "ltw1129-scuolern", "ltw1129-poste", "ltw1129-postern", "ltw1130-agg_banche", "ltw1140-museibo2011"]

for host in hosts:

    reqq = urllib2.Request("http://fattanza.no-ip.org/progettoTW/vicinoa/" + host  + "/params/40/10/")
    reqq.add_header('Accept', 'application/json')

    try:
        r = urllib2.urlopen(reqq)
        dump = json.loads(r.read())
        r.close()
        locations = dump['locations']
        metadata = dump['metadata']
    except urllib2.HTTPError, e:
        print("HTTPERROR")
        exit(1)
    except urllib2.URLError, e:
        print("URLERROR")
        exit(1)

    for id,value in locations.items():
        category = smart_str(value['category'])
        name = smart_str(value['name'])
        address = smart_str(value['address'])
        lat = smart_str(value['lat'])
        long = smart_str(value['long'])
        opening = smart_str(value['opening'])
        closing = smart_str(value['closing'])
        tel = smart_str(value['tel'])
        output += "INSERT INTO locations(name,category,address,latitude,longitude,opening,closing,tel) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s');\n" % (name, category,address,lat,long,opening,closing,tel)

print output
