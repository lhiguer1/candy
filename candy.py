#!/usr/bin/env python3
import requests
import sys
import os
import lxml.html
import logging
from dotenv import dotenv_values
from datetime import datetime

config = dotenv_values('.env')
username = config['username']
password = config['password']

page_path = 'pages'

if not (username and password):
    raise ValueError('username and/or password not set in \'.env\' file')
    

signin_url         = 'https://www.coingecko.com/account/sign_in'
candy_url          = 'https://www.coingecko.com/account/candy'
daily_check_in_url = 'https://www.coingecko.com/account/candy/daily_check_in'

def log(message):
    logtime = datetime.now()
    logpath = 'logs'
    logname = logtime.date().isoformat() + '.log'

    if not os.path.isdir(logpath):
        os.mkdir(logpath)

    logging.basicConfig(filename=os.path.join(logpath, logname), format='%(asctime)s - %(message)s', level=logging.INFO)
    logging.info(message)

def get_authenticity_token(response):
    '''
    Find required 'authenticity_token'
    '''
    login_html = lxml.html.fromstring(response.text)
    hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')

    for x in hidden_inputs:
        if key := x.attrib.get('name'):
            if key == 'authenticity_token':
                return x.attrib['value']
    sys.exit('Failed to get authenticity token')

def save_page(title, content:bytes):
    '''
    Save page for debug purposuses
    '''
    if not os.path.isdir(page_path):
        os.mkdir(page_path)

    with open(os.path.join(page_path, title), 'wb') as fd:
        fd.write(content)

def can_get_candy(response):
    '''
    Check if candy is available by looking for an element with an id=next-daily-reward-countdown-timer_element
    '''
    html = lxml.html.fromstring(response.text)
    timer_element = html.xpath(r'//span[@id="next-daily-reward-countdown-timer"]')
    return not timer_element

def sign_in(session):
    # get authenticity_token for signin page
    response = session.get(signin_url)
    form = {
            'utf8': '✓',
            'authenticity_token': get_authenticity_token(response),
            'user[email]': username,
            'user[password]': password,
            'user[redirect_to]': '',
            'user[remember_me]': 0,
            'commit': 'Log+in'
            }

    save_page('signin.html', response.content)

    # sign in
    response = session.post(signin_url, data=form)
    save_page('signedin.html', response.content)
    log('Signed in')
    return response

def get_candy(session):
    # get authenticity_token for daily check in page
    response = sess.get(candy_url)

    # get them Clams
    if not can_get_candy(response):
        log('Can\'t get candy yet')
        sys.exit()

    form = {'authenticity_token': get_authenticity_token(response) }
    save_page('candy.html', response.content)

    response = sess.post(daily_check_in_url, data=form)
    save_page('candy_after.html', response.content)
    log('Candy Collected')
    return response

if __name__=='__main__':
    with requests.Session() as sess:
        sign_in(sess)
        get_candy(sess)
        


