#client for dolibarr api
import datetime
import requests
import json
import logging
import os
import sys
import time
from dolibarr.conf import conf


class Dolibarr:

    def __init__(self, url, apikey, debug=False):
        self.url = url +"/api/index.php/"
        self.apikey = apikey
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({'DOLAPIKEY': self.apikey})
        self.session.headers.update({'Content-Type': 'application/json'})
        self.session.headers.update({'Accept': 'application/json'})

    def get(self, resource, params=None):
        print(self.url + resource)
        if self.debug:
            logging.debug('GET %s %s', self.url+resource, params)
        r = self.session.get(self.url + resource, params=params)
        if self.debug:
            logging.debug('GET %s %s', r.status_code, r.text)
        return r
    
    def post(self, resource, data=None):
        if self.debug:
            logging.debug('POST %s %s', resource, data)
        r = self.session.post(self.url + resource, data=data)
        if self.debug:
            logging.debug('POST %s %s', r.status_code, r.text)
        return r

    def put(self, resource, data=None):
        if self.debug:
            logging.debug('PUT %s %s', resource, data)
        r = self.session.put(self.url + resource, data=data)
        if self.debug:
            logging.debug('PUT %s %s', r.status_code, r.text)
        return r
    '''
    get /agendaevents
    '''
    def get_events(self,pmin,pmax):
        #get today date unix stamp
        today = datetime.date.today()
        # dolibarr queryparams
        params ={
            'sortfield': 't.datep',
            'sortorder': 'DESC',
            'limit': 100,
            'page': 0,
            'sqlfilters': '(t.datec:>=:\'%s\') ' % today.strftime('%Y-%m-%d') #get events from today
        }
        params['sqlfilters'] += ' AND (t.percent:>=:%i) AND (t.percent:<=:%i)' % ( pmin, pmax)
        #code type AC_OTH
        params['sqlfilters'] += ' AND (t.code:LIKE:\'%s\')' % (conf["evt_code_type"])
        r = self.get('agendaevents', params=params)
        print( params['sqlfilters'])
        if r.status_code == 200:
            #debug raw
            #print(r.body)
            
            return r.json()
        else:
            return r.text
    '''
    get /thirdparties/{id} 
    '''
    def get_thirdparty(self, id):
        r = self.get('thirdparties/'+str(id))
        if r.status_code == 200:
            return r.json()
        else:
            return r.text
    #get /documents/download 
    '''Parameters
    Parameter 	Value 	Description 	Parameter Type 	Data Type
    modulepart: Name of module or area concerned by file download ('facture', ...)	query 	string
    original_file: Relative path with filename, relative to modulepart (for example: IN201701-999/IN201701-999.pdf)	query 	string

    Response Body

    {
    "filename": "lick.gif",
    "content-type": "image/gif",
    "filesize": 144875,
    "content": "R0lGODlhQAHwA...g4dcNsWSPPOOw=="
    "encoding": "base64"
    }
    '''
    def get_document(self, modulepart, original_file):
        r = self.get('documents/download?modulepart='+modulepart+'&original_file='+original_file)
        if r.status_code == 200:
            return r.json()
        else:
            return r.text

#implement update event agenda
#put /agendaevents/{id} 
    def update_event(self, id, data):
       
        r = self.put('agendaevents/'+str(id), data=json.dumps(data))
        if r.status_code == 200:
            return r.json()
        else:
            return r.text
#debug conf

dol = Dolibarr(url=conf["url"],apikey=conf["apikey"],debug=True)
dol.debug=True;
