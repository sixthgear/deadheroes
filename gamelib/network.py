import urlparse
import requests
import json

import pyglet
from gamelib.util_hax import defer

urls = {
    "login":                       "register/",
    "player":                      "player/",
    "list_dungeons":               "dungeons/",
    "dungeon":                     "dungeon/",
    "replay":                      "completion/"
}

def SessionCheck(func):

    def wrapper(self, *args, **kwargs):
        if self.is_logged_in():
            return func(self, *args, **kwargs)
        else:
            defer(self.controller.on_no_connection)

    return wrapper

class Session(object):
    def __init__(self, controller, server = 'http://localhost:8000'): # http://misadventuregames.com:8000'):
        self.controller = controller
        self.server = server
        self.http_session = None

    def login(self, user, password):
        session = requests.Session()

        url = urlparse.urljoin(self.server, urls['login'])

        try:
            resp = session.post(url, data={ 'user': user,
                                            'password': password})
        except requests.exceptions.RequestException:
            self.http_session = None
            defer(self.controller.on_no_connection)
            return

        if resp.status_code == requests.codes.ok:
            self.http_session = session
            defer(self.controller.on_logged_in, resp.text)
            return

        self.http_session = None
        defer(self.controller.on_login_failure, resp.text)

    def is_logged_in(self):
        return self.http_session != None


    @SessionCheck
    def get_player(self):
        
        url = urlparse.urljoin(self.server, urls['player'])

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
    def get_dungeon(self, dungeon_id=None):
        if dungeon_id:
            frag = urlparse.urljoin(urls['dungeon'], dungeon_id)
            url = urlparse.urljoin(self.server, frag)
        else:
            url = urlparse.urljoin(self.server, urls['dungeon'])

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
            resp = self.http_session.post(url, data={'dungeon': dungeon})
        except requests.exceptions.RequestException:
            #TODO: should probably event this
            return False

        if resp.status_code == requests.codes.ok:
            return resp.text

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
    def upload_replay(self, username, dungeon_id, replay, won):
        url = urlparse.urljoin(self.server, urls['replay'] + dungeon_id)
        # print url
        data = {
            'username': username,            
            'replay': replay,
            'player_win': str(won).lower()
        }
        
        try:
            resp = self.http_session.post(url, data)
        except requests.exceptions.RequestException:
            #TODO: should probably event this
            return False

        if resp.status_code == requests.codes.ok:
            return True

        return False


