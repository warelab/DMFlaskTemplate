#!/usr/bin/python

# from flask import request #, make_response

import flask
from flask import request, render_template

from .. import app
#from .. import wordpress_api as api
from . import valueFromRequest

new_page = flask.Blueprint("new_page", __name__)

# Note: add to __all__ in __init__.py file
@app.route('/path') #, methods=['GET'])
def func_name():
	''' Documentation here. '''
	templateDict = {}
	
	
	return render_template("template.html", **templateDict)