import requests

class AuthService:

    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None

    def login(self, username, password):

        try:
            r = requests.post(
                f"{self.base_url}/api/authenticate",
                json={
                    "username": username,
                    "password": password
                }
            )

            self.token = r.json()["id_token"]
            return True

        except:
            return False