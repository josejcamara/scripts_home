#!/usr/bin/env python3

"""
This script downloads photos from your Google Photos account

Usage:
    gphotos_download.py from_date to_date

"""
import os
import datetime
import sys

import requests
import pandas as pd

from google_api import GooglePhotosApi


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
    print(f'Checking photos from {sdate} to {edate} into {main_path}')

    # Get list of existing photos
    existing_files = [f for dp, dn, fn in os.walk(main_path) for f in fn]
    # existing_files_df = pd.DataFrame(existing_files)
    # existing_files_df = existing_files_df.rename(columns={0: "filename"})
    # existing_files_df.head(2)

    # API call
    download_photos(google_photos_api, date_list, main_path, existing_files)


if __name__ == "__main__":
    # TODO: Check args ...
    try:
        main(from_date='2023/11/15')
    except KeyboardInterrupt as ex:
        print("\nProcess stopped by the user", type(ex))
