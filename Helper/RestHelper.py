import requests
import json
import operator
from flask import jsonify

API_HOST = ""
headers = {}

def req(path, query, method, data={}):
    url = API_HOST + path
    print('HTTP Method: %s' % method)
    print('Request URL: %s' % url)
    print('Headers: %s' % headers)
    print('QueryString: %s' % query)
    print('----')

    if method == 'GET':
        return requests.get(url, headers=headers)
    elif method == 'POST':
        return requests.put(url, headers=headers, data=data)
    elif method == 'PUT':
        return requests.post(url, headers=headers, data=data)
    elif method == 'DELETE':
        return requests.delete(url, headers=headers)

class EncoderRestHelper:
    def __init__(self, API_HOST):
        self.API_HOST = API_HOST
        self.API_HEADERS = {'Content-Type': 'application/json'}

    def __del__(self):
        pass

    def get_videoList(self):
        video_list = list()
        url = self.API_HOST + 'content'
        resp = requests.get(url=url)
        respContent = json.loads(resp.text)['content']
        for eachVideo in respContent:
            video_list.append(eachVideo['name'])
        return video_list