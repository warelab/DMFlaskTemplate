#!/usr/bin/python

# from flask import request #, make_response

import flask
import logging
from flask import request, render_template
#from wordpress_orm.entities.user import UserRequest

from wordpress_orm import wp_session
from ..wordpress_orm_extensions.user import SBUser

from .. import app
from .. import wordpress_api as wpapi
from . import valueFromRequest
from .footer import populate_footer_template

logger = logging.getLogger("wordpress_orm")

people_page = flask.Blueprint("people_page", __name__)

@people_page.route('/people')
def people():
	''' People page. '''
	templateDict = {}

	with wpapi.Session():

		user_request = wpapi.UserRequest()
		user_request.context = "edit"
		user_request.per_page = 50
		user_request.roles = ['team_member']

		team = user_request.get(class_object=SBUser)

		USDA = [u for u in team if ("USDA" in u.s.organization)]

		comp = [u for u in team if ("Computational" in u.s.job_title)
					and not ("USDA" in u.s.organization)
					and not ("Post" in u.s.job_title)
					or ("Systems" in u.s.job_title)]

		researchers = [u for u in team if not ("Computational" in u.s.job_title)
						and not ("USDA" in u.s.organization)
						and not ("Systems" in u.s.job_title)
						or ("Post" in u.s.job_title)]


		people_banner_media = wpapi.media(slug="sorghum_combine")
		templateDict["banner_media"] = people_banner_media

		populate_footer_template(template_dictionary=templateDict, wp_api=wpapi, photos_to_credit=[people_banner_media])

	templateDict['comp'] = comp
	templateDict['USDA'] = USDA
	templateDict['researchers'] = researchers
	print(researchers)
	return render_template("people.html", **templateDict)
