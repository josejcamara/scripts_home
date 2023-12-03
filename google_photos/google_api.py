#!/usr/bin/env python3

"""
List of classes using the Google API
"""

import pickle
import os
import json
import sys

import requests
import pandas as pd

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GooglePhotosApi:
    """ Class for the Google Photos API """
    SCOPE_READ_ONLY = ['https://www.googleapis.com/auth/photoslibrary.readonly']
    API_NAME = 'photoslibrary'
    API_VERSION = 'v1'
    CREDENTIALS_FOLDER = '_secrets_'
    SERVICE_ACCOUNT_FILE = 'gphotos_credentials.json'

    def __init__(self,
                 api_name=API_NAME,
                 client_secret_file=os.path.join(CREDENTIALS_FOLDER, SERVICE_ACCOUNT_FILE),
                 api_version=API_VERSION,
                 scopes=None):    # ['https://www.googleapis.com/auth/photoslibrary']):
        '''
        Args:
            client_secret_file: string, location where the requested credentials are saved
            api_version: string, the version of the service
            api_name: string, name of the api e.g."docs","photoslibrary",...
            api_version: version of the api

        Return:
            service:
        '''

        # Check credentials for the API
        if not os.path.exists(GooglePhotosApi.CREDENTIALS_FOLDER):
            os.makedirs(GooglePhotosApi.CREDENTIALS_FOLDER)

        if not os.path.isfile(client_secret_file):
            print(f'Unable to read credentials file on {client_secret_file}')
            sys.exit(10)

        if scopes is None:
            scopes = self.SCOPE_READ_ONLY

        # Set class variables
        self.api_name = api_name
        self.client_secret_file = client_secret_file
        self.api_version = api_version
        self.scopes = scopes
        self.cred_pickle_file = f'./{self.CREDENTIALS_FOLDER}/token_{api_name}_{api_version}.pickle'

        self.cred = None

    def get_credentials(self):
        """ Gets a pickle file with relevant credentials """
        # Is already a pickle file with relevant credentials
        if os.path.exists(self.cred_pickle_file):
            with open(self.cred_pickle_file, 'rb') as token:
                self.cred = pickle.load(token)

        # if no pickle file, create one using google_auth_oauthlib.flow
        if not self.cred or not self.cred.valid:
            if self.cred and self.cred.expired and self.cred.refresh_token:
                self.cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_file, self.scopes)
                self.cred = flow.run_local_server()

            with open(self.cred_pickle_file, 'wb') as token:
                pickle.dump(self.cred, token)

        return self.cred

    def search_media_on_date(self, year, month, day):
        """ API request for media for a specific date """

        self.get_credentials()

        url_search = 'https://photoslibrary.googleapis.com/v1/mediaItems:search'
        payload = {
                    "filters": {
                        "dateFilter": {
                            "dates": [
                                {
                                    "day": day,
                                    "month": month,
                                    "year": year
                                }
                            ]
                        }
                    }
                    }
        headers = {
            'content-type': 'application/json',
            'Authorization': f'Bearer {self.cred.token}'
        }

        try:
            res = requests.request(
                "POST",
                url_search,
                data=json.dumps(payload),
                headers=headers,
                timeout=10)
        except requests.exceptions.RequestException as ex:
            print('search_media_on_date error', ex.response.text)
            sys.exit(1)

        return res

    def get_media_info(self, year, month, day, media_items_df):
        """
        Args:
            year, month, day: day for the filter of the API call
            media_items_df: existing data frame with all find media items so far
        Return:
            media_items_df: media items data frame extended by the articles found for the specified tag
            items_df: media items uploaded on specified date
        """

        items_list_df = pd.DataFrame()

        # create request for specified date
        search_response = self.search_media_on_date(year, month, day)

        for item in search_response.json().get('mediaItems', []):
            items_df = pd.DataFrame(item)
            items_df = items_df.rename(columns={"mediaMetadata": "creationTime"})
            items_df.set_index('creationTime')
            items_df = items_df[items_df.index == 'creationTime']

            # append the existing media_items data frame
            items_list_df = pd.concat([items_list_df, items_df])
            media_items_df = pd.concat([media_items_df, items_df])

        return (items_list_df, media_items_df)

# ------ GooglePhotosApi ------


if __name__ == "__main__":
    print(GooglePhotosApi)
