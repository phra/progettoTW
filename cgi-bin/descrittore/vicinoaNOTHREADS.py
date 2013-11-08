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
from xml.dom.minidom import parse, parseString
from encoding import smart_str
from operator import itemgetter as IG
import json, urllib2, math, csv, tempfile, codecs, rdflib, rdfextras


def toplain(listout):
	s = '\n'.join('RESULT|||V') + '\n'
	for tupla in listout:
		s += 'ID: ' + smart_str(tupla[0]) + ', LAT: ' + smart_str(tupla[1]) + ', LONG: ' + smart_str(tupla[2]) + ', DISTANZA: ' + smart_str(tupla[11]) + '.\n'
	return s
def tojson(listout):
	dictoutjson = {}
	dictout = {}
	meta = [('creator', 'Working Group LTW 2011/2012'), ('created', '20/12/2011'), ('version', '1.1'), ('source', 'http://vitali.web.cs.unibo.it/TechWeb12/Formati'),('valid', '31/12/2011')]
	metadata = dict(meta)
	for t in listout:
		dictout[t[0]] = {'lat': t[1], 'long': t[2], 'category': smart_str(t[3]), 'name': t[4], 'opening': t[5], 'closing': t[6], 'address': t[7], 'tel': t[8], 'subcategory': t[9], 'note': t[10], 'distance': t[11]}
	dictoutjson['metadata'] = metadata
	dictoutjson['locations'] = dictout
	return json.dumps(dictoutjson)

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
	for t in listout:
		s += '''<location id="%s" lat="%s" long="%s">
		<category> %s </category>
		<subcategory> %s </subcategory>
		<name> %s </name>
		<address> %s </address>
		<tel> %s </tel>
		<opening> %s </opening>
		<closing> %s </closing>
		</location>''' % (smart_str([0]),smart_str(t[1]),smart_str(t[2]),smart_str(t[3]),smart_str(t[9]),smart_str(t[4]),smart_str(t[7]),smart_str(t[8]),smart_str(t[5]),smart_str(t[6]))
	s += '</locations>'
	return s

def tocsv(listout):
	s = '"id","category","name","address","lat","long","subcategory","note","opening","closing"'
	for t in listout:
		s += '"%s","%s","%s","%s","%s","%s","%s","%s","%s,"%s","%s","%s","%s","%s","%s","Working Group LTW 2011/2012","2011-12-20","2012-10-01","1.1","Unknown"\r\n' % (t[0],t[3],t[4],t[7],t[1],t[2],t[9],t[10],t[5],t[6])
	return s

def tottl(listout):
	s = '''@prefix : <http://www.essepuntato.it/resource/> .
@prefix cs: <http://cs.unibo.it/ontology/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix vcard: <http://www.w3.org/2006/vcard/ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix this: <http://vitali.web.cs.unibo.it/twiki/pub/TechWeb12/DataSource2/posteBO2011.ttl> .

this:metadata
	 dcterms:creator "Working Group LTW 2011/2012"
	; dcterms:created "2011-12-20"^^xsd:date
	; dcterms:description "1.2"
	; dcterms:valid "2011-02-21"^^xsd:date
	; dcterms:source "http://www.aziendedibologna.it/poste_bologna_e_provincia.htm".
'''
	for id, value in dictout.items():
		s += ''':%s cs:closing "%s";
		cs:opening "%s";
		vcard:category "%s";
		vcard:extended-address "%s";
		vcard:fax "%s";
		vcard:fn "%s";
		vcard:latitude "%s";
		vcard:longitude "%s";
		vcard:tel "%s" .
''' % (value['id'], value['closing'], value['opening'], value['category'], value['address'], value['fax'], value['name'], value['lat'], value['long'], value['tel'])
	return s
def index(req):

	if not (('application/json' in req.headers_in['Accept']) or ('application/xml' in req.headers_in['Accept']) or ('text/csv' in req.headers_in['Accept']) or ('text/turtle' in req.headers_in['Accept']) or ('text/x-python' in req.headers_in['Accept'])):
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

	#req.write("let's try!\r\n")+
	try:
		parms = util.FieldStorage(req)
		AGGRs = smart_str(parms.getfirst('aggr')).split('/')
		latA = float(parms.getfirst('lat'))
		lonA = float(parms.getfirst('long'))
		MAX = smart_str(parms.getfirst('max')).lower()
		DISTANZA = smart_str(parms.getfirst('distance')).lower()
		CATEGORY = smart_str(parms.getfirst('category')).lower()
	except:
		req.status = A.HTTP_NOT_ACCEPTABLE
		req.write('406: NOT ACCEPTABLE\r\n')
		req.write('parametri errati.')
		req.write('i parametri sono: lat: %s, long: %s[, max: %s, distance: %s]\r\nex: http://fattanza.no-ip.org/progettoTW/vicinoa/ltw1129-farmacie/params/44.500456/11.277643/10/5000\r\n' % (smart_str(parms.getfirst('lat')), smart_str(parms.getfirst('long')), smart_str(parms.getfirst('max')), smart_str(parms.getfirst('distance'))))
		raise A.SERVER_RETURN, A.DONE
	#req.write(AGGR)
	listout = []
	hosts = []
	host = 'http://vitali.web.cs.unibo.it/twiki/pub/TechWeb12/MetaCatalogo1112/metaCatalogo.xml'
	reqq = urllib2.Request(host)
	reqq.add_header('Accept', 'application/xml')
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
		req.write('%s non raggiungibile. (errore: %d)\r\n' % (host,e.args[0]))
		raise A.SERVER_RETURN, A.DONE
	data = r.read()
	dom = parseString(smart_str(data))
	root = dom.getElementsByTagName('metaCatalogo')[0]
	catas = root.getElementsByTagName('catalogo')
	for AGGR in AGGRs:
		for cata in catas:
			if smart_str(cata.getAttribute('id')).lower() in smart_str(AGGR).lower():
				host = smart_str(cata.getAttribute('url'))
				reqq = urllib2.Request(host)
				reqq.add_header('Accept', 'application/xml')
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
					req.write('%s non raggiungibile. (errore: %d)\r\n' % (host,e.args[0]))
					raise A.SERVER_RETURN, A.DONE
				catalogo = r.read()
				dom = parseString(smart_str(catalogo))
				root = dom.getElementsByTagName('catalogo')[0]
				foo = root.getElementsByTagName('aggregatori')[0]
				aggrs = foo.getElementsByTagName('aggregatore')
				for aggr in aggrs:
					if smart_str(aggr.getAttribute('id')).lower() == smart_str(AGGR).lower():
						url = smart_str(aggr.getAttribute('url'))
						hosts.append(url)

	RT = 6372795.477598
	radlatA = latA * (math.pi / 180.0)
	radlonA = lonA * (math.pi / 180.0)

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
			req.write('%s non raggiungibile. (errore: %d)\r\n' % (host,e.args[0]))
			raise A.SERVER_RETURN, A.DONE


		if 'application/json' in smart_str(r.info().getheader('Content-Type')):
			data = smart_str(r.read())
			dump = json.loads(data)
			locations = dump['locations']
			metadata = dump['metadata']

			for id, value in locations.items():
				latB = float(value['lat'])
				lonB = float(value['long'])
				category = smart_str(value['category']).lower()
				radlatB = latB * (math.pi / 180.0)
				radlonB = lonB * (math.pi / 180.0)
				a = RT * math.acos(math.sin(radlatA) * math.sin(radlatB) + math.cos(radlatA) * math.cos(radlatB) * math.cos(radlonA - radlonB))
				#req.write("la distanza di %s e' di: %f \r\n" % (id,a))

				if DISTANZA == 'none':
					if category == CATEGORY or CATEGORY == '*' or CATEGORY == 'none':
						lat = smart_str(value['lat'])
						long = smart_str(value['long'])
						category = smart_str(value['category'])
						name = smart_str(value['name'])
						opening = smart_str(value['opening'])
						closing = smart_str(value['closing'])
						tel = smart_str(value['tel'])
						address = smart_str(value['address'])
						listout.append((id, lat, long, category, name, opening, closing, address, tel, '', '', a))
						#req.write(repr(tupla)+'\r\n')
				else:
					if (a < float(DISTANZA)):
						if category == CATEGORY or CATEGORY == '*' or CATEGORY == 'none':
							lat = smart_str(value['lat'])
							long = smart_str(value['long'])
							category = smart_str(value['category'])
							name = smart_str(value['name'])
							opening = smart_str(value['opening'])
							closing = smart_str(value['closing'])
							tel = smart_str(value['tel'])
							address = smart_str(value['address'])
							listout.append((id, lat, long, category, name, opening, closing, address, tel, '', '', a))


		elif 'application/xml' in smart_str(r.info().getheader('Content-Type')):
			data = r.read()
			dom = parseString(smart_str(data))
			root = dom.getElementsByTagName('locations')[0]
			metadata = root.getElementsByTagName('metadata')[0]
			locations = dom.getElementsByTagName('location')

			for location in locations:
				category = smart_str(location.getElementsByTagName('category')[0]).lower()
				id = smart_str(location.getAttribute('id')).lower()
				latB = float(location.getAttribute('lat'))
				lonB = float(location.getAttribute('long'))
				radlatB = latB * (math.pi / 180.0)
				radlonB = lonB * (math.pi / 180.0)
				a = RT * math.acos(math.sin(radlatA) * math.sin(radlatB) + math.cos(radlatA) * math.cos(radlatB) * math.cos(radlonA - radlonB))

				if DISTANZA == 'none':
					if category == CATEGORY or CATEGORY == '*' or CATEGORY == 'none':
						lat = smart_str(location.getAttribute('lat'))
						long = smart_str(location.getAttribute('long'))
						category = smart_str(location.getElementsByTagName('category')[0].childNodes[0].data)
						name = smart_str(location.getElementsByTagName('name')[0].childNodes[0].data)
						address = smart_str(location.getElementsByTagName('address')[0].childNodes[0].data)
						closing = smart_str(location.getElementsByTagName('closing')[0].childNodes[0].data)
						category = smart_str(location.getElementsByTagName('category')[0].childNodes[0].data)
						subcategory = smart_str(location.getElementsByTagName('subcategory')[0].childNodes[0].data)
						tel = smart_str(location.getElementsByTagName('tel')[0].childNodes[0].data)
						opening = ''
						for open in location.getElementsByTagName('opening')[0].childNodes:
							opening += open.data + ' '

						listout.append((id, lat, long, category, name, opening, closing, address, tel, subcategory, '', a))
				else:
					if (a < float(DISTANZA)):
						if category == CATEGORY or CATEGORY == '*' or CATEGORY == 'none':
							lat = smart_str(location.getAttribute('lat'))
							long = smart_str(location.getAttribute('long'))
							category = smart_str(location.getElementsByTagName('category')[0].childNodes[0].data)
							name = smart_str(location.getElementsByTagName('name')[0].childNodes[0].data)
							address = smart_str(location.getElementsByTagName('address')[0].childNodes[0].data)
							closing = smart_str(location.getElementsByTagName('closing')[0].childNodes[0].data)
							category = smart_str(location.getElementsByTagName('category')[0].childNodes[0].data)
							subcategory = smart_str(location.getElementsByTagName('subcategory')[0].childNodes[0].data)
							tel = smart_str(location.getElementsByTagName('tel')[0].childNodes[0].data)
							opening = ''
							for open in location.getElementsByTagName('opening')[0].childNodes:
								opening += open.data + ' '

							listout.append((id, lat, long, category, name, opening, closing, address, tel, subcategory, '', a))

		elif 'text/csv' in smart_str(r.info().getheader('Content-Type')):
			data = r.read()
			temp = tempfile.TemporaryFile()
			temp.write(smart_str(data))
			enc = 'utf-8'
			temp.seek(0)
			temp.readline()
			attrs = ["id","category","name","address","lat","long","subcategory","note","opening","closing","creator","created","valid","version","source"]
			dump = csv.DictReader(temp, attrs, lineterminator='\n')
			for line in dump:
				id = smart_str(line['id']).lower()
				latB = float(line['lat'])
				lonB = float(line['long'])
				radlatB = latB * (math.pi / 180.0)
				radlonB = lonB * (math.pi / 180.0)
				a = RT * math.acos(math.sin(radlatA) * math.sin(radlatB) + math.cos(radlatA) * math.cos(radlatB) * math.cos(radlonA - radlonB))

				if DISTANZA == 'none':
					if smart_str(line['category']).lower() == CATEGORY or CATEGORY == '*' or CATEGORY == 'none':
						lat = smart_str(line['lat'])
						long = smart_str(line['long'])
						category = smart_str(line['category'])
						name = smart_str(line['name'])
						opening = smart_str(line['opening'])
						closing = smart_str(line['closing'])
						tel = ''
						address = smart_str(line['address'])

						listout.append((id, lat, long, category, name, opening, closing, address, tel, '', '', a))
				else:
					if (a < float(DISTANZA)):
						if smart_str(line['category']).lower() == CATEGORY or CATEGORY == '*' or CATEGORY == 'none':
							lat = smart_str(line['lat'])
							long = smart_str(line['long'])
							category = smart_str(line['category'])
							name = smart_str(line['name'])
							opening = smart_str(line['opening'])
							closing = smart_str(line['closing'])
							tel = ''
							address = smart_str(line['address'])

							listout.append((id, lat, long, category, name, opening, closing, address, tel,'', '', a))
			temp.close()

		elif 'text/turtle' in smart_str(r.info().getheader('Content-Type')):
			graph = rdflib.Graph()
			dump = graph.parse(r, format='n3')
			rdflib.plugin.register('sparql', rdflib.query.Processor, 'rdfextras.sparql.processor', 'Processor')
			rdflib.plugin.register('sparql', rdflib.query.Result, 'rdfextras.sparql.query', 'SPARQLQueryResult')
			foo = dump.query("""
						 PREFIX vcard: <http://www.w3.org/2006/vcard/ns#>
						 PREFIX cs: <http://cs.unibo.it/ontology/>
						 PREFIX : <http://www.essepuntato.it/resource/>

						 SELECT ?x ?fn ?latitude ?longitude ?tel ?category ?fax ?opening ?closing ?address
						 WHERE {

						     ?x vcard:fn ?fn ;
							vcard:latitude ?latitude ;
							vcard:longitude ?longitude ;
							vcard:category ?category ;
							vcard:tel ?tel ;
							vcard:fax ?fax ;
							vcard:extended-address ?address ;
							cs:opening ?opening ;
							cs:closing ?closing .
						 }
				""")

			for each in foo.topUnion:
				id = smart_str(each['x']).split('/')[4]
				radlatB = float(smart_str(each['latitude'])) * (math.pi / 180.0)
				radlonB = float(smart_str(each['longitude'])) * (math.pi / 180.0)
				a = RT * math.acos(math.sin(radlatA) * math.sin(radlatB) + math.cos(radlatA) * math.cos(radlatB) * math.cos(radlonA - radlonB))
				if DISTANZA == 'none':
					if smart_str(each['category']).lower() == CATEGORY or CATEGORY == '*' or CATEGORY == 'none':
						temp = {}
						id = smart_str(each['x']).split('/')[4]
						lat = smart_str(each['latitude'])
						long = smart_str(each['longitude'])
						tel = smart_str(each['tel'])
						name = smart_str(each['fn'])
						address = smart_str(each['address'])
						category = smart_str(each['category'])
						fax = smart_str(each['fax'])
						opening = smart_str(each['opening'])
						closing = smart_str(each['closing'])
						listout.append((id, lat, long, category, name, opening, closing, address, tel, '', '', a))
				elif a < DISTANZA:
					if smart_str(each['category']).lower() == CATEGORY or CATEGORY == '*' or CATEGORY == 'none':
						temp = {}
						id = smart_str(each['x']).split('/')[4]
						lat = smart_str(each['latitude'])
						long = smart_str(each['longitude'])
						tel = smart_str(each['tel'])
						name = smart_str(each['fn'])
						address = smart_str(each['address'])
						category = smart_str(each['category'])
						fax = smart_str(each['fax'])
						opening = smart_str(each['opening'])
						closing = smart_str(each['closing'])
						listout.append((id, lat, long, category, name, opening, closing, address, tel, '', '', a))

		else:
			req.write('501: Internal Server Error\n')
			req.write("l'aggregatore %s vuole fornire dati in %s, non compatibile con il protocollo." % (host, smart_str(r.info().getheader('Content-Type'))))
			req.status = A.HTTP_INTERNAL_SERVER_ERROR
			raise A.SERVER_RETURN, A.DONE

	if MAX != 'none':
		listout.sort(key=IG(11))
		del(listout[int(MAX):])

	if 'application/json' in content_type:
		req.content_type = 'application/json; charset=utf-8'
		req.write(tojson(listout))
	elif 'application/xml' in content_type:
		req.content_type = 'application/xml; charset=utf-8'
		req.write(toxml(listout))
	elif 'text/csv' in content_type:
		req.content_type = 'text/cvs; charset=utf-8'
		req.write(tocsv(listout))
	elif 'text/turtle' in content_type:
		req.content_type = 'text/turtle; charset=utf-8'
		req.write(tottl(listout))
	else:
		req.content_type = 'text/plain; charset=utf-8'
		req.write(toplain(listout))

	req.status = A.OK
	raise A.SERVER_RETURN, A.DONE

