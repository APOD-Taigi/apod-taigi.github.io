import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class Blogger:
    def __init__(self, client_id, client_secret, refresh_token, api_key):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.api_key = api_key
        self.credentials = self.get_credentials(
            self.client_id, self.client_secret, self.refresh_token
        )
        self.service = build("blogger", "v3", credentials=self.credentials)

    @staticmethod
    def get_refresh_token(client_secrets_file):
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes=["https://www.googleapis.com/auth/blogger"]
        )
        flow.run_local_server()
        credentials = flow.credentials
        refresh_token = credentials._refresh_token
        return refresh_token

    @staticmethod
    def get_credentials(client_id, client_secret, refresh_token):
        res = requests.post(
            "https://www.googleapis.com/oauth2/v4/token",
            data={
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
            },
        )
        res.raise_for_status()
        access_token = res.json()["access_token"]
        credentials = Credentials(access_token)
        return credentials

    def list(self, blog_id):
        done = False
        page_token = None
        while not done:
            res = (
                self.service.posts()
                .list(blogId=blog_id, pageToken=page_token)
                .execute()
            )
            posts = res["items"]
            for p in posts:
                yield p

            page_token = res.get("nextPageToken")
            if not page_token:
                done = True
