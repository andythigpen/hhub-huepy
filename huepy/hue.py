import requests
import json
import os
import sys
import logging

class Api(object):
    def __init__(self, ip=None, username=None):
        self.ip = ip
        self.username = username
        self.devicetype = 'hue.py'

    def discover(self):
        response = self.get('http://www.meethue.com/api/nupnp')
        if len(response) == 0:
            return None
        self.ip = response[0]['internalipaddress']
        return self.ip

    def register(self, username=None):
        if not username:
            username = self.username
        data = {
            'devicetype' : self.devicetype,
            'username'   : username,
        }
        response = self.post(self.api_url, data)[0]
        if 'error' in response:
            raise Exception(response['error']['description'])
        self.username = response['success']['username']

    def delete_user(self, username):
        url = self.config_url + '/whitelist/' + username
        r = requests.delete(url)
        response = r.json()[0]
        if 'error' in response:
            raise Exception(response['error']['description'])

    def get(self, url):
        r = requests.get(url)
        return r.json()

    def post(self, url, data):
        r = requests.post(url, data=json.dumps(data))
        return r.json()

    def put(self, url, data):
        r = requests.put(url, data=json.dumps(data))
        return r.json()

    def delete(self, url):
        r = requests.delete(url)
        return r.json()

    @property
    def api_url(self):
        if not self.ip:
            raise Exception('Bridge IP not set! Try calling discover()')
        return 'http://%s/api' % self.ip

    @property
    def user_url(self):
        if not self.username:
            raise Exception('Username not set! Try calling register()')
        return self.api_url + '/' + self.username

    def __getattr__(self, name):
        if not name.endswith('_url'):
            raise AttributeError
        return self.user_url + '/' + name[:-4].replace('_', '/')

    @property
    def config(self):
        return self.get(self.config_url)

    @property
    def state(self):
        return self.get(self.user_url)

    def groups(self):
        response = self.get(self.groups_url)
        return [Group(self, k, **v) for k,v in response.items()]

    @property
    def group(self):
        return Group(self, None)

    @property
    def all(self):
        return self.group.find('0')

    def lights(self):
        response = self.get(self.lights_url)
        return [Light(self, k, **v) for k,v in response.items()]

    @property
    def light(self):
        return Light(self, None)

class LightResource(object):
    def __init__(self, api, url, cmd, **kwargs):
        self.api = api
        self.url = url
        self.cmd = cmd
        setattr(self, cmd, {})
        self._set_items(**kwargs)
        if len(getattr(self, cmd)) == 0:
            self.load()

    def load(self):
        self._set_items(**self.api.get(self.url))

    def _set_items(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

    def update(self, **kwargs):
        if not hasattr(self, self.cmd):
            setattr(self, self.cmd, {})
        d = getattr(self, self.cmd)
        d.update(kwargs)
        logging.debug('update state: %s', d)
        url = self.url + '/' + self.cmd
        logging.debug('put %s: %s', url, kwargs)
        self.api.put(url, kwargs)

    def __getattr__(self, name):
        '''
        Provide shortcut methods for setting individual state variables.
        It's better to use update() when setting multiple variables at once so
        that only one request is made, but if you only need to change one
        thing at a time, these shortcut methods can be handy.
        '''
        d = getattr(self, self.cmd)
        if name in d:
            def attrfn(value=None):
                if value is not None:
                    d[name] = value
                    self.update()
                    return self
                else:
                    return d[name]
            return attrfn
        raise AttributeError

    @classmethod
    def _find(cls, api, resource_id, collection):
        if str(resource_id).isnumeric():
            return cls(api, str(resource_id))
        for resource in getattr(api, collection)():
            if resource.name == resource_id:
                return resource
        raise Exception('Unable to find %s: %s' % (str(cls).lower(),
                                                   resource_id))

class Group(LightResource):
    def __init__(self, api, groupid=None, **kwargs):
        url = api.groups_url
        if groupid is not None:
            url += '/' + groupid
        self.groupid = groupid
        super(Group, self).__init__(api, url, 'action', **kwargs)

    def find(self, resource_id):
        return Group._find(self.api, resource_id, 'groups')

    def create(self, name, lights):
        light_ids = []
        for light in lights:
            if type(light) == Light:
                light_ids.append(light.lightid)
            else:
                light_ids.append(str(light))
        url = self.api.groups_url
        response = self.api.post(url, {
            'name' : name,
            'lights' : light_ids,
        })
        if len(response) == 0 or 'error' in response[0]:
            raise Exception('Error creating group: %s' % name)
        self.groupid = response[0]['success']['id'].rpartition('/')[-1]
        self.url = self.api.groups_url + '/' + self.groupid
        self.load()
        return self

    def delete(self):
        response = self.api.delete(self.url)
        if len(response) == 0 or 'error' in response[0]:
            raise Exception('Error deleting group: %s' % name)


class Light(LightResource):
    def __init__(self, api, lightid, **kwargs):
        url = api.lights_url
        if lightid:
            url += '/' + lightid
        self.lightid = lightid
        super(Light, self).__init__(api, url, 'state', **kwargs)

    def find(self, resource_id):
        return Light._find(self.api, resource_id, 'lights')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Control Hue lights')
    parser.add_argument('-a', '--address', dest='address',
                        help='hostname/ip of bridge')
    parser.add_argument('-u', '--user', dest='user',
                        help='username')
    parser.add_argument('-l', '--level', dest='level', default='WARN',
                        help='log level')
    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(level=getattr(logging, args.level.upper()))
    ip = args.address
    username = args.user
    api = Api(ip=ip, username=username)
    if not ip:
        ip = api.discover()
        print('Hue bridge discovered at %s' % ip)
    if not username:
        try:
            print('hue.py needs to register with your Hue bridge')
            username = input('Choose a username: ')
            input('Press the link button on your bridge and then press <enter>.')
            api.register(username)
        except Exception as e:
            print('Failed to register: %s' % e)
            sys.exit(1)
    try:
        api.config
    except:
        print('Failed to communicate with the bridge')
        sys.exit(1)
    print('Successfully connected to bridge at ' + ip)

