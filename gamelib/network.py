import urlparse
import requests
import json

import pyglet

urls = {
	"login": "register/",
	"player": "player/",
	"list_dungeons": "dungeons/",
	"dungeon": "dungeon/",
	"replay": "completion/"
}

def SessionCheck(func):

	def wrapper(self, *args, **kwargs):
		if self.is_logged_in():
			return func(self, *args, **kwargs)
		else:
			self.dispatch_event('on_no_connection')

	return wrapper

class Session(pyglet.event.EventDispatcher):
	def __init__(self, server = 'http://localhost:8000'):
		self.server = server
		self.http_session = None

	def login(self, user, password):
		session = requests.Session()

		url = urlparse.urljoin(self.server, urls['login'])

		try:
			resp = session.post(url, data={	'user': user,
											'password': password})
		except requests.exceptions.RequestException:
			self.http_session = None
			self.dispatch_event('on_no_connection')
			return

		if resp.status_code == requests.codes.ok:
			self.http_session = session
			self.dispatch_event('on_connected')
			return

		self.http_session = None
		self.dispatch_event('on_login_failure', resp.text)

	def is_logged_in(self):
		return self.http_session != None

	@SessionCheck
	def dungeons(self):
		url = urlparse.urljoin(self.server, urls['list_dungeons'])

		try:
			resp = self.http_session.get(url)
		except requests.exceptions.RequestException:
			return None

		if resp.status_code == requests.codes.ok:
			try:
				return json.loads(resp.text)
			except AttributeError:
				return None
		else:
			return None

	@SessionCheck
	def get_dungeon(self, dungeon_id):
		frag = urlparse.urljoin(urls['dungeon'], dungeon_id)
		url = urlparse.urljoin(self.server, frag)

		try:
			resp = self.http_session.get(url)
		except requests.exceptions.RequestException:
			return None

		if resp.status_code == requests.codes.ok:
			try:
				return json.loads(resp.text)
			except AttributeError:
				return None

		return None

	@SessionCheck
	def upload_dungeon(self, dungeon):
		url = urlparse.urljoin(self.server, urls['dungeon'])

		try:
			resp = self.http_session.post(url, dungeon)
		except requests.exceptions.RequestException:
			#TODO: should probably event this
			return False

		if resp.status_code == requests.codes.ok:
			return True

		return False

	@SessionCheck
	def get_replay(self, replay_id):
		frag = urlparse.urljoin(urls['replay'], replay_id)
		url = urlparse.urljoin(self.server, frag)

		try:
			resp = self.http_session.get(url)
		except requests.exceptions.RequestException:
			return None

		if resp.status_code == requests.codes.ok:
			try:
				return json.loads(resp.text)
			except AttributeError:
				return None

		return None

	@SessionCheck
	def upload_replay(self, replay):
		url = urlparse.urljoin(self.server, urls['replay'])

		try:
			resp = self.http_session.post(url, dungeon)
		except requests.exceptions.RequestException:
			#TODO: should probably event this
			return False

		if resp.status_code == requests.codes.ok:
			return True

		return False


Session.register_event_type('on_connected')
Session.register_event_type('on_no_connection')
Session.register_event_type('on_login_failure')