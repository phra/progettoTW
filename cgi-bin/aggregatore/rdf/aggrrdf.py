#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       aggregatoreRDF v1.0
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

import sys
sys.path.append('/var/www/progettoTW/cgi-bin/aggregatore/rdf/')
from mod_python import apache as A, util
from encoding import smart_str
import codecs, rdflib, rdfextras


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


def handler(req):

	if not (('text/turtle' in req.headers_in['Accept']) or ('application/xml' in req.headers_in['Accept'])):
		req.content_type = 'text/plain; charset=utf-8'
		req.headers_out.add("Access-Control-Allow-Origin","*")
		req.status = A.HTTP_NOT_ACCEPTABLE
		req.write('406: NOT ACCEPTABLE\r\n')
		req.write('intersezione tra content-type vuota.\r\n')
		raise A.SERVER_RETURN, A.DONE
	
	req.content_type = 'text/plain; charset=utf-8'
	req.headers_out.add("Access-Control-Allow-Origin","*")
	if req.method != 'GET':
		req.status = A.HTTP_METHOD_NOT_ALLOWED
		req.write('405: METHOD NOT ALLOWED\r\n')
		req.write('metodo %s non permesso.\r\n' % req.method)
		raise A.SERVER_RETURN, A.DONE

	#req.write("let's try!\r\n")
	try:
		path = '/var/www/progettoTW/cgi-bin/aggregatore/rdf/posteBO2011.ttl'
		enc = 'utf-8'
		fd = codecs.open(path,'r',enc)
		#fd.close()

	except IOError:
		req.status = A.HTTP_INTERNAL_SERVER_ERROR
		req.write('500: INTERNAL SERVER ERROR\r\n')
		req.write('%s non trovato\r\n' % path)
		raise A.SERVER_RETURN, A.DONE

	dictout = {}
	graph = rdflib.Graph()
	dump = graph.parse(fd, format='n3')
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
	try:
		parms = util.FieldStorage(req)		
		KEY = smart_str(parms.getfirst('key')).lower()
		COMP = smart_str(parms.getfirst('comp')).lower()
		VALUE = smart_str(parms.getfirst('value')).lower()
		if KEY == 'none' and COMP == 'none' and VALUE == 'none':
			raise Exception('foo')
		if KEY == 'none' or COMP == 'none' or VALUE == 'none':
			raise Exception('bar')
	except Exception, what:
		if what.args[0] == 'bar':
			req.status = A.HTTP_NOT_ACCEPTABLE
			req.write('406: NOT ACCEPTABLE\r\n')
			req.write('parametri insufficienti.\r\n')
			req.write('i parametri sono: %s %s %s\r\n\r\nesempio: http://fattanza.no-ip.org/progettoTW/cgi-bin/aggregatore/rdf/aggrrdf.py?key=name&comp=contains&value=5' % (KEY, COMP, VALUE))
			raise A.SERVER_RETURN, A.DONE
		if what.args[0] == 'foo':
			req.content_type = 'text/turtle'
			s = ''.join('''@prefix : <http://www.essepuntato.it/resource/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix this: <http://vitali.web.cs.unibo.it/twiki/pub/TechWeb12/DataSource2/posteBO2011.ttl> .''')
			req.write(s + smart_str(dump.serialize(format="turtle",encoding="utf-8")))	
			fd.close()		
			req.status = A.OK
			raise A.SERVER_RETURN, A.DONE
	
	
	for each in foo.topUnion:
		id = smart_str(each['x']).split('/')[4]
		temp = {}
		temp['id'] = smart_str(each['x']).split('/')[4]
		temp['lat'] = smart_str(each['latitude'])
		temp['long'] = smart_str(each['longitude'])
		temp['tel'] = smart_str(each['tel'])
		temp['name'] = smart_str(each['fn'])
		temp['address'] = smart_str(each['address'])
		temp['category'] = smart_str(each['category'])
		temp['fax'] = smart_str(each['fax'])
		temp['opening'] = smart_str(each['opening'])
		temp['closing'] = smart_str(each['closing'])
		dictout[id] = temp
	
	fd.close()
	if (KEY == 'id'):
		if (COMP == 'eq'):
			for id, value in dictout.items():
				if not VALUE in smart_str(id).lower():
					#req.write('ID OK -> %s \r\n' % id)
					del(dictout[id])
		elif (COMP == 'ne'):
			for id, value in dictout.items():
				if VALUE in smart_str(id).lower():
					#req.write('ID OK -> %s \r\n' % id)
					del(dictout[id])
		elif (COMP == 'contains'):
			for id, value in dictout.items():
				if not VALUE in smart_str(id).lower():
					#req.write('ID OK -> %s \r\n' % id)
					del(dictout[id])
		else:
			req.status = A.HTTP_NOT_ACCEPTABLE
			req.write('406: NOT ACCEPTABLE\r\n')
			req.write('parametro %s non riconosciuto.\r\n' % COMP)
			raise A.SERVER_RETURN, A.DONE
	elif (KEY == 'name' or KEY == 'lat' or KEY == 'long' or KEY == 'category' or KEY == 'address' or KEY == 'opening' or KEY == 'closing'):
		if (COMP == 'eq'):
			if(KEY == 'name' or KEY == 'lat' or KEY == 'long' or KEY == 'category'):
				for id, value in dictout.items():
					if not smart_str(value[KEY]).lower() == VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						del(dictout[id])
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"eq" disponibile solo per: name, lat, long, category.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'ne'):
			if(KEY == 'name' or KEY == 'lat' or KEY == 'long' or KEY == 'category'):
				for id, value in dictout.items():
					if not smart_str(value[KEY]).lower() != VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						del(dictout[id])
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"ne" disponibile solo per: name, lat, long, category.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'lt'):
			if (KEY == 'lat' or KEY == 'long'):
				for id, value in dictout.items():
					if not smart_str(value[KEY]).lower() < VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						del(dictout[id])
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"lt" disponibile solo per:  lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE				
		elif (COMP == 'gt'):
			if (KEY == 'lat' or KEY == 'long'):
				for id, value in dictout.items():
					if not smart_str(value[KEY]).lower() > VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						del(dictout[id])
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"gt" disponibile solo per:  lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'le'):
			if (KEY == 'lat' or KEY == 'long'):
				for id, value in dictout.items():
					if not smart_str(value[KEY]).lower() <= VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						del(dictout[id])
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"le" disponibile solo per:  lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'ge'):
			if (KEY == 'lat' or KEY == 'long'):
				for id, value in dictout.items():
					if not (smart_str(value[KEY]).lower() >= VALUE):
						#req.write('ID OK -> %s \r\n' % id)
						del(dictout[id])
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"ge" disponibile solo per: lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'contains'):
			if not((KEY == 'lat') or (KEY == 'long')):
				for id, value in dictout.items():	
					if not (VALUE in smart_str(value[KEY]).lower()):
						del(dictout[id])
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"contains" non disponibile solo per: lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'ncontains'):
			if not((KEY == 'lat') or (KEY == 'long')):
				for id, value in dictout.items():		
					if (VALUE in smart_str(value[KEY]).lower()):
						del(dictout[id])
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"ncontains" non disponibile solo per: lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE
		else:
			req.status = A.HTTP_NOT_ACCEPTABLE
			req.write('406: NOT ACCEPTABLE\r\n')
			req.write('parametro %s non riconosciuto.\r\n' % COMP)
			raise A.SERVER_RETURN, A.DONE
	else:
		req.status = A.HTTP_NOT_ACCEPTABLE
		req.write('406: NOT ACCEPTABLE\r\n')
		req.write('parametro %s non riconosciuto.\r\n' % KEY)
		raise A.SERVER_RETURN, A.DONE

	req.content_type = 'text/turtle; charset=utf-8'
	req.write(tottl(dictout))
	req.status = A.OK
	raise A.SERVER_RETURN, A.DONE
