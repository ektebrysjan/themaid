# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.update
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = """D://Dropbox//Utvikling//client_secret.json"""

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.videos().update(
        part="snippet,status,localizations",
        body={
          "id": "YOUR_VIDEO_ID",
          "localizations": {
            "es": {
              "title": "no hay nada a ver aqui",
              "description": "Esta descripcion es en español."
            }
          },
          "snippet": {
            "categoryId": 22,
            "defaultLanguage": "en",
            "description": "This description is in English.",
            "tags": [
              "new tags"
            ],
            "title": "There is nothing to see here."
          },
          "status": {
            "privacyStatus": "private"
          }
        }
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()