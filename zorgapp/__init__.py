from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

ENV = 'prod'
developer = 'Arjun'
if ENV == 'dev':
    app.debug = True
    app.config['SECRET_KEY'] = 'awwfaw'
    if developer == 'Arjun':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Postgre-arj4703@localhost/Zorg'
    elif developer == 'Tarun':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Tarun@postgresql@localhost/Zorg'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hxceiafawftfoj:be308eb925667514c2f0102ea54672bd5b11a3c6643062b2012dedc396304b36@ec2-54-237-155-151.compute-1.amazonaws.com:5432/d82ngqr88afvm9'
    app.config['SECRET_KEY'] = os.environ['secret']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

from zorgapp import routes
