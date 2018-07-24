
'''

Custom WordPress object defined using the plugin WordPress Pods.

Ref: https://wordpress.org/plugins/pods/
'''

import json
import logging
import requests

from wordpress_orm import WPEntity, WPRequest, WPORMCacheObjectNotFoundError


logger = logging.getLogger("wordpress_orm")

class ScientificPaper(WPEntity):

	def __init__(self, id=None, api=None):
		super().__init__(api=api)

		# related objects that need to be cached
		self._author = None
		self._category = None

	def __repr__(self):
		if len(self.s.title) < 11:
			truncated_title = self.s.title
		else:
			truncated_title = self.s.title[0:10] + "..."
		return "<WP {0} object at {1}, url='{2}'>".format(self.__class__.__name__, hex(id(self)),
																			self.s.id,
																			truncated_title)

	@property
	def schema_fields(self):
		return ["id", "date", "date_gmt", "guid", "modified", "modified_gmt",
				"slug", "status", "type", "link", "title", "content", "template",
				"paper_title", "abstract","source_url", "paper_authors", "publication_date",
				"pubmed_id"]

	@property
	def categories(self):
		'''
		Returns a list of categories (as Category objects) associated with this post.
		'''
		if self._categories is None:
			self._categories = list()
			for category_id in self.s.categories:
				try:
					self._categories.append(self.api.category(id=category_id))
				except exc.NoEntityFound:
					logger.debug("Expected to find category ID={0} from post (ID={1}), but no category found.".format(category_id, self.s.id))
		return self._categories

	@property
	def category_names(self):
		return [x.s.name for x in self.categories]

	@property
	def author(self):
		'''
		Returns the author of this post, class: 'User'.
		'''
		if self._author is None:
			ur = self.api.UserRequest()
			ur.id = self.s.author # ID for the author of the object
			user_list = ur.get()
			if len(user_list) == 1:
				self._author = user_list[0]
			else:
				raise exc.UserNotFound("User ID '{0}' not found.".format(self.author))
		return self._author


class ScientificPaperRequest(WPRequest):
	'''
	A class that encapsulates requests for WordPress scientific papers.
	'''
	def __init__(self, api=None):
		super().__init__(api=api)
		self.id = None # WordPress ID
		self._before = None
		self._after = None

		self._status = list()
		self._category_ids = list()
		self._slugs = list()

	@property
	def parameter_names(self):
		return ["slug", "before", "after", "status", "categories", "paper_title"]

	def get(self):
		'''
		Returns a list of 'Scientific Paper' objects that match the parameters set in this object.
		'''
		self.url = self.api.base_url + "scientific_paper"

		if self.id:
			self.url += "/{}".format(self.id)

		# -------------------
		# populate parameters
		# -------------------
		if self.slug:
			self.parameters["slug"] = self.slug

		if self.before:
			self.parameters["before"] = self._before.isoformat()

		if self.after:
			self.parameters["after"] = self._after.isoformat()

		# -------------------

		try:
			self.get_response()
			logger.debug("URL='{}'".format(self.request.url))
		except requests.exceptions.HTTPError:
			logger.debug("Post response code: {}".format(self.response.status_code))
			if self.response.status_code == 400: # bad request
				logger.debug("URL={}".format(self.response.url))
				raise exc.BadRequest("400: Bad request. Error: \n{0}".format(json.dumps(self.response.json(), indent=4)))
			elif self.response.status_code == 404: # not found
				return None

		papers_data = self.response.json()

		if isinstance(papers_data, dict):
			# only one object was returned; make it a list
			papers_data = [papers_data]

		papers = list()
		for d in papers_data:

			# Before we continue, do we have this ScientificPaper in the cache already?
			try:
				paper = self.api.wordpress_object_cache.get(class_name=ScientificPaper.__name__, key=d["id"])
				papers.append(paper)
				continue
			except WPORMCacheObjectNotFoundError:
				# nope, carry on
				pass

			paper = ScientificPaper(api=self.api)
			paper.json = json.dumps(d)

			paper.update_schema_from_dictionary(d)
			
# 			paper.s.id = d["id"]
# 			paper.s.date = d["date"]
# 			paper.s.date_gmt = d["date_gmt"]
# 			paper.s.guid = d["guid"]
# 			paper.s.modified = d["modified"]
# 			paper.s.modified_gmt = d["modified_gmt"]
# 			paper.s.slug = d["slug"]
# 			paper.s.status = d["status"]
# 			paper.s.type = d["type"]
# 			paper.s.link = d["link"]
# 			paper.s.title = d["title"]
# 			paper.s.content = d["content"]
# 			paper.s.template = d["template"]
# 
# 			paper.abstract = d["abstract"]
# 			paper.paper_authors = d["paper_authors"]
# 			paper.source_url = d["source_url"]
# 			paper.publication_date = d["publication_date"]
# 			paper.pubmed_id = d["pubmed_id"]

			if "_embedded" in d:
				logger.debug("TODO: implement _embedded content for ScientificPaper object")

			# add to cache
			self.api.wordpress_object_cache.set(value=paper, keys=(paper.s.id, paper.s.slug))

			papers.append(paper)

		return papers


	@property
	def slugs(self):
		'''
		The list of post slugs to retrieve.
		'''
		return self._slugs

	@slugs.setter
	def slugs(self, values):
		if values is None:
			self.parameters.pop("slugs", None)
			self._slugs = list()
			return
		elif not isinstance(values, list):
			raise ValueError("Slugs must be provided as a list (or append to the existing list).")

		for s in values:
			if isinstance(s, str):
				self._slugs.append(s)
			else:
				raise ValueError("Unexpected type for property list 'slugs'; expected str, got '{0}'".format(type(s)))

	@property
	def after(self):
		'''
		WordPress parameter to return posts after this date.
		'''
		return self._after

	@after.setter
	def after(self, value):
		'''
		Set the WordPress parameter to return posts after this date.
		'''
		# The stored format is a datetime object, even though WordPress requires
		# it to be ISO-8601.
		#
		if value is None:
			self.parameters.pop("after", None)
			self._after = None
		elif isinstance(value, datetime):
			self._after = value
		else:
			raise ValueError("The 'after' property only accepts `datetime` objects.")

	@property
	def before(self):
		'''
		WordPress parameter to return posts before this date.
		'''
		return self._after

	@before.setter
	def before(self, value):
		'''
		Set the WordPress parameter to return posts before this date.
		'''
		# The stored format is a datetime object, even though WordPress requires
		# it to be ISO-8601.
		#
		if value is None:
			self.parameters.pop("before", None)
			self._before = None
		elif isinstance(value, datetime):
			self._before = value
		else:
			raise ValueError("The 'before' property only accepts `datetime` objects.")

	@property
	def categories(self):
		return self._category_ids

	@categories.setter
	def categories(self, values):
		'''
		This method validates the categories passed to this request.

		It accepts category ID (integer or string) or the slug value.
		'''
		if values is None:
			self.parameters.pop("categories", None)
			self._category_ids = list()
			return
		elif not isinstance(values, list):
			raise ValueError("Categories must be provided as a list (or append to the existing list).")

		for c in values:
			cat_id = None
			if isinstance(c, Category):
				cat_id = c.s.id
#				self._category_ids.append(str(c.s.id))
			elif isinstance(c, int):
#				self._category_ids.append(str(c))
				cat_id = c
			elif isinstance(c, str):
				try:
					# is this a category ID value?
					cat_id = int(c)
					#self._category_ids.append(str(int(c)))
				except ValueError:
					# not a category ID value, try by slug?
					try:
						category = self.api.category(slug=c)
						cat_id = category.s.id
						#self._category_ids.append(category.s.id)
					except exc.NoEntityFound:
						logger.debug("Asked to find a category with the slug '{0}' but not found.".format(slug))

			# Categories are stored as string ID values.
			#
			self._category_ids.append(str(cat_id))
