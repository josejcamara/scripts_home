# Google Photos Scripts

These scripts will allow you to automate some actions over your Google Photos account
- gphotos_download: Download your photos organized by year/month

# Prerequisites

This script uses the Google API and you'll need to enable that feature in your account and create an API user

### Enable Google Photos API Service

- Go to the Google API Console https://console.cloud.google.com/.
- From the menu bar, select a project or create a new project.
- To open the Google API Library, from the Navigation menu, select "APIs & Services" > Library.
- Search for "Google Photos Library API". Select the correct result and click "enable". If its already enabled, click "manage"
- Afterwards it will forward you to the "Photos API/Service details" page.

### Configure "OAuth consent screen"

- Go back to the Photos API Service details page and click on "OAuth consent screen" on the left side (below "Credentials")
- Add a Test user: Follow the steps using the email of the account you want to use for testing the API call
- Go back to dashboard

### Create API/OAuth credentials

- On the left side of the Google Photos API Service page, click Credentials
- Click on "Create Credentials" and create a OAuth client ID
- As application type I am choosing "Desktop app" and give your client you want to use to call the API a name
- Download the JSON file to the created credentials, rename it to "gphotos_credentials.json" and save it in the folder "credentials"

# Usage
Run `gphotos.py -h` for the updated help version

```
positional arguments:
  action                Action to perform
  dest                  Destination folder

options:
  -h, --help            show this help message and exit
  -f FROM, --from FROM  From date (yyyy/mm/dd) (default: today)
  -t TO, --to TO        To date (yyyy/mm/dd) (default: today)
```
For example: `gphotos.py get ~/gphotos -f 2023/12/01`

# Development

## Create virtualenv and install required packages

Create a virtual environment 
> make setup

Activate venv
> source ./venv/bin/activate 

Install requirements 
> make deps

Run Lint analysis
> make lint

Run Test suite
> make test

# References
- https://github.com/polzerdo55862/google-photos-api
- https://max-coding.medium.com/loading-photos-and-metadata-using-google-photos-api-with-python-7fb5bd8886ef
