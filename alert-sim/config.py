from requests.auth import HTTPBasicAuth
from urlpath import URL

@dataclass
class Config:
    baseUrl = URL("https://dev.api.ps2alerts.com")
    auth = HTTPBasicAuth("ps2alerts", "foobar") # default dev auth
