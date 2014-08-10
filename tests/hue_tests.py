import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'huepy'))

import unittest
from unittest import mock
import hue
import json

class ApiTestCase(unittest.TestCase):
    def test_discover(self):
        api = hue.Api()
        mock_request = mock.Mock()
        mock_request.json.return_value = [{
            "id":"123456789",
            "internalipaddress":"192.168.1.10",
            "macaddress":"00:11:22:33:44:55",
            "name":"Philips hue"
        }]
        with mock.patch('hue.requests.get', return_value=mock_request) as m:
            ip = api.discover()
            self.assertEqual(ip, '192.168.1.10')
            self.assertEqual(api.ip, ip)
        m.assert_called_once_with('http://www.meethue.com/api/nupnp')
        mock_request.json.assert_called_once_with()

    def test_discover_empty_response(self):
        api = hue.Api()
        mock_request = mock.Mock()
        mock_request.json.return_value = []
        with mock.patch('hue.requests.get', return_value=mock_request) as m:
            ip = api.discover()
            self.assertEqual(ip, None)
            self.assertEqual(api.ip, None)
        m.assert_called_once_with('http://www.meethue.com/api/nupnp')
        mock_request.json.assert_called_once_with()

    def test_register(self):
        api = hue.Api('192.168.1.10')
        mock_request = mock.Mock()
        mock_request.json.return_value = [{
            'success' : {'username' : 'test'}
        }]
        with mock.patch('hue.requests.post', return_value=mock_request) as m:
            api.register('test')
            self.assertEqual(api.username, 'test')
        m.assert_called_once_with('http://192.168.1.10/api', data=json.dumps({
            'username'   : 'test',
            'devicetype' : 'hue.py'
        }))
        mock_request.json.assert_called_once_with()

    def test_register_error(self):
        api = hue.Api('192.168.1.10')
        mock_request = mock.Mock()
        mock_request.json.return_value = [{
            'error' : {'description' : 'Link button not pressed.'}
        }]
        with self.assertRaises(Exception) as cm:
            with mock.patch('hue.requests.post', return_value=mock_request) as m:
                api.register('test')
                self.assertEqual(api.username, None)
        #FIXME: ordering is not guaranteed with dicts so these tests can fail
        #       seemingly randomly
        m.assert_called_once_with('http://192.168.1.10/api', data=json.dumps({
            'username'   : 'test',
            'devicetype' : 'hue.py'
        }))

class GroupTestCase(unittest.TestCase):
    @mock.patch('hue.requests')
    def test_create_group(self, mock_requests):
        api = hue.Api('192.168.1.10', 'test_user')
        mock_request = mock.Mock()
        mock_request.json.return_value = [{
            'success' : {'id' : '/groups/1'}
        }]
        with mock.patch('hue.requests.post', return_value=mock_request) as m:
            g = api.group.create('test', ['1','2'])
            self.assertEqual(g.groupid, '1')
        m.assert_called_once_with('http://192.168.1.10/api/test_user/groups',
                data=json.dumps({
            'name'   : 'test',
            'lights' : ['1', '2']
        }))
        mock_request.json.assert_called_once_with()

    @mock.patch('hue.requests')
    def test_create_group_error(self, mock_requests):
        api = hue.Api('192.168.1.10', 'test_user')
        mock_request = mock.Mock()
        mock_request.json.return_value = [{
            'error' : {'description' : 'Error creating group'}
        }]
        with self.assertRaises(Exception) as cm:
            with mock.patch('hue.requests.post', return_value=mock_request) as m:
                g = api.group.create('test', ['1','2'])
        m.assert_called_once_with('http://192.168.1.10/api/test_user/groups',
                data=json.dumps({
            'name'   : 'test',
            'lights' : ['1', '2']
        }))
    #TODO test delete group
    #TODO test find group

if __name__ == "__main__":
    unittest.main()
