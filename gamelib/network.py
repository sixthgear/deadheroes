import urlparse
import requests

import pyglet

urls = {
	"login": "register/",
}

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

		self.dispatch_event('on_login_failure', resp.text)


	def is_logged_in(self):
		return self.http_session != None

	def dungeons(self):
		pass

	def get_dungeon(self, dungeon_id):
		pass

	def upload_dungeon(self, dugeon):
		pass

	def get_replay(self, replay_id):
		pass

	def upload_replay(self, replay):
		pass

Session.register_event_type('on_connected')
Session.register_event_type('on_no_connection')
Session.register_event_type('on_login_failure')