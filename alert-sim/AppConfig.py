from requests.auth import HTTPBasicAuth
from urlpath import URL

from dataclasses import dataclass

@dataclass
class AppConfig:
    apiBaseUrl = URL("https://dev.api.ps2alerts.com")
    auth = HTTPBasicAuth("ps2alerts", "foobar") # default dev auth
