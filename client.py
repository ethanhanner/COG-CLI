# Andy Sayler
# COG API Client
# v2 API
# September 2015

import sys
import json
import abc
import os
import os.path

import requests

_EP_TOKENS = 'tokens'
_KEY_TOKENS = 'token'
_EP_FILES = 'files'
_EP_FILES_CONTENTS = 'contents'
_KEY_FILES = 'files'
_EP_ASSIGNMENTS = 'assignments'
_EP_ASSIGNMENTS_SUBMITABLE = 'submitable'
_EP_ASSIGNMENTS_RUNABLE = 'runable'
_KEY_ASSIGNMENTS = 'assignments'
_EP_TESTS = 'tests'
_KEY_TESTS = 'tests'

_BLOCK_SIZE = 1024

def _debug_dump(r):

    print(
        'Request:\n{}\n{}\n{}\n\n{}\n{}'.format(
            '-----------START-----------',
            r.request.method + ' ' + r.request.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in r.request.headers.items()),
            r.request.body,
            '------------END------------'
        )
    )
    print('Response:\n{}'.format(r.text))

class Connection(object):

    def __init__(self, url, username=None, password=None, token=None):

        # Set vars
        self._url = url
        self._auth = None

        # Authenticate (if able)
        if token:
            self.authenticate(token=token)
        elif username and password:
            self.authenticate(username=username, password=password)

    def authenticate(self, username=None, password=None, token=None):

        endpoint = "{:s}/{:s}/".format(self._url, _EP_TOKENS)

        if token:

            # Verify Token
            auth = requests.auth.HTTPBasicAuth(token, '')
            r = requests.get(endpoint, auth=auth)
            r.raise_for_status()
            token = r.json()[_KEY_TOKENS]

        else:

            # Check Username/Password
            if not username or not password:
                raise TypeError("username and password required")

            # Get Token
            auth = requests.auth.HTTPBasicAuth(username, password)
            r = requests.get(endpoint, auth=auth)
            r.raise_for_status()
            token = r.json()[_KEY_TOKENS]

        self._auth = requests.auth.HTTPBasicAuth(token, '')

    def is_authenticated(self):
        if self._auth:
            return True
        else:
            return False

    def get_url(self):
        return self._url

    def http_post(self, endpoint, json=None, files=None):
        url = "{:s}/{:s}/".format(self._url, endpoint)
        res = requests.post(url, auth=self._auth, json=json, files=files)
        res.raise_for_status()
        return res.json()

    def http_get(self, endpoint):
        url = "{:s}/{:s}/".format(self._url, endpoint)
        res = requests.get(url, auth=self._auth)
        res.raise_for_status()
        return res.json()

    def http_delete(self, endpoint):
        url = "{:s}/{:s}/".format(self._url, endpoint)
        res = requests.delete(url, auth=self._auth)
        res.raise_for_status()
        return res.json()

    def http_download(self, endpoint, path):
        url = "{:s}/{:s}/".format(self._url, endpoint)
        res = requests.get(url, auth=self._auth)
        res.raise_for_status()
        with open(path, 'wb') as fd:
            for chunk in res.iter_content(chunk_size=_BLOCK_SIZE):
                fd.write(chunk)
        return path

class COGObject(object):

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, connection):
        """ Constructor"""

        self._conn = connection
        self._ep = None
        self._key = None

    @abc.abstractmethod
    def create(self, endpoint=None, json=None, files=None):

        if endpoint is None:
            endpoint = self._ep

        res = self._conn.http_post(endpoint, json=json, files=files)
        uuid_list = res[self._key]
        return uuid_list

    def list(self, endpoint=None):

        if endpoint is None:
            endpoint = self._ep

        res = self._conn.http_get(endpoint)
        uuid_list = res[self._key]
        return uuid_list

    def show(self, uid):
        ep = "{:s}/{:s}".format(self._ep, uid)
        res = self._conn.http_get(ep)
        obj = res[uid]
        return obj

    def delete(self, uid):
        ep = "{:s}/{:s}".format(self._ep, uid)
        res = self._conn.http_delete(ep)
        obj = res[uid]
        return obj

class Files(COGObject):

    def __init__(self, connection):
        """ Constructor"""

        # Call Parent
        super(Files, self).__init__(connection)

        #Set Base Key and Endpoint
        self._ep = _EP_FILES
        self._key = _KEY_FILES

    def create(self, path, extract=False):

        # Process Args
        if extract:
            key = 'extract'
        else:
            key = 'file'

        # Setup Files
        files = {key: path}

        # Call Parent
        return super(Files, self).create(files=files)

    def list(self, tst_uid=None, sub_uid=None):

        # Setup Endpoint
        if tst_uid:
            ep = "{:s}/{:s}/{:s}".format(_EP_TESTS, tst_uid, _EP_FILES)
        elif sub_uid:
            ep = "{:s}/{:s}/{:s}".format(_EP_SUBMISSIONS, tst_uid, _EP_FILES)
        else:
            ep = self._ep

        # Call Parent
        return super(Files, self).list(endpoint=ep)

    def download(self, uid, path):

        # Process Directory Path
        if os.path.isdir(path):
            fle_obj = self.show(uid)
            fle_name = os.path.basename(fle_obj["name"])
            path = os.path.join(path, fle_name)
        elif not os.path.basename(path):
            raise FileNotFoundError(path)

        # Download File
        ep = "{:s}/{:s}/{:s}/".format(self._ep, uid, _EP_FILES_CONTENTS)
        path = self._conn.http_download(ep, path)
        return path

class Assignments(COGObject):

    def __init__(self, connection):
        """ Constructor"""

        # Call Parent
        super(Assignments, self).__init__(connection)

        #Set Base Key and Endpoint
        self._ep = _EP_ASSIGNMENTS
        self._key = _KEY_ASSIGNMENTS

    def create(self, name, env):

        # Setup Data
        data = {'name': name, 'env': env}

        # Call Parent
        return super(Assignments, self).create(json=data)

    def list(self, submitable=False, runable=False):

        # Limted Cases
        if submitable or runable:

            submittable_set = set([])
            if submitable:
                ep = "{:s}/{:s}".format(_EP_ASSIGNMENTS, _EP_ASSIGNMENTS_SUBMITABLE)
                submittable_set = set(super(Assignments, self).list(endpoint=ep))

            runable_set = set([])
            if runable:
                ep = "{:s}/{:s}".format(_EP_ASSIGNMENTS, _EP_ASSIGNMENTS_SUBMITABLE)
                runable_set = set(super(Assignments, self).list(endpoint=ep))

            # Combine
            if submitable and runable:
                asn_list = list(submittable_set.intersection(runable_set))
            else:
                asn_list = list(submittable_set.union(runable_set))

        # Open Case
        else:

            ep = self._ep
            asn_list = super(Assignments, self).list(endpoint=ep)

        # Call Parent
        return asn_list

class Tests(COGObject):

    def __init__(self, connection):
        """ Constructor"""

        # Call Parent
        super(Tests, self).__init__(connection)

        #Set Base Key and Endpoint
        self._ep = _EP_TESTS
        self._key = _KEY_TESTS

    def create(self, asn_uid, name, tester, maxscore):

        # Setup Data
        data = {"name": name, "tester": tester, "maxscore": maxscore}

        # Setup Endpoint
        ep = "{:s}/{:s}/{:s}".format(_EP_ASSIGNMENTS, asn_uid, _EP_TESTS)

        # Call Parent
        return super(Tests, self).create(endpoint=ep, json=data)

    def list(self, asn_uid=None):

        # Setup Endpoint
        if asn_uid:
            ep = "{:s}/{:s}/{:s}".format(_EP_ASSIGNMENTS, asn_uid, _EP_TESTS)
        else:
            ep = self._ep

        # Call Parent
        return super(Tests, self).list(endpoint=ep)

# def test_file_add(url, auth, tst_uid, fle_uids):

#     endpoint = "{:s}/{:s}/{:s}/{:s}/".format(url, _EP_TESTS, tst_uid, _EP_FILES)
#     d = {_KEY_FILES: fle_uids}
#     dj = json.dumps(d)
#     r = requests.put(endpoint, auth=auth, data=dj)
#     r.raise_for_status()
#     fle_list = r.json()[_KEY_FILES]
#     return fle_list

# def test_file_remove(url, auth, tst_uid, fle_uids):

#     endpoint = "{:s}/{:s}/{:s}/{:s}/".format(url, _EP_TESTS, tst_uid, _EP_FILES)
#     d = {_KEY_FILES: fle_uids}
#     dj = json.dumps(d)
#     r = requests.delete(endpoint, auth=auth, data=dj)
#     r.raise_for_status()
#     fle_list = r.json()[_KEY_FILES]
#     return fle_list
