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
TODO

# Development

## Create virtualenv and install required packages

Create a virtual environment 
> python3 -m venv venv

Activate it 
> . ./venv/bin/activate 

Install requirements 
> pip install -r requirements.txt

# References
- https://github.com/polzerdo55862/google-photos-api
- https://max-coding.medium.com/loading-photos-and-metadata-using-google-photos-api-with-python-7fb5bd8886ef
