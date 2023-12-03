#!/usr/bin/env python3

"""
This script downloads photos from your Google Photos account

Usage:
    gphotos_download.py from_date to_date

"""
import os
import datetime
import sys
import argparse

import requests
import pandas as pd

from google_api import GooglePhotosApi

DATES_FORMAT = '%Y/%m/%d'


def valid_date(s):
    """ Date validation """
    try:
        return datetime.datetime.strptime(s, DATES_FORMAT).date()
    except ValueError as e:
        msg = "Invalid Date {s}"
        raise argparse.ArgumentTypeError(msg) from e


def get_items_file(items_df, dirname):
    """ Proper request to download items """
    for index, item in items_df.iterrows():
        response = requests.get(
            item.baseUrl + '=d',  # =d Full resolution instead of transcode
            timeout=30)

        file_name = item.filename
        print(f'  :{index+1}:>', dirname, file_name)

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
            folder_name = f'{main_path}/{ddate.year}/{ddate.month:02d}'
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


def main(date_from, date_to, target_folder):
    """
        Download photos for a selected range of dates
    """

    google_photos_api = GooglePhotosApi()

    # Check if target folder exists
    main_path = os.path.expanduser(target_folder)
    if not os.path.isdir(main_path):
        print(f'Target folder "{main_path}" does NOT exists.')
        sys.exit(1)

    # create a list with all dates between start date and today
    date_list = pd.date_range(date_from, date_to-datetime.timedelta(days=0), freq='d')
    if len(date_list) == 0:
        print(f'Date list empty. No days between {date_from} and {date_to}')
        sys.exit(5)

    # Get list of existing photos
    print(f'Checking for photos from {date_list[0]} to {date_list[-1]} in {main_path}')
    existing_files = []
    for y in range(date_from.year, date_to.year+1):
        # Too slow, add into download_photos, by year or month!!
        print(os.path.join(main_path, str(y)))
        existing_files.extend(
            [f for dp, dn, fn in os.walk(os.path.join(main_path, str(y))) for f in fn]
            )
    print(f'Found {len(existing_files)} local files. ')

    # API call
    print("Starting download...")
    download_photos(google_photos_api, date_list, main_path, existing_files)


def parse_args():
    """ Manage the arguments received """

    today = datetime.datetime.today().strftime(DATES_FORMAT)

    parser = argparse.ArgumentParser(
        description="Google Photos Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("action", help="Action to perform", choices=["get"])
    parser.add_argument("dest", help="Destination folder")
    parser.add_argument("-f", "--from", help="From date (yyyy/mm/dd)", default=today, type=valid_date)
    parser.add_argument("-t", "--to", help="To date (yyyy/mm/dd)", default=today, type=valid_date)

    config = parser.parse_args()

    return vars(config)


if __name__ == "__main__":
    args = parse_args()

    try:
        main(date_from=args["from"], date_to=args["to"], target_folder=args["dest"])
    except KeyboardInterrupt as ex:
        print("\nProcess stopped by the user", type(ex))
