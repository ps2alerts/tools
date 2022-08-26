import sys
sys.path.append("..") # Adds higher directory to python modules path. This is so dumb.
import requests
from urllib.parse import urlencode
import urllib3
urllib3.disable_warnings() # Turn off the SSL verification warning log spam

from AppConfig import AppConfig
from service import Logger
log = Logger.getLogger()

class Ps2AlertsApiOps:
    def get(path, query=None):
        if (query):
            if (type(query) is not dict):
                raise Exception('Query was not supplied as a dict and therefore we cannot url parse it')

            queryParams = urlencode(query, doseq=False)
            url = str(AppConfig.apiBaseUrl / path)+'?'+queryParams
        else:
            url = str(AppConfig.apiBaseUrl / path)

        log.debug(url)
        response = requests.get(url, verify=False)
        assert 200 <= response.status_code <= 299, "API request failed!"
        return response.json()
