import json
import requests
from requests.auth import HTTPBasicAuth
from csv import DictReader

def readFromCsv(filename):
    with open(filename, 'r') as f:
        dict_reader = DictReader(f)
        list_of_dict = list(dict_reader)
        print(list_of_dict)
    return list_of_dict[0]

class Confluence_api():

    def __init__(self):
        self.spacelist = []
        setup_params = readFromCsv('setup.csv')
        self.base_url = setup_params['baseurl']
        self.username = setup_params['username']
        self.token = setup_params['token']
        self.auth = HTTPBasicAuth(self.username, self.token)

    def set_space_permission(self, space_key, usergroup):
        url = f'https://{self.base_url}/wiki/rest/api/space/{space_key}/permission'
        headers = {
                   "Accept": "application/json",
                   "Content-Type": "application/json"
                    }
        payload = json.dumps({
                              "subject": {
                                            "type": "group",
                                            "identifier": "test1_user_group"
                                            },
                              "operation": {
                                            "key": "read",
                                            "target": "space"
                                            },
                              #"_links": {}
                                })
        # Send API-forespørselen
        response = requests.request(
                                 "POST",
                                 url,
                                 data=payload,
                                 auth=self.auth,
                                 headers=headers)
        # Sjekk svaret fra serveren
        if response.status_code == 200:
            print("Lesetilgang er gitt til brukergruppen 'brukere'.")
            print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

        else:
            print("En feil oppstod. Statuskode:", response.status_code)
            print("Feilmelding:", response.text)



