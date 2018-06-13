#!/usr/bin/python

from __future__ import division
from __future__ import print_function

import sys
import socket
import logging

import wordpress_orm
from flask import Flask

from . import jinja_filters
from . import _app_setup_utils
from .utilities.color_print import print_warning, print_error, print_info, yellow_text, green_text, red_text


print("__init__")

# ================================================================================

def register_blueprints(app=None):
	'''
	Register the code associated with each URL paths. Manually add each new
	controller file you create here.
	'''
	from .controllers.index import index_page
	from .controllers.miscellanea import miscellanea_page
	from .controllers.assan_blank import assan_blank_page
	from .controllers.admin_template import assan_admin_template
	from .controllers.notebook import notebook_page
	from .controllers.wp_demo import wp_demo_page
	from .controllers.post import post_page
	from .controllers.posts import post_grid
	from .controllers.mission_statement import mission_statement_page
	from .controllers.resource_links import resource_links_page
	from .controllers.contact import contact_page
	from .controllers.people import people_page
	from .controllers.faq import faq_page
	from .controllers.search import search_page
	from .controllers.search_api import search_api
	from .controllers.research import research_page
	from .controllers.jobs import jobs_page
	from .controllers.mailing_list import mailing_list_page
	from .controllers.events import events_page
	from .controllers.news import news_page
	from .controllers.about import about_page
	from .controllers.community import community_page
	from .controllers.resources import resources_page
	#from .controllers.controller1 import xxx

	app.register_blueprint(index_page)
	app.register_blueprint(miscellanea_page)
	app.register_blueprint(assan_blank_page)
	app.register_blueprint(assan_admin_template)
	app.register_blueprint(wp_demo_page)
	app.register_blueprint(post_page)
	app.register_blueprint(post_grid)
	app.register_blueprint(mission_statement_page)
	app.register_blueprint(resource_links_page)
	app.register_blueprint(contact_page)
	app.register_blueprint(people_page)
	app.register_blueprint(faq_page)
	app.register_blueprint(search_page)
	app.register_blueprint(research_page)
	app.register_blueprint(jobs_page)
	app.register_blueprint(mailing_list_page)
	app.register_blueprint(events_page)
	app.register_blueprint(news_page)
	app.register_blueprint(about_page)
	app.register_blueprint(community_page)
	app.register_blueprint(resources_page)
	#app.register_blueprint(notebook_page)
	#app.register_blueprint(xxx)

	if (app.debug):
		from .controllers.sandbox import sandbox_page
		app.register_blueprint(sandbox_page)

# ================================================================================

#try:
#	app
#except NameError:
#	app = Flask(__name__)

app = None

# defined here so that other files can import this object
wordpress_api = None # define below after configuration is read -> app.config["WP_BASE_URL"]

# set up wordpress-orm logger
wordpress_orm_logger = logging.getLogger("wordpress_orm")

def create_app(debug=False, conf=dict()):

	print(" = = = = = = = = = = = creating app ...")

	global app
	app = Flask(__name__) # creates the app instance using the name of the module
	app.debug = debug

	# --------------------------------------------------
	# Read configuration files.
	# -------------------------
	# You can define a different configuration
	# file based on the host the app is running on.
	#
	# Configuration files are located in the "configuration_files" directory.
	# -----------------------------------------------------------------------
	server_config_file = None

	# configuration files by host name in debug mode
	if app.debug:
		hostname = socket.gethostname()
		if "your_host" in hostname:
			server_config_file = _app_setup_utils.getConfigFile("your_host.cfg")
		else:
			server_config_file = _app_setup_utils.getConfigFile("default.cfg") # default

	else:
		if conf["usingUWSGI"]:
			try:
				import uwsgi
				# The uWSGI configuration file defines a key value pair to point
				# to a particular configuration file in this module under "configuration_files".
				# The key is 'flask_config_file', and the value is the name of the configuration
				# file.
				# NOTE: For Python 3, the value from the uwsgi.opt dict below must be decoded, e.g.
				# config_file = uwsgi.opt['flask-config-file'].decode("utf-8")
			except ImportError:
				print("Trying to run in production mode, but not running under uWSGI.\n"
					  "You might try running again with the '--debug' (or '-d') flag.")
				sys.exit(1)

			# read configuration file specified in uWSGI parameters
			config_filename = None
			try:
				config_filename = uwsgi.opt['flask-config-file'].decode("utf-8")
			except KeyError:
				print("No Flask configuration file was found (this is ok, it's optional.)")
			if config_filename:
				server_config_file = _app_setup_utils.getConfigFile(config_filename)
				print(green_text("Loading config file: "), yellow_text(server_config_file))
				app.config.from_pyfile(server_config_file)

	# -----------------------------
	# Perform app setup below here.
	# -----------------------------

	if app.debug:
		#print("{0}App '{1}' created.{2}".format('\033[92m', __name__, '\033[0m'))
		print_info("Application '{0}' created.".format(__name__))
	else:
		if conf["usingSentry"]:
			_app_setup_utils.setupSentry(app, dsn=sentryDSN)

	# Change the implementation of "decimal" to a C-based version (much! faster)
	try:
		import cdecimal
		sys.modules["decimal"] = cdecimal
	except ImportError:
		pass # not available

	if conf["usingSQLAlchemy"]:
		if conf["usingPostgreSQL"]:
			_app_setup_utils.setupJSONandDecimal()

	    # This "with" is necessary to prevent exceptions of the form:
	    #    RuntimeError: working outside of application context
	    #    (i.e. the app object doesn't exist yet - being created here)

			with app.app_context():
				from .model.databasePostgreSQL import db

	# config is defined by now
	global wordpress_api
	wordpress_api = wordpress_orm.API(url=app.config["WP_BASE_URL"])

	# Register all paths (URLs) available.
	register_blueprints(app=app)

	# Register all Jinja filters in the file.
	app.register_blueprint(jinja_filters.blueprint)

	return app
