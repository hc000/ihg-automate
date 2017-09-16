# ihg-reward-night-alerter
Script that checks IHG's site for available reward nights

## Requirements
**Python Version:** Tested with Python 3.5.2, but it will probably work with any Python 3.

**Twilio:** The alerts are programmed to be sent via SMS, however you can fork the code and write your own
alerting system. You need a Twilio account and a phone number from Twilio.

**Telegram:** The script is configured to send status messages via Telegram Bot, you can however just use it as the actual alert, just disable Twilio integration and provide a Telegram Bot Token.

##### Using Auto-Booking
To use the Auto booking features, you will need to configure some more options.
You will need to download the [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) for your version of Chrome, but you should probably use Chrome 60.

## Usage

The script will hit an endpoint on the IHG site that checks the reward room availability for a given hotel.

Clone this repo, open `app.py` and configure the script to your liking.

##### Running the Script
I'd recommend using some sort of scheduler on your OS to run the script every couple minutes,
5 minutes worked fine for me.

| OS      |  Running                                             |
|---------|------------------------------------------------------|
| Windows | Use Task Scheduler to run the script every X minutes |
| Linux   | Use cron to run the script every X minutes           |
| Mac     | Use cron or whatever scheduler it has.               |


### Configuration
```python
# Hotel Configuration
# Name of the hotel isn't as important as the Hotel Code,
# The name is just for pretty notifications
hotel_name = 'Intercontinental Thalasso Bora Bora'
# Hotel Code is how the tool knows which hotel to check, you can get the Hotel Code from the website URL
# I.E
# https://www.ihg.com/intercontinental/hotels/us/en/faa-a/bobhb/hoteldetail?qRef=rr&qDest=Intercontinental%2Bresor...
#                                                         ^^^^^
hotel_code = 'BOBHB'
```
The script is configured by the hotel code, which you can get from the URL of the IHG Hotel Site,
they're usually either in the URL path or sometimes in the URL encoded form data.
You can also configure the hotel name, which is just to make the alert a bit more pretty.

```python
# Search Range
# This requires a monthly range, you cannot set this to weeks, because IHG's API
# searches in two month sets.
# Uses Python's datetime to create a datetime object for today.
start_date = datetime.now()
# End date. Just takes the start date and adds a year to it.
end_date = start_date + timedelta(days=365)
```
Search range should datetime objects, configured in months. The API endpoint only takes a month number and a year number,
so whatever range you provide, the only thing sent to the API will be year and month. The API returns results for two months at a time.
Meaning if you ask for 08-2018 it will returns availability for 08 and 09. Due to this, the script will send requests for every other month,
this is probably detectable with some crazy pattern detection, but I wouldn't worry about.

#### Spam Control
```python
# Hashes file location
# The script gets the nights and creates a hash from them, every check it will make sure the hash
# isn't the same before sending another message, this is to prevent spam and will only send text message
# alerts once there is a change.
# If you would like to not use hashes for spam control, set this variable to None.
path_to_hashes_file = "./hashes.txt"
```
By providing a path to the hashes text file, you're enabling the spam control feature. This will prevent the
script from texting you every single time you run it. This will hash the alert message and save it to the file,
and will only send out the alert if the hash is different (I.E new dates).
**It's recommended to enable this if you're using Twilio Integration, as it costs money to send SMS**

#### Twilio
```python
# Twilio Client
TWILIO_AUTH_TOKEN = environ.get('TWILIO_AUTH_TOKEN')
TWILIO_ACCOUNT_SID = environ.get('TWILIO_ACCOUNT_SID')
TWILIO_PHONE_NUMBER = environ.get("TWILIO_PHONE_NUMBER")
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# List of numbers be receiving the results of this scape.
# Must be in acceptable Twilio phone number format I.E +15555555555
recipients = []
```
If you would like to use Twilio SMS integration to send out Text Message alerts for available dates.
You will need to create [Twilio account](https://www.twilio.com) and purchase a phone number.
Once you've got Twilio configured, you can add a list of phone number to the recipients list, starting with the
country code.

#### Telegram
```python
# Telegram Bot API
# Used to send status messages for successful changes or error reports.
# If you don't want to use Telegram for status reporting, set this variable to None
telegram_bot_token = environ.get('TELEGRAM_BOT_TOKEN')
if telegram_bot_token:
    bot = Bot(telegram_bot_token)
    # Your Telegram Chat ID, where the Telegram Bot sends a message
    scrape_admin_chat_id = environ.get('TELEGRAM_CHAT_iD')
    # Select whether or not you heartbeat messages.
    send_heartbeat = False
```
If you would like to use Telegram to send yourself a status report for every scape, then configure the the `telegram_bot_token`, otherwise set it to `None`.
Also provide a chat ID where you'd like the message to the message to be sent. The report message contains basically everything in the alert message plus some debug stuff.

```console
IHG Scrape Report

Here is the scrape report for the following hotel:
Intercontinental Resort Bora Bora Thalasso

Text Message:
There is availability at the Intercontinental Resort Bora Bora Thalasso for the follow dates:
2018-4-6

Book now!

Total Runtime: 47 seconds
Total Message Recipients: 3
Recipients:
+15555555555

Previous Hash: 3341b5fb86718bbbade40ffc1f620039
New Hash: be067f0091a4361c466a4539ef7a9fca
```

It will also send you messages if the script fails to get the available dates as well, those messages look like this:
```console
IHG Scrape Error Report

There was an error with the scrape.

Message:
Request for 08-2017 has failed.

Arguments:
C:\\Users\\Administrator\\Documents\\Python Scripts\\igh-scraper-BOBHB\\app.py
```

#### Auto-Booking
To use auto booking you will need to download the Chrome Driver and provide the path to the script. You will also need to provide your credentials.

**Auto-Booking only works with Bora Bora Thalasso, if you are using this script to monitor a different hotel and you enable Auto-Booking, the script will most likely fail.
If you need another hotel, then you can replace the `book_nights` function with your own.**

```python
# Auto-Booking
# This requires that you have the chromedriver installed for Selenium
# Auto-Booking Toggle, if you don't want to use it, then set to false.
"""
    AUTO-BOOKING HAS ONLY BEEN TESTED TO WORK WITH BORA BORA THALASSO HOTEL.
    EVERY HOTEL PAGE MOST LIKELY DIFFERENT HTML SO THE
"""
use_auto_booking = False
if use_auto_booking:
    # Path to Chromedriver.
    path_to_chromedriver = r'C:/chromedriver.exe'
    web = webdriver.Chrome(executable_path=path_to_chromedriver,
                           chrome_options=chromeOptions)
    # Credentials for logging in
    # These are required to login and book the rooms.
    credentials = {
        'username': None,
        'pin': None
    }
```