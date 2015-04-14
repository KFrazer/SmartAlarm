# SmartAlarm
A Smart Alarm clock python script with a tkinter gui. Planned for deployment on Raspberry Pi.


# Note the following dependencies:
*pyglet and AVbin*

This one might give you some trouble. To get AVbin working I had to ultimately download version 8 and


*Weather*

import pywapi

I had to download this and manually and run setup, etc. No pip install available.


*These are all from Google.*

from apiclient.discovery import build

from oauth2client.file import Storage

from oauth2client.client import AccessTokenRefreshError

from oauth2client.client import OAuth2WebServerFlow

from oauth2client import tools

from oauth2client.tools import run_flow

The Google website has instructions for how to install these using pip. It's not
the standard command.


*These I just installed using pip*

from Tkinter

import httplib2

import argparse


I think the rest of the dependencies were built in...
