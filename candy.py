#!/usr/bin/env python3
import requests
import lxml.html
from dotenv import dotenv_values

config = dotenv_values('.env')
username = config['username']
password = config['password']

if not (username and password):
    raise ValueError('username and/or password not set in \'.env\' file')
    

signin_url         = 'https://www.coingecko.com/account/sign_in'
candy_url          = 'https://www.coingecko.com/account/candy'
daily_check_in_url = 'https://www.coingecko.com/account/candy/daily_check_in'


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

def save_page(title, content:bytes):
    '''
    Save page for debug purposuses
    '''
    with open(title, 'wb') as fd:
        fd.write(content)

def can_get_candy(response):
    '''
    Check if candy is available by looking for an element with an id=next-daily-reward-countdown-timer_element
    '''
    html = lxml.html.fromstring(response.text)
    timer_element = html.xpath(r'//span//t[@id="next-daily-reward-countdown-timer"]')
    return not timer_element

if __name__=='__main__':
    with requests.Session() as sess:
        # get authenticity_token for signin page
        response = sess.get(signin_url)
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
        print(f'[+] {form["authenticity_token"]=}')
        assert form['authenticity_token']

        # sign in
        response = sess.post(signin_url, data=form)
        save_page('signedin.html', response.content)
        
        # get authenticity_token for candy page
        response = sess.get(candy_url)
        form = {'authenticity_token': get_authenticity_token(response) }
        save_page('candy.html', response.content)
        print(f'[+] {form["authenticity_token"]=}')

        # get them Clams
        if can_get_candy(response):
            response = sess.post(daily_check_in_url, data=form)
            save_page('candy_after.html', response.content)


