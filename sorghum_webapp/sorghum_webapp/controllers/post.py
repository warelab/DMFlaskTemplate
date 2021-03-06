#!/usr/bin/python

# from flask import request #, make_response

import flask
from flask import request, render_template

import wordpress_orm as wp
from wordpress_orm import wp_session, exc

from .. import app
from .. import wordpress_api as api
from . import valueFromRequest
from .footer import populate_footer_template

WP_BASE_URL = app.config["WP_BASE_URL"]

post_page = flask.Blueprint("post_page", __name__)
post_category_page = flask.Blueprint("post_category_page", __name__)

@post_page.route('/post/<slug>')
def post(slug):
	'''
	This page displays a single blog post retrieved from WordPress.
	'''
	templateDict = {}

	#api = wp.API(url="http://content.sorghumbase.org/wordpress/index.php/wp-json/wp/v2/")

	with api.Session():
		# get the post based on the slug
		try:
			post = api.post(slug=slug)
		except exc.NoEntityFound:
			# TODO return top level posts page
			raise Exception("Return top level posts page, maybe with an alert of 'post not found'.")

		# Get the three latest "News" posts from WordPress.
		# -------------------------------------------------
		pr = api.PostRequest()
		pr.categories = ['news']	# accepts category slug values, not display name
		pr.order = "desc"			# descending order
		pr.per_page = 3				# only get three newest
		latest_posts = pr.get()

		sorghum_grains_image = api.media(slug="sorghum-grains_1920x1000")

		populate_footer_template(wp_api=api, template_dictionary=templateDict, photos_to_credit=[])

		# pre-fetch relationships (premature optimization!)
		for p in latest_posts:
			p.categories


	templateDict["post"] = post
	templateDict["latest_posts"] = latest_posts
	templateDict["sorghum_grains_image"] = sorghum_grains_image
	templateDict["display_comments"] = False
	templateDict["allow_new_comments"] = False
	templateDict["author_gravatar_url"] = post.author.gravatar_url(size=140)

	#for c in post.comments:
	#	print(c)
	#logger.debug(" ============= controller finished ============= ")
	return render_template("post.html", **templateDict)

@post_category_page.route('/posts/category/<slug>')
def post_category(category_slug):
	'''
	This page displays a grid of post thumbnails from a given category.
	'''
	templateDict = {}




	return render_template("post_category.html", **templateDict)
