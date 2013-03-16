import urllib2 as U
from mod_python import apache as A, util
from xml.dom.minidom import parse, parseString
from encoding import smart_str
from operator import itemgetter as IG
import json, math, csv, tempfile, codecs

def index(req):
	headers = { 'Accept' : 'application/json' }
	reqq = U.Request('http://ltw1129.web.cs.unibo.it/cgi-bin/descrittore/vicinoa.py?lat=44.500456&long=11.277643&max=10&distance=5000', headers= headers)

	try:
		r = U.urlopen(reqq)
	except U.HTTPError, e:
		req.status = A.HTTP_INTERNAL_SERVER_ERROR
		req.write('500: INTERNAL SERVER ERROR\r\n')
		req.write('%s non raggiungibile. (errore: %d)\r\n' % (host,e.code))
		raise A.SERVER_RETURN, A.DONE
	except U.URLError, e:
		req.status = A.HTTP_INTERNAL_SERVER_ERROR
		req.write('500: INTERNAL SERVER ERROR\r\n')
		req.write('%s non raggiungibile. (errore: %d)\r\n' % (host,e.args))
		raise A.SERVER_RETURN, A.DONE
		
	data = r.read()
	req.content_type = 'text/plain'
	req.write(data)
