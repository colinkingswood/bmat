from django.test import TestCase

# Create your tests here.
import requests
import simplejson as json

url = "127.0.0.1:8000/add_channel/"
data = {'name': 'channel_name'}
json_data = json.dumps(data)
requests.post(url, data=json_data)