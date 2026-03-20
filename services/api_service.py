import requests

class ApiService:

    def __init__(self, api_url):
        self.api_url = api_url

    def send(self, data, token):

        headers = {
            "Authorization": "Bearer " + token
        }

        try:
            r = requests.post(
                self.api_url,
                json=data,
                headers=headers
            )

            return r.status_code

        except:
            return None