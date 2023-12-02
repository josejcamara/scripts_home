#!/usr/bin/env python3

"""
This script downloads photos from your Google Photos account

Usage:
    gphotos_download.py from_date to_date

Author's references:
- https://github.com/polzerdo55862/google-photos-api
- https://max-coding.medium.com/loading-photos-and-metadata-using-google-photos-api-with-python-7fb5bd8886ef

"""

import pickle
import os
import json
import datetime
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


def get_items_file(items_df, dirname):
    """ Proper request to download items """
    for index, item in items_df.iterrows():
        response = requests.get(
            item.baseUrl + '=d',  # =d Full resolution instead of transcode
            timeout=30)

        file_name = item.filename
        print(f'  :{index}:>', dirname, file_name)

        # TODO: VIDEOS COME AS PICTURES
        with open(os.path.join(dirname, file_name), 'wb') as f:
            f.write(response.content)
            f.close()


def download_photos(gapi, date_list, main_path, existing_files):
    """ Download all not existing photos into the main path folder structure """
    media_items_df = pd.DataFrame()
    existing_files_df = pd.DataFrame(existing_files)
    existing_files_df = existing_files_df.rename(columns={0: "filename"})

    for ddate in date_list:
        # Get photos from the account
        items_search_df, media_items_df = gapi.get_media_info(
            year=ddate.year,
            month=ddate.month,
            day=ddate.day,
            media_items_df=media_items_df)

        if len(items_search_df) == 0:
            print(f'No media items found for date: {ddate.year} / {ddate.month} / {ddate.day}')

        else:
            # Create folders by year/month
            folder_name = f'{main_path}/{ddate.year}/{ddate.month}'
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)

            # Discard filenames already downloaded
            if existing_files_df.empty:
                not_downloaded_df = items_search_df.copy()
            else:
                not_downloaded_df = pd.merge(
                    items_search_df,
                    existing_files_df,
                    on='filename',
                    how='left',
                    indicator=True).query('_merge=="left_only"')
                # not_downloaded_df.head(2)

            # Download new items
            info_msg = f'{len(not_downloaded_df.index)}/{len(items_search_df.index)}'
            info_msg += f' new items found for date: {ddate.year} / {ddate.month} / {ddate.day}'
            print(info_msg)

            get_items_file(not_downloaded_df, folder_name)


def main(from_date, to_date=None, target_folder="~/gphotos_downloads"):
    """
        Download photos for a selected range of dates
        Date format yyyy/mm/dd
    """
    date_format = '%Y/%m/%d'

    google_photos_api = GooglePhotosApi()

    if to_date is None:
        to_date = datetime.datetime.today().strftime(date_format)

    # Check if target folder exists
    main_path = os.path.expanduser(target_folder)
    if not os.path.isdir(main_path):
        print(f'Target folder "{main_path}" does NOT exists.')
        sys.exit(1)

    # create a list with all dates between start date and today
    sdate = datetime.datetime.strptime(from_date, date_format).date()
    edate = datetime.datetime.strptime(to_date, date_format).date()
    date_list = pd.date_range(sdate, edate-datetime.timedelta(days=1), freq='d')
    print(f'Checking photos from {sdate} to {edate}')

    # Get list of existing photos
    existing_files = [f for dp, dn, fn in os.walk(main_path) for f in fn]
    # existing_files_df = pd.DataFrame(existing_files)
    # existing_files_df = existing_files_df.rename(columns={0: "filename"})
    # existing_files_df.head(2)

    # API call
    download_photos(google_photos_api, date_list, main_path, existing_files)


if __name__ == "__main__":
    # TODO: Check args ...

    main(from_date='2023/11/15')
