import base64
import os
import tempfile
from datetime import datetime,timedelta
from os.path import exists
import this
from types import NoneType
from flask_cors import cross_origin
from dolibarr import conf, dol
from app import app
from sms.conf import  conf as sms_conf
import mimetypes
import time
from flask import render_template, request, current_app
from gtts import gTTS
temp = tempfile.mkdtemp()
import dolibarr




@app.route('/')
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def home():
   
    now = datetime.now()
    # -1 hour
    now = datetime.now() - timedelta(hours=2)
     #now time formatDD/MM/YYYYTHH:MM.
    nowdate = now.strftime("%d/%m/%Y %H:%M")  
    #nowtime format HH:MM
    nowtime = now.strftime("%H:%M")

    ''' SMS={
        "url": sms_conf['url'],
        #encode base64 username:password
        "auth": base64.b64encode((sms_conf['username'] + ":" + sms_conf['password']).encode('utf-8')).decode('utf-8'),
    }
    '''

    
    return render_template('index.html',nowtime=nowtime,now=nowdate, title="Home", content="Hello, World!", dolapikey=conf['apikey'])


'''
route for build events
'''


@app.route('/events')
def events():
    r = dol.get_events(pmin=0, pmax=99)
    # if status code is not 200
    # debug events

    # if is json
    # debug type
    print((r))
    if isinstance(r, list):
        return r
        html = "<h1>Events</h1>"

        #

        # foreach events
        for event in r:
            html += "<h2>" + event["label"] + "</h2>"
            # if note_pulic is not null
            if event["note_public"] != None:
                html += "<p>" + event["note_public"] + "</p>"
            # convert datec int unix stam to date
            datec = datetime.fromtimestamp(int(event["datec"])).strftime('%Y-%m-%d %H:%M:%S')
            html += "<p>" + datec + "</p>"
            # convert datep int unix stam to date
            datep = datetime.fromtimestamp(int(event["datep"])).strftime('%Y-%m-%d %H:%M:%S')
            html += "<p>" + datep + "</p>"
            # if note empty convert datef int unix stam to date
            if event["datef"] != "":
                datef = datetime.fromtimestamp(int(event["datef"]))
                html += "<p>" + datef.__format__('%Y-%m-%d %H:%M:%S') + "</p>"
                # show duration

        return html
    else:
        return r

    # format date .strftime('%Y-%m-%d %H:%M:%S')
    def format_date(date):
        return date.strftime('%Y-%m-%d %H:%M:%S')
    # call name


@app.route('/call', methods=['POST'])
def call_name():
    name = request.form.get('name')
    # if exist name.mp3 in temp, return name.mp3
    # else create name.mp3 in temp
    file = temp + "/" + name + ".mp3"
    if not exists(file):
        tts = gTTS(text="Se solicita al acompañante de " + name, lang='es')
        tmpFile = open(file, 'wb');
        tts.write_to_fp(tmpFile)
        tmpFile.close()
    # log path file
    print("stored:", file)
    # get binary file
    enc = ""
    with open(file, 'rb') as f:
        enc = base64.b64encode(f.read())
    # to json

    return {"file": enc.decode("utf-8")}


# get /contacts/{id}
@app.route('/contacts/<id>')
def contact(id):
    # get contact by id
    r = dol.get_contact(id)
    # if status code is not 200
    # debug contact
    # if is json
    # debug type
    print((r))
    if isinstance(r, dict):
        html = "<h1>Contact</h1>"
        html += "<h2>" + r["name"] + "</h2>"
        html += "<p>" + r["address"] + "</p>"
        html += "<p>" + r["email"] + "</p>"
        html += "<p>" + r["phone"] + "</p>"
        html += "<p>" + r["phone_mobile"] + "</p>"
        return html
    else:
        return r


# @app.route('/download/photo',methods=[ 'GET'])


# get thirdparties
@app.route('/buildevent/<thirdpartyid>', methods=['POST'])
def build_event(thirdpartyid):
    # get event from get request json
    event = request.get_json()
    #log event
   # print(event)

    #if event percent is > 0 secs remmaing is datef - now unix timestamp
    if int(event["percentage"]) > 0:
        #get now unix timestamp seconds
        now = int(time.time())
        secs_remaing = event["datef"] - now
    else:
        secs_remaing = event['datef']-event['datep']
    #if secs remmaing is < 0 set to 0
    if secs_remaing < 0:
        secs_remaing = 0
   
    #get duration in 00:00:00 format
    duration = str(timedelta(seconds=secs_remaing))




    # get thirdparty by id
    r = dol.get_thirdparty(thirdpartyid)
    # get logo from thirdparty
    logo = r["logo"]

    # if file logo not exist in /tmp/logos
    if not exists(temp + "/logos/" + logo):
        # test encode base64, directly
        # file ='lick.gif'
        # with open(file, "rb") as image_file:
        #  encoded_string = base64.b64encode(image_file.read())
        # print first and las 10 chars of encoded string, separated by ...
        # print(encoded_string[:10]+"..."+encoded_string[-10:])
        # download logo {id}/logos/{logo}
        img_base64 = download_photo("%s/logos/%s" % (r['id'], r['logo']))
        # print first and las 10 chars of img_base64, separated by ...
        # print(img_base64[:10]+"..."+img_base64[-10:])
        # if no exist dir /tmp/logos create dir
        if not exists(temp + "/logos"):
            os.mkdir(temp + "/logos")
        # to binary file
        imgdata = base64.b64decode(img_base64.split(",")[1])
        # save file in /tmp/logos
        with open(temp + "/logos/" + logo, 'wb') as f:
            f.write(imgdata)  # write binary data

        # save logo in /tmp/logos
        with open(temp + "/logos/" + logo, 'wb') as f:
            f.write(imgdata)
    else:
        # get binary file
        enc = ""
        with open(temp + "/logos/" + logo, 'rb') as f:
            # get media type from file
            mime = mimetypes.guess_type(f.name)[0]  # e.g. 'image/jpeg' or None if cannot be guessed
            enc = base64.b64encode(f.read())
        # to json
        img_base64 = 'data:' + mime + ';base64,' + enc.decode("utf-8")
    # if isinstance(r, dict):
    if isinstance(r, dict):
        # get now datetime in unix timestamp int
        now = datetime.now().timestamp()
        print(r)
        return render_template('card.html',e=event, title= r["name"], call= r["name"], time_remaing=duration,img=img_base64)




def download_photo(logo):
    # get logo from get request
    # logo = request.args.get('logo')
    # get contact by id
    r = dol.get_document("thirdparty", logo)
    # if status code is not 200
    # debug contact
    # if is json
    # debug type
    print((r))
    if isinstance(r, dict):
        # return encoded base64 image src
        return 'data:' + r["content-type"] + ";base64," + r["content"]
    else:
        return r
#implement put route event/start/id and data json
@app.route('/event/start/<id>', methods=['PUT'])
def event_start(id):
    #get datef from get request
    data = request.get_json()
    #update event in dolibarr
    r = dol.update_event(id, data={
        "datef": data['datef'],
        "datep": data['datep'],
    "percentage":50})
    return r

#implement put route event_end
@app.route('/event/end/<id>', methods=['PUT'])
def event_end(id):
    #update event in dolibarr
    r = dol.update_event(id, data={"percentage":100})
    #return json
    return r
