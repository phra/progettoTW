#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       aggregatoreJSON v1.0
#       
#       Copyright 2011 indieCODE <ltw1129@web.cs.unibo.it>
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


from mod_python import apache as A, util
from encoding import smart_str
import codecs, csv

def handler(req):

	if not (('text/csv' in req.headers_in['Accept']) or ('text/x-python' in req.headers_in['Accept'])):
		req.content_type = 'text/plain; charset="UTF-8"'
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
		path = '/home/web/ltw1129/cgi-bin/aggregatore/csv/scuolematerneBO2011.csv'
		enc = 'utf-8'
		fd = codecs.open(path,'r',enc)
		attrs = ["id","category","name","address","lat","long","subcategory","note","opening","closing","creator","created","valid","version","source"]
		fd.readline()
		dump = csv.DictReader(fd, attrs, lineterminator='\n')
	except IOError:
		req.status = A.HTTP_INTERNAL_SERVER_ERROR
		req.write('500: INTERNAL SERVER ERROR\r\n')
		req.write('%s non trovato\r\n' % path)
		raise A.SERVER_RETURN, A.DONE	
	s = ''.join('id,category,name,address,lat,long,subcategory,note,opening,closing,creator,created,valid,version,source\n')

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
			req.write('i parametri sono: %s %s %s\r\n\r\n' % (KEY, COMP, VALUE))
			raise A.SERVER_RETURN, A.DONE
		if what.args[0] == 'foo':
			req.content_type = 'text/csv'
			for line in dump:
				s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
							
			req.write(smart_str(s))
			fd.close()
			req.status = A.OK
			raise A.SERVER_RETURN, A.DONE 

	if (KEY == 'id'):
		if (COMP == 'eq'):
			for line in dump:
				if smart_str(line['id']).lower() == VALUE:
					#req.write('ID OK -> %s \r\n' % id)
					s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
		elif (COMP == 'ne'):
			for line in dump:
				if smart_str(line['id']).lower() != VALUE:
					#req.write('ID OK -> %s \r\n' % id)
					s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
		elif (COMP == 'contains'):
			for line in dump:
				if VALUE in smart_str(line['id']).lower():
					#req.write('ID OK -> %s \r\n' % id)
					s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
		else:
			req.status = A.HTTP_NOT_ACCEPTABLE
			req.write('406: NOT ACCEPTABLE\r\n')
			req.write('parametro %s non riconosciuto.\r\n' % COMP)
			raise A.SERVER_RETURN, A.DONE
	elif (KEY == 'name' or KEY == 'lat' or KEY == 'long' or KEY == 'category' or KEY == 'address' or KEY == 'opening' or KEY == 'closing'):
		if (COMP == 'eq'):
			if(KEY == 'name' or KEY == 'lat' or KEY == 'long' or KEY == 'category'):
				for line in dump:
					if smart_str(line[KEY]).lower() == VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"eq" disponibile solo per: name, lat, long, category.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'ne'):
			if(KEY == 'name' or KEY == 'lat' or KEY == 'long' or KEY == 'category'):
				for line in dump:
					if smart_str(line[KEY]).lower() != VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"ne" disponibile solo per: name, lat, long, category.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'lt'):
			if (KEY == 'lat' or KEY == 'long'):
				for line in dump:
					if smart_str(line[KEY]).lower() < VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"lt" disponibile solo per:lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE				
		elif (COMP == 'gt'):
			if (KEY == 'lat' or KEY == 'long'):
				for line in dump:
					if smart_str(line[KEY]).lower() > VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"gt" disponibile solo per:lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'le'):
			if (KEY == 'lat' or KEY == 'long'):
				for line in dump:
					if smart_str(line[KEY]).lower() <= VALUE:
						#req.write('ID OK -> %s \r\n' % id)
						s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"le" disponibile solo per:lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'ge'):
			if (KEY == 'lat' or KEY == 'long'):
				for line in dump:
					if (smart_str(line[KEY]).lower() >= VALUE):
						#req.write('ID OK -> %s \r\n' % id)
						s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"ge" disponibile solo per:lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'contains'):
			if not((KEY == 'lat') or (KEY == 'long')):
				for line in dump:		
					if (VALUE in smart_str(line[KEY]).lower()):
						#smart_str(line[KEY]+'\n')
						s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"contains" non disponibile solo per:lat, long.\r\n')
				raise A.SERVER_RETURN, A.DONE
		elif (COMP == 'ncontains'):
			if not((KEY == 'lat') or (KEY == 'long')):
				for line in dump:		
					if not (VALUE in smart_str(line[KEY]).lower()):
						s += line['id']+','+line['category']+','+line['name']+',"'+line['address']+'",'+line['lat']+','+line['long']+','+line['subcategory']+','+line['note']+',"'+line['opening']+'","'+line['closing']+'",'+line['creator']+','+line['created']+','+line['valid']+','+line['version']+','+line['source']+'\n'
			else:
				req.status = A.HTTP_NOT_ACCEPTABLE
				req.write('406: NOT ACCEPTABLE\r\n')
				req.write('"ncontains" non disponibile solo per:lat, long.\r\n')
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

	req.content_type = 'text/csv; charset="UTF-8"'
	req.write(smart_str(s))
	fd.close()
	req.status = A.OK
	raise A.SERVER_RETURN, A.DONE
