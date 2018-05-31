#!/usr/bin/python

# from flask import request #, make_response

import flask
import logging
from flask import request, render_template
from wordpress_orm import wp_session

from .. import app
from .. import wordpress_api as api
from . import valueFromRequest
from .footer import populate_footer_template

logger = logging.getLogger("wordpress_orm")

post_grid = flask.Blueprint("post_grid", __name__)

WAY_MORE_THAN_WE_WILL_EVER_HAVE = 100
@app.route('/posts')
def posts():
	''' List of posts '''
	templateDict = {}
	start_page = valueFromRequest(key="page", request=request) or 1
	n_per_page = valueFromRequest(key="show", request=request) or 9
	categories = valueFromRequest(key="categories", request=request, aslist=True)

	with wp_session(api):

		post_request = api.PostRequest()
		if categories:
			post_request.categories = categories
		post_request.categories_exclude = ["faq"]
		post_request.per_page = WAY_MORE_THAN_WE_WILL_EVER_HAVE
		post_tally = post_request.get(count=True)

		post_request.orderby = "date"
		post_request.order = "desc"
		post_request.per_page = n_per_page
		post_request.page = start_page

		posts = post_request.get(count=False)

		posts_banner_media = api.media(slug="k-state-sorghum-field-1920x1000")
		templateDict["banner_media"] = posts_banner_media

		# pre-cache these items so new HTTP connections aren't made from the template
		for p in posts:
			p.categories
			p.author

		populate_footer_template(template_dictionary=templateDict, wp_api=api, photos_to_credit=[posts_banner_media])

	templateDict['posts'] = posts
	templateDict['post_tally'] = post_tally

	logger.debug(" ============= controller finished ============= ")

	return render_template("posts.html", **templateDict)