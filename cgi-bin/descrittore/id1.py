#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  id.py
#
#  Copyright 2011 indieCODE <fattanza.no-ip.org/progettoTW>
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
from encoding import smart_str
from mod_python import apache as A, util
from xml.dom.minidom import parse, parseString
import json, urllib2, csv, tempfile, codecs, rdflib, rdfextras, threading

def toplain(dictout):
	s = '\n'.join('RESULT|||V')
	for id, value in dictout.items():
		s += 'ID: ' + id + ', LAT: ' + value['lat'] + ', LONG: ' + value['long'] + ', CATEGORY: ' + value['category'] + '.\n'
	return s

def tohtml(dictout):
	s = ''
	for id, value in dictout.items():
	#	s += '<h2>%s</h2>' % id
		s += '<p id="infoParam">%s</p> <p id="infoParam1">%s</p>' % (value['name'], value['address'])
	s += ''
	return s

def tojson(dictout):
	dictoutjson = {}
	meta = [('creator', 'Working Group LTW 2011/2012'), ('created', '20/12/2011'), ('version', '1.1'), ('source', 'http://vitali.web.cs.unibo.it/TechWeb12/Formati'),('valid', '31/12/2011')]
	metadata = dict(meta)
	dictoutjson['metadata'] = metadata
	dictoutjson['locations'] = dictout
	return json.dumps(dictoutjson)

def toxml(dictout):
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
	for id, value in dictout.items():
		s += '''<location id="%s" lat="%s" long="%s">
		<category> %s </category>
		<subcategory> %s </subcategory>
		<name> %s </name>
		<address> %s </address>
		<tel> %s </tel>
		<opening> %s </opening>
		<closing> %s </closing>
		</location>''' % (id,value['lat'],value['long'],value['category'], value['subcategory'], value['name'], value['address'], value['tel'], value['opening'], value['closing'])
	s += '</locations>'
	return s

def tocsv(dictout):
	s = '"id","category","name","address","lat","long","subcategory","note","opening","closing"'
	for id, value in dictout.items():
		s += '"%s","%s","%s","%s","%s","%s","%s","%s","%s,"%s","%s","%s","%s","%s","%s","Working Group LTW 2011/2012","2011-12-20","2012-10-01","1.1","Unknown"\r\n' % (id,value['category'],value['name'],value['address'], value['lat'], value['long'], value['subcategory'], value['note'], value['opening'], value['closing'])
	return s

def tottl(dictout):
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


def piglia(req,IDs,host,dictout,lock):
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
			for ID in IDs:
				if smart_str(id).lower() == smart_str(ID).lower():
					lat = smart_str(value['lat'])
					long = smart_str(value['long'])
					category = smart_str(value['category'])
					name = smart_str(value['name'])
					opening = smart_str(value['opening'])
					closing = smart_str(value['closing'])
					tel = smart_str(value['tel'])
					address = smart_str(value['address'])
					with lock:
						dictout[id] = {
							'lat': lat,
							'long': long,
							'category': category,
							'subcategory': '',
							'note': '',
							'name': name,
							'opening': opening,
							'closing': closing,
							'address': address,
							'tel': tel,
							}


	elif 'application/xml' in smart_str(r.info().getheader('Content-Type')):
		data = r.read()
		dom = parseString(smart_str(data))
		root = dom.getElementsByTagName('locations')[0]
		metadata = root.getElementsByTagName('metadata')[0]
		locations = dom.getElementsByTagName('location')

		for location in locations:
			id = smart_str(location.getAttribute('id'))
			for ID in IDs:
				if smart_str(id).lower() == smart_str(ID).lower():
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
					with lock:
						dictout[id] = {
							'lat': lat,
							'long': long,
							'category' : category,
							'name': name,
							'opening': opening,
							'closing': closing,
							'address': address,
							'tel': tel,
							'subcategory': subcategory,
							'note': ''
							}

	elif 'text/csv' in smart_str(r.info().getheader('Content-Type')):
		data = r.read()
		temp = tempfile.TemporaryFile()
		temp.write(smart_str(data))
		enc = 'utf-8'
		#fd = codecs.open(temp,'r',enc)
		temp.seek(0)
		temp.readline()
		attrs = ["id","category","name","address","lat","long","subcategory","note","opening","closing","creator","created","valid","version","source"]
		dump = csv.DictReader(temp, attrs, lineterminator='\n')
		for line in dump:
			for ID in IDs:
				id = smart_str(line['id'])
				if smart_str(id).lower() == smart_str(ID).lower():
					lat = smart_str(line['lat'])
					long = smart_str(line['long'])
					category = smart_str(line['category'])
					subcategory = ''.join(smart_str(line['subcategory']))
					name = smart_str(line['name'])
					opening = smart_str(line['opening'])
					closing = smart_str(line['closing'])
					address = smart_str(line['address'])
					creator = smart_str(line['creator'])
					created = smart_str(line['created'])
					valid = smart_str(line['valid'])
					version = smart_str(line['version'])
					source = smart_str(line['source'])
					with lock:
						dictout[id] = {
							'lat': lat,
							'long': long,
							'category' : category,
							'name': name,
							'opening': opening,
							'closing': closing,
							'address': address,
							'tel': '',
							'subcategory': subcategory,
							'note': ''
							}
		#req.write('prova\n')
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
			for ID in IDs:
				if smart_str(each['x']).split('/')[4].lower() == smart_str(ID).lower():
					temp = {}
					temp['id'] = id = smart_str(each['x']).split('/')[4]
					temp['lat'] = smart_str(each['latitude'])
					temp['long'] = smart_str(each['longitude'])
					temp['tel'] = smart_str(each['tel'])
					temp['name'] = smart_str(each['fn'])
					temp['address'] = smart_str(each['address'])
					temp['category'] = smart_str(each['category'])
					temp['fax'] = smart_str(each['fax'])
					temp['opening'] = smart_str(each['opening'])
					temp['closing'] = smart_str(each['closing'])
					temp['subcategory'] = ''
					temp['note'] = ''
					with lock:
						dictout[id] = temp
	else:
		req.write('500: Internal Server Error\n')
		req.write("l'aggregatore %s vuole fornire dati in %s, non compatibile con il protocollo." % (host, smart_str(r.info().getheader('Content-Type'))))
		req.status = A.HTTP_INTERNAL_SERVER_ERROR
		raise A.SERVER_RETURN, A.DONE


def index(req):

	if not (('application/json' in req.headers_in['Accept']) or ('application/xml' in req.headers_in['Accept']) or ('text/csv' in req.headers_in['Accept']) or ('text/turtle' in req.headers_in['Accept']) or ('text/html' in req.headers_in['Accept'])):
		req.content_type = 'text/plain; charset="UTF-8"'
		req.status = A.HTTP_NOT_ACCEPTABLE
		req.write('406: NOT ACCEPTABLE\r\n')
		req.write('intersezione tra content-type vuota.\r\n')
		raise A.SERVER_RETURN, A.DONE

	accept = req.headers_in['Accept']
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
		IDs = smart_str(parms.getfirst('id')).split('/')
	except:
		req.status = A.HTTP_NOT_ACCEPTABLE
		req.write('406: NOT ACCEPTABLE\r\n')
		req.write('parametri errati.')
		raise A.SERVER_RETURN, A.DONE
	#req.write(AGGR)
	dictout = {}
	hosts = []
	host = 'http://fattanza.no-ip.org/progettoTW/metacatalogo'
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
						url = smart_str(aggr.getAttribute('url')).lower()
						hosts.append(url)

	threads = []
	lock = threading.Lock()
	for host in hosts:
		t = threading.Thread(target=piglia,args=(req,IDs,host,dictout,lock))
		t.start()
		threads.append(t)
	for t in threads:
		threading.Thread.join(t)

	if 'text/html' in accept:
		req.content_type = 'text/html; charset="UTF-8"'
		req.write(tohtml(dictout))
	elif 'application/json' in accept:
		req.content_type = 'application/json; charset="UTF-8"'
		req.write(tojson(dictout))
	elif 'application/xml' in accept:
		req.content_type = 'application/xml; charset="UTF-8"'
		req.write(toxml(dictout))
	elif 'text/csv' in accept:
		req.content_type = 'text/cvs; charset="UTF-8"'
		req.write(tocsv(dictout))
	elif 'text/turtle' in accept:
		req.content_type = 'text/turtle; charset="UTF-8"'
		req.write(tottl(dictout))
	else:
		req.content_type = 'text/plain; charset="UTF-8"'
		req.write(toplain(dictout))

	req.status = A.OK
	raise A.SERVER_RETURN, A.DONE

