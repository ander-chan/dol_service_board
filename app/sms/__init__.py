'''
sms gamu api example
AUTH=$(echo -ne "admin:password" | base64 --wrap 0)
curl -H 'Content-Type: application/json' -H "Authorization: Basic $AUTH" -X POST --data '{"text":"Hello, how   are you?", "number":"+420xxxxxxxxx"}' http://localhost:5000/sms
'''
import requests

from app.sms.conf import Conf


##send sms
def send_sms(number, text):
    auth = (Conf.username, Conf.password)
    url = Conf.url + '/sms'
    data = {'text': text, 'number': number}
    #if smsc is defined
    if 'smsc' in Conf:
        data['smsc'] = Conf.smsc

    r = requests.post(url, auth=auth, json=data)
    return r.status_code
