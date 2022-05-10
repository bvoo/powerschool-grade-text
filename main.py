import requests
import json
from bs4 import BeautifulSoup
import logging
import log as log
from twilio.rest import Client

log.log()

with open('secrets.json') as f:
    logging.info('Loading secrets')
    secrets = json.load(f)

Client = Client(secrets['account_sid'], secrets['auth_token'])

url = 'https://' + secrets['district'] + '.powerschool.com/guardian/home.html'


data = {
    'dbpw': secrets['password'],
    'translator_username': '',
    'translator_password': '',
    'translator_ldappassword': '',
    'returnUrl': '',
    'serviceName': 'PS Parent Portal',
    'serviceTicket': '',
    'pcasServerUrl': '',
    'credentialType': 'User Id and Password Credential',
    'request_locale': 'en_US',
    'account': secrets['username'],
    'pw': secrets['password'],
    'translatorpw': ''
}

r = requests.post(url, data=data)
if r.status_code == 200:
    logging.success('Logged in!')

soup = BeautifulSoup(r.text, 'html.parser')

def sendSms(text):
    logging.info('Sending SMS')
    
    text = '\n'.join(['{}: {}'.format(grade['name'], grade['grade']) for grade in text])
    
    Client.messages.create(
        body=text,
        from_=secrets['twilio_number'],
        to=secrets['phone_number']
    )

    logging.success('Sent SMS!')



def getGrades():
    grades = []

    logging.info('Getting grades')
    lookup = soup.find('div', id='quickLookup')
    
    table = lookup.find('table')
    rows = table.find_all('tr')
    headers = rows[0].find_all('th')

    for tr in table.select('tr'):
        for td in tr.select('td'):
            if td.find('a'):
                if not td.text[0].isalpha():
                    continue

                keywords = [
                    'Morning',
                    'Carr',
                    'Club',
                    'Moral',
                    'Lights'
                ]

                if any(keyword in td.text for keyword in keywords):
                    continue
                
                index = tr.select('td').index(td)

                if 'Email' in td.text:
                    text = td.text[:td.text.index('Email')]
                else:
                    text = td.text
                
                logging.info('{}: {}'.format(headers[index - 12].text, text))

                grades.append({
                    'name': headers[index - 12].text,
                    'grade': text
                })
    
    logging.success('Got grades!')
    sendSms(grades)


getGrades()
