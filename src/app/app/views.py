from markupsafe import escape
from flask import render_template, request, redirect, url_for

from app import app

from .errorviews import *

@app.route('/')
def home():
   return "Hello World!"