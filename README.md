=================
WildAlly
=================

WildAlly connects wildlife rehabilitators to nearby users seeking volunteer experience or assistance with injured/orphaned wildlife. Online listings often omit important information about rehabilitators and can be difficult to find and search; WildAlly allows anyone to find the nearest organization that fits their needs with only a few clicks. Wildlife rehabilitators who open accounts benefit from flexible profile settings and a user-friendly visual analytics system.


### Technology Stack

============  ==============
* Celery      * pygeocoder
* Redis       * Pillow
* SQLite      * Jinja
* SQLAlchemy  * Javascript
* Python      * JQuery
* Flask       * Chart.js
* Passlib     * Bootstrap
============  ==============

|               |               |
| ------------- | ------------- |
| * Celery      | * pygeocoder  |
| * Redis       | * Pillow      |
| * SQLite      | * Jinja       |
| * SQLAlchemy  | * Javascript  |
| * Python      | * JQuery      |
| * Flask       | * Chart.js    |
| * Passlib     | * Bootstrap   |


### Find a Wildlife Rehabilitator

WildAlly will attempt to automatically geolocate the user; users can also enter an address, city, or state to search.
A map will be rendered with markers representing the registered wildlife rehabilitators.
If desired, the user can filter the markers to show only wildlife rehabilitators who offer volunteer opportunities and/or accept various types of animals.
Clicking a marker will open an info window displaying the rehabilitator's contact information, address (if provided), notes, and photos.
Information about the click (current time, filters selected) is saved to the database.

*Note: The map is populated by querying the database for wildlife rehabilitator organization information and animal types.
Because these are represented by two tables with a many-to-many relationship through an intermediary table, animal types can be modified, added, or deleted without altering the code.*


### Wildlife Rehabilitator Tools

If a wildlife rehabilitor wishes to have their information displayed on WildAlly, they can sign up for an account.
The map will automatically create a new marker and info window for each new account created.

*Note: Wildlife rehabilitators often work out of their homes, so in many cases they will prefer not to have their full addresses displayed to users; if they opt out of having their address displayed, their marker will be displayed at an approximate location nearby.*

#### Settings

Wildlife rehabilitators can update individual settings quickly and intuitively with AJAX. A single event handler manages all of the settings. If the address is updated, all of the address fields will be bundled together and updated synchronously; this allows the app to automatically and accurately generate a new geocode for the marker's updated location.

#### Photos

Wildlife rehabilitators can upload photos to be displayed alongside their information on the map. To maintain uniform dimensions (dictated by global variables in server.py), each photo will automatically be cropped. The app analyzes the dimensions of the original image, determines the coordinates to crop from, and uses Pillow to generate the new image. It then performs a check for the user's image filepath, and creates one if it doesn't yet exist. Finally, the image is saved.

#### Analytics

A number of charts are provided to help wildlife rehabilitators understand how and when users are searching for them.
Wildlife rehabilitators can view their markers' clicks over time: today's clicks by hour, this week's clicks by day, and this month's clicks by week.
They can also view a breakdown of the filters selected when the marker was clicked; a chart representing all clicks across the app is provided for comparison.

WildAlly uses Celery with Redis to automatically generate text files containing the JSON utilized to generate the charts.
Every 15 minutes, an independent Celery worker process updates each of these files with click information recently stored to the database.