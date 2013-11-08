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
	meta = [('creator', 'Working Group LTW 2011/2012'), ('created', '20/12/2011'), ('version', '1.1'), ('source', 'http://vitali.web.cs.unibo.it/TechWeb12/Formati'),('valid', '31/12/2011')]
	metadata = dict(meta)
	locations = {}
	for tupla in listout:		
		item = {}
		item['lat'] = tupla[1]
		item['long'] = tupla[2]
		item['distance'] = tupla[3]
		locations[tupla[0]] = item
	listoutjson['locations'] = locations
	listoutjson['metadata'] = metadata
	return json.dumps(listoutjson)
	
def toxml(listout):
	s = '''<?xml version="1.0" encoding="UTF-8"?>
<locations>
	<metadata>
		<creator>Working Group LTW 2011/2012</creator>
		<created>12/20/2011</created>
		<version>1.2</version>
		<source>http://vitali.web.cs.unibo.it/TechWeb12/Formati</source>
		<valid>02/21/2011</valid>
		<note>Le date sono in formato americano: MM/GG/AAAA</note>
	</metadata>
'''
	for tupla in listout:
		s += '''<location id="%s" lat="%s" long="%s">
<distance>%s</distance>
</location>''' % (tupla[0],tupla[1],tupla[2],tupla[3])
	s += '</locations>'
	return s
	
def tocsv(listout):
	s = '"Id","Lat","Long","distance"'
	for tupla in listout:
		s += '"%s","%s","%s","%s"\r\n' % (tupla[0],tupla[1],tupla[2],tupla[3])
	return s
	
def handler(req):
	
	if not (('application/json' in req.content_type) or ('application/xml' in req.content_type) or ('text/csv' in req.content_type) or ('text/turtle' in req.content_type) or ('text/x-python' in req.content_type)):
		req.content_type = 'text/plain'
		req.status = A.HTTP_NOT_ACCEPTABLE
		req.write('406: NOT ACCEPTABLE\r\n')
		req.write('intersezione tra content-type vuota.\r\n')
		raise A.SERVER_RETURN, A.DONE
	
	content_type = ''.join(req.content_type)
	req.content_type = 'text/plain'
	
	if req.method != 'GET':
		req.status = A.HTTP_METHOD_NOT_ALLOWED
		req.write('405: METHOD NOT ALLOWED\r\n')
		req.write('metodo %s non permesso.\r\n' % req.method)
		raise A.SERVER_RETURN, A.DONE

	#req.write("let's try!\r\n")+
	try:
		parms = util.FieldStorage(req)
		AGGR = parms.getlist('aggr')
		latA = float(parms.getfirst('lat'))
		lonA = float(parms.getfirst('long'))
		MAX = smart_str(parms.getfirst('max')).lower()
		DISTANZA = smart_str(parms.getfirst('distance')).lower()
	except:
		req.status = A.HTTP_NOT_ACCEPTABLE
		req.write('406: NOT ACCEPTABLE\r\n')
		req.write('parametri errati.')
		req.write('i parametri sono: %s %s %s\r\n\r\n' % (parms.getfirst('lat'), parms.getfirst('long'), latA))
		raise A.SERVER_RETURN, A.DONE
	#req.write(AGGR)
	listout = []
	
	RT = 6372795.477598
	radlatA = latA * (math.pi / 180.0)
	radlonA = lonA * (math.pi / 180.0)
	hosts = ['http://fattanza.no-ip.org/progettoTW/aggregatore/json/aggrjson.py','http://fattanza.no-ip.org/progettoTW/aggregatore/xml/aggrxml.py']
	
	for host in hosts:
		reqq = urllib2.Request(host)
		reqq.add_header('Accept', 'text/plain application/json application/xml text/turtle text/csv text/comma-separated-values')
		try:
			r = urllib2.urlopen(reqq)
		except urllib2.HTTPError, e:
			req.status = A.HTTP_INTERNAL_SERVER_ERROR
			req.write('500: INTERNAL SERVER ERROR\r\n')
			req.write('%s non raggiungibile. (errore: %d)\r\n' % (host,e.code))
			raise A.SERVER_RETURN, A.DONE
		except urllib2.URLError, e:
			req.status = A.HTTP_INTERNAL_SERVER_ERROR
			req.write('500: INTERNAL SERVER ERROR\r\n')
			req.write('%s non raggiungibile. (errore: %d)\r\n' % (host,e.args))
			raise A.SERVER_RETURN, A.DONE
			

		if 'application/json' in smart_str(r.info().getheader('Content-Type')):
			data = r.read()
			dump = json.loads(data)
			locations = dump['locations']
			metadata = dump['metadata']

			for id, value in locations.items():
				latB = float(value['lat'])
				lonB = float(value['long'])
				radlatB = latB * (math.pi / 180.0)
				radlonB = lonB * (math.pi / 180.0)
				a = RT * math.acos(math.sin(radlatA) * math.sin(radlatB) + math.cos(radlatA) * math.cos(radlatB) * math.cos(radlonA - radlonB))
				#req.write("la distanza di %s e' di: %f \r\n" % (id,a))
		
				if DISTANZA == 'none':
					tupla = (smart_str(id) , smart_str(latB), smart_str(lonB), a)
					listout.append(tupla)
					#req.write(repr(tupla)+'\r\n')
				else:
					if (a < float(DISTANZA)):
						#del(locations[id])
						tupla = (smart_str(id) , smart_str(latB), smart_str(lonB), a)
						
						#req.write(repr(tupla))
						listout.append(tupla)
						#req.write('ID OK: %s -> latB = %f e lonB = %f (radlatB = %f, radlonB = %f) \r\n\r\n\r\n' % (id, latB,lonB,radlatB,radlonB))
					else:
						pass#req.write('ID KO: %s -> latB = %f e lonB = %f \r\n\r\n\r\n' % (id, latB,lonB))

		elif 'application/xml' in smart_str(r.info().getheader('Content-Type')):
			data = r.read()
			dom = parseString(smart_str(data))
			root = dom.getElementsByTagName('locations')[0]
			metadata = root.getElementsByTagName('metadata')[0]
			locations = dom.getElementsByTagName('location')

			for location in locations:
				id = smart_str(location.getAttribute('id'))
				latB = float(location.getAttribute('lat'))
				lonB = float(location.getAttribute('long'))
				radlatB = latB * (math.pi / 180.0)
				radlonB = lonB * (math.pi / 180.0)
				a = RT * math.acos(math.sin(radlatA) * math.sin(radlatB) + math.cos(radlatA) * math.cos(radlatB) * math.cos(radlonA - radlonB))
				#req.write("la distanza di %s e' di: %f \r\n" % (id,a))
		
				if DISTANZA == 'none':
					tupla = (smart_str(id) , smart_str(latB), smart_str(lonB), a)
					listout.append(tupla)
				else:
					if (a < float(DISTANZA)):
						#del(locations[id])
						tupla = (smart_str(id) , smart_str(latB), smart_str(lonB), a)
						#req.write(repr(tupla))
						listout.append(tupla)
						#req.write('ID OK: %s -> latB = %f e lonB = %f (radlatB = %f, radlonB = %f) \r\n\r\n\r\n' % (id, latB,lonB,radlatB,radlonB))
					else:
						pass#req.write('ID KO: %s -> latB = %f e lonB = %f \r\n\r\n\r\n' % (id, latB,lonB))
	
	if MAX == 'none':
		#req.write('asdasdasdasd')
		pass
	else:
		#req.write('asdasdasdasd')
		listout.sort(key=IG(3))
		del(listout[int(MAX):])
	
	if 'application/json' in content_type:
		req.content_type = 'application/json'
		req.write(tojson(listout))
	elif 'application/xml' in content_type or 'text/x-python' in content_type:
		req.content_type = 'application/xml'
		req.write(toxml(listout))
	elif 'text/csv' in content_type:
		req.content_type = 'text/cvs'
		req.write(tocsv(listout))
	elif 'text/turtle' in content_type:
		req.content_type = 'text/turtle'
		req.write(tottl(listout))
	else:
		req.content_type = 'text/plain'
		req.write(toplain(listout))
	
	req.status = A.OK
	raise A.SERVER_RETURN, A.DONE

