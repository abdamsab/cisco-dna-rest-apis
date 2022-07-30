
import requests
from requests.auth import HTTPBasicAuth

apicem = {
  "host":"sandboxdnac.cisco.com",
  "port":"443",
  "username":"devnetuser",
  "password":"Cisco123!"
}

def apic_login(host, username, password):
    """
    Use the REST API to log into an APIC-EM and retrieve ticket
    """

    url = "https://{}/api/system/v1/auth/token".format(host)

    # Make login request and return the response body
    response = requests.request("POST", url, auth=HTTPBasicAuth(username, password), verify=False)

    print(response.text)

apic_login(apicem["host"], apicem["username"], apicem["password"])