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

from mod_python import apache as A, util
from xml.dom.minidom import parse, parseString
from encoding import smart_str
from operator import itemgetter as IG
import json, urllib2, math


def tojson(listout):
	listoutjson = {}
	#meta = [('creator', 'Working Group LTW 2011/2012'), ('created', '20/12/2011'), ('version', '1.1'), ('source', 'http://vitali.web.cs.unibo.it/TechWeb12/Formati'),('valid', '31/12/2011')]
	metadata = dict(meta)
	distance = {}

	listoutjson['distance'] = listout
	#listoutjson['metadata'] = metadata
	return json.dumps(listoutjson)
	
def toxml(listout):
	return '''<?xml version="1.0" encoding="UTF-8"?>
<distance>%s</distance>

''' % listout
	
def tocsv(listout):
	return 'distance"\r\n%s' % listout

def toplain(listout):
	return ''.join(listout)
	
	
	
def index(req):
	
	if not (('application/json' in req.content_type) or ('application/xml' in req.content_type) or ('text/csv' in req.content_type) or ('text/turtle' in req.content_type) or ('text/x-python' in req.content_type)):
		req.content_type = 'text/plain'
		req.headers_out.add("Access-Control-Allow-Origin","*")
		req.status = A.HTTP_NOT_ACCEPTABLE
		req.write('406: NOT ACCEPTABLE\r\n')
		req.write('intersezione tra content-type vuota.\r\n')
		raise A.SERVER_RETURN, A.DONE
	
	content_type = ''.join(req.content_type)
	req.content_type = 'text/plain; charset="UTF-8"'
	req.headers_out.add("Access-Control-Allow-Origin","*")
	
	if req.method != 'GET':
		req.status = A.HTTP_METHOD_NOT_ALLOWED
		req.write('405: METHOD NOT ALLOWED\r\n')
		req.write('metodo %s non permesso.\r\n' % req.method)
		raise A.SERVER_RETURN, A.DONE

	try:
		parms = util.FieldStorage(req)
		AGGR = parms.getlist('aggr')
		latA = float(parms.getfirst('lat1'))
		lonA = float(parms.getfirst('long1'))
		latB = float(parms.getfirst('lat2'))
		lonB = float(parms.getfirst('long2'))
	except:
		req.status = A.HTTP_NOT_ACCEPTABLE
		req.write('406: NOT ACCEPTABLE\r\n')
		req.write('parametri errati.')
		req.write('i parametri sono: %s %s %s\r\n\r\n' % (parms.getfirst('lat'), parms.getfirst('long'), latA))
		raise A.SERVER_RETURN, A.DONE

	
	RT = 6372795.477598
	radlatA = latA * (math.pi / 180.0)
	radlonA = lonA * (math.pi / 180.0)
	radlatB = latB * (math.pi / 180.0)
	radlonB = lonB * (math.pi / 180.0)
	a = RT * math.acos(math.sin(radlatA) * math.sin(radlatB) + math.cos(radlatA) * math.cos(radlatB) * math.cos(radlonA - radlonB))
	#req.write(smart_str(a))
	#raise A.SERVER_RETURN, A.DONE

	
	if 'application/json' in content_type:
		req.content_type = 'application/json; charset="UTF-8"'
		req.write(tojson(a))
	elif 'application/xml' in content_type:
		req.content_type = 'application/xml; charset="UTF-8"'
		req.write(toxml(a))
	elif 'text/csv' in content_type:
		req.content_type = 'text/cvs; charset="UTF-8"'
		req.write(tocsv(a))
	else:
		req.content_type = 'text/plain; charset="UTF-8"'
		req.write(toplain(a))
	
	req.status = A.OK
	raise A.SERVER_RETURN, A.DONE

