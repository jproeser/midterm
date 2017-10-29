from flask_bootstrap import Bootstrap
from flask import Flask, request, render_template, session, redirect, url_for, flash
from flask import make_response
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, Form, BooleanField, PasswordField, validators
from wtforms.validators import Required
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import re
import nltk
from pyzipcode import Pyzipcode as pz
import unittest
import pyzipcode
from uszipcode import ZipcodeSearchEngine
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
import random
import sqlite3
import webbrowser  
from jinja2 import Template
from flask_script import Manager, Shell


import requests
import json


app = Flask(__name__)
manager = Manager(app)

Bootstrap(app)
app.debug = True 
app.config['SECRET_KEY'] = 'hard to guess string'


##############################################
##############################################

class NameForm(FlaskForm):
    name = StringField('<h4>What is your name?<br/></h4>', [Required()])
    soundcloud = StringField('<h4>What is the URL to your soundcloud accout?</h4><p><i>(If you do not have one, choose any account)<i/></p><br/>', [Required(message="required"),
        validators.Regexp('^https://soundcloud.com/', message="Username must contain only letters numbers or underscore")
    ])
    submit = SubmitField('Submit')



@app.route('/')
def homepage():
    return render_template('home.html')




@app.route('/signin')
def signin():
    simpleForm = NameForm()

    resp = make_response(render_template('firstform.html', form=simpleForm))
    form = NameForm(request.form)
    # resp.set_cookie('name', '<name>')
    # resp.set_cookie('soundcloud')


    return resp




@app.route('/welcome', methods = ['GET', 'POST'])
def welcome():
    form = NameForm(request.form)


    name = form.name.data
    soundcloud = form.soundcloud.data
    print (name)
    print (soundcloud)
    x = re.match('^https://soundcloud.com/',soundcloud)    

    if x is None and name is "":
        flash('Please fill out the form before submitting!')    
    elif name is "":
        flash('Please enter your name!')    
    
    elif x is None:
        flash('Please enter a valid SoundCloud URL, beginning with https://soundcloud.com/')


    if request.method == 'POST' and form.validate_on_submit():
        
        # name = form.name.data
        # soundcloud = form.soundcloud.data

        

        session['name'] = form.name.data
        name=session.get('name')

  


        session['soundcloud'] = form.soundcloud.data
        soundcloud=session.get('soundcloud')


        sc = str(soundcloud)
        sc = sc.replace("https://soundcloud.com/", "")


        return render_template('welcome.html', name = name, soundcloud = soundcloud, sc = sc)

    return redirect(url_for('signin'))



def parseSoundcloud(x):
    name = session.get('name')
    soundcloud = session.get('soundcloud')
    sc = str(soundcloud)
    sc = sc.replace("https://soundcloud.com/", "")

    z = str(x)

    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
    url = 'https://soundcloud.com/'+str(x)+'/tracks'
    #url = z
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    songlinks=[]

    scheight = .1
    while scheight < 9.9:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
        scheight += .01
    #scrolls through the entire webpage so that all the songs are found, not just the first 10

    elem = driver.find_element_by_tag_name('a')

    for x in driver.find_elements_by_class_name('soundTitle__title'):
    #finds the link to each song of each user
        songlinks.append(x.get_attribute('href'))
    #stores this in a list

########
    followers=[]

    for y in driver.find_elements_by_class_name('infoStats__statLink'):
        followers.append(y.get_attribute('title'))

    numf=followers[0]

    split = numf.split(' ', 1)
    nsplit = split[0]
    nusplit = nsplit.replace(',', '')
    numfollowers = int(nusplit)


    moreorless = ' '

    if numfollowers < 100:
        moreorless = 'less'

    if numfollowers >= 100:
        moreorless = 'more'



    driver.quit()


    return render_template('sclinks.html', songlinks=songlinks, name=name, sc=sc, followers=followers, moreorless=moreorless)


@app.route('/me')
def me():    


    name = session.get('name')


    return name


@app.route('/soundcloud', methods= ['POST','GET'])
def scform():
    return render_template('scform.html')





@app.route('/yoursc')
def yoursc():
    if request.method == 'GET':
        result = request.args
        x = result.get('sc')
        return parseSoundcloud(x)
 

@app.route('/my/<sc>')
def my(sc):
    name = session.get('name')


    x = sc
    return parseSoundcloud(x)


@app.errorhandler(404)
def pageNotFound(error):
    # return 'sorry'
    return render_template('404error.html'), 404



@app.errorhandler(500)
def internal_error(error):
    return render_template('500error.html'), 500





if __name__ == "__main__":
    manager.run() 






