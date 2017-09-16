from requests import post, get
from time import sleep, time
from dateutil import rrule
from datetime import datetime, timedelta
from random import randint
from os import environ
from twilio.rest import TwilioRestClient
from telepot import Bot
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout
from hashlib import md5
from sys import argv
from selenium import webdriver
from booking import book_nights, chromeOptions

# Hotel Configuration
# Name of the hotel isn't as important as the Hotel Code,
# The name is just for pretty notifications
hotel_name = 'Intercontinental Thalasso Bora Bora'
# Hotel Code is how the tool knows which hotel to check, you can get the Hotel Code from the website URL
# I.E
# https://www.ihg.com/intercontinental/hotels/us/en/faa-a/bobhb/hoteldetail?qRef=rr&qDest=Intercontinental%2Bresor...
#                                                         ^^^^^
hotel_code = 'BOBHB'

# Search Range
# This requires a monthly range, you cannot set this to weeks, because IHG's API
# searches in two month sets.
# Uses Python's datetime to create a datetime object for today.
start_date = datetime.now()
# End date. Just takes the start date and adds a year to it.
end_date = start_date + timedelta(days=365)

# Hashes file location
# The script gets the nights and creates a hash from them, every check it will make sure the hash
# isn't the same before sending another message, this is to prevent spam and will only send text message
# alerts once there is a change.
# If you would like to not use hashes for spam control, set this variable to None.
path_to_hashes_file = './hashes.txt'

# Twilio Client
use_twilio = False
if use_twilio:
    TWILIO_AUTH_TOKEN = environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_ACCOUNT_SID = environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_PHONE_NUMBER = environ.get("TWILIO_PHONE_NUMBER")
    client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# List of numbers be receiving the results of this scape.
# Must be in acceptable Twilio phone number format I.E +15555555555
recipients = []

# Telegram Bot API
# Used to send status messages for successful changes or error reports.
# If you don't want to use Telegram for status reporting, set this variable to None
telegram_bot_token = None  # environ.get('TELEGRAM_BOT_TOKEN')
if telegram_bot_token:
    bot = Bot(telegram_bot_token)
    # Your Telegram Chat ID, where the Telegram Bot sends a message
    scrape_admin_chat_id = environ.get('TELEGRAM_CHAT_iD')

# Auto-Booking
# This requires that you have the chromedriver installed for Selenium
# Auto-Booking Toggle, if you don't want to use it, then set to false.
"""
    AUTO-BOOKING HAS ONLY BEEN TESTED TO WORK WITH BORA BORA THALASSO HOTEL.
    EVERY HOTEL PAGE MOST LIKELY DIFFERENT HTML SO THE SCRIPT WILL NOT WORK.
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


# Sends the requests to get the status of the rooms.
def get_availability_status():
    post_url = 'https://www.ihg.com/intercontinental/hotels/us/en/reservation/bulkavail'
    post_headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.8,ru;q=0.6',
        'adrum': 'isAjax: true',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'origin': 'http://www.ihg.com',
        'x-requested-with': 'XMLHttpRequest',
    }

    list_of_dates = []

    # This will toggle from True to False because it only needs to send every other result in the range.
    # Quick and dirty way to send a request for every other month.
    # Start at True
    check = True
    for dt in rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date):
        start_month = str(dt).split(" ")[0].split("-")[1]
        start_year = str(dt).split(" ")[0].split("-")[0]
        form_data = {
            'hotelCode': hotel_code,
            'rateCode': 'IVANI',
            'startMonth': int(start_month),
            'startYear': int(start_year)
        }
        try:
            # If check is True it will send a request for that month.
            if check:
                print("Getting availability for {}-{}".format(start_month, start_year))

                req = post(url=post_url, data=form_data, headers=post_headers, timeout=10)
                if req.status_code == 200:
                    new_json = req.json().copy()
                    del new_json['env']
                    if 'availabledate' in new_json:
                        print(new_json['availabledate'])
                        list_of_dates += new_json['availabledate']
                    elif 'errMessage' in new_json:
                        print(new_json['errMessage'][0])
                        pass
                    # Sets to false so the next request doesn't send.
                    check = False
                else:
                    print('Request failed, they maybe onto us.')
            # If check is false, the previous request was sent, this month can be skipped.
            else:
                # Sets back to True so the next request goes through.
                check = True
        except ConnectionError as e:
            message = 'Request for {}-{} has failed.'.format(start_month, start_year)
            print(message)
            send_bot_error_message(message)
            pass
        except ReadTimeoutError as e:
            message = 'Request for {}-{} has failed.'.format(start_month, start_year)
            print(message)
            send_bot_error_message(message)
            pass
        except ReadTimeout as e:
            message = 'Request for {}-{} has failed.'.format(start_month, start_year)
            print(message)
            send_bot_error_message(message)
            pass
        except Exception as e:
            message = 'Request for {}-{} has failed.'.format(start_month, start_year)
            print(message)
            send_bot_error_message(message)
            pass
        # Adds a 0 - 5 second pause between requests. Be respectful to the server.
        # Trust me, removing this sleep will not cause you to lose the room.
        # It's more likely that your IP will be blocked.
        sleep(randint(0, 5))
    return sorted(set(list_of_dates))


def write_hash_to_file(item):
    print("Updates file with {}".format(item))
    file = open(path_to_hashes_file, 'w')
    file.write(str(item))


def read_hash_from_file():
    file = open(path_to_hashes_file, 'r')
    return file.read()


def send_bot_message(m, runtime, total_recipients, prev_hash, curr_hash):
    msg = """<b>IHG Scrape Report</b>
    
Here is the scrape report for the following hotel:
<b>{}</b>

<b>Text Message:</b>
<pre>{}</pre>

<b>Total Runtime:</b> <code>{} seconds</code>
<b>Total Message Recipients:</b> <code>{}</code>
<b>Recipients:</b>
<pre>{}</pre>
    """.format(hotel_name, m, runtime, len(total_recipients), '\n'.join([str(item) for item in total_recipients]))
    if prev_hash and curr_hash:
        msg += "\n\n<b>Previous Hash:</b> <code>{}</code>\n<b>New Hash:</b> <code>{}</code>"
    bot.sendMessage(chat_id=scrape_admin_chat_id, text=msg, parse_mode="HTML")


def send_bot_error_message(m):
    msg = """<b>IHG Scrape Error Report</b>

There was an error with the scrape.

Message:
<code>{}</code>

Arguments:
<code>{}</code>
        """.format(m, " ".join(argv))
    bot.sendMessage(chat_id=scrape_admin_chat_id, text=msg, parse_mode="HTML")


def send_text_message_alert(text_message):
    for recipient in recipients:
        text_message = client.messages.create(
            to=recipient,
            from_=TWILIO_PHONE_NUMBER,
            body=text_message)


if __name__ == '__main__':
    # Captures the start time of the script, this is to time the total scape time.
    start_time = time()

    print('\n\nChecking Reward Night Availability Status for {} ({})\n\n'.format(hotel_name,
                                                                                 hotel_code))
    # Gets the scraped data from the site.
    status = get_availability_status()
    # If the data returns as an error String then it will not do anything,
    # otherwise if a list of dates comes back, it will send a text message to
    # a phone number.
    if status:
        if isinstance(status, list):
            # Starts booking process
            book_nights(credentials, dates=status, hotel_code=hotel_code, web=web)

            available_dates = "\n".join(status)
            alert_message = "There is availability at the {} for the follow dates:\n{}\n\n" \
                            "Book now!".format(hotel_name, available_dates)

            if len(alert_message) > 1599:
                print('\n\nToo many available dates to send a text message. Please reduce your search date range.\n\n')

            # Checks if hashes/spam control is enabled.
            if path_to_hashes_file:
                previous_hash = read_hash_from_file()
                current_hash = md5(bytes(alert_message, 'utf-8')).hexdigest()
                if current_hash != previous_hash:
                    # Writes the new hash to file.
                    write_hash_to_file(current_hash)

                    if use_twilio:
                        # Sends the alert message via SMS.
                        # This is the perfect place to change the alert medium, if you want to use Email or something
                        # You can write your own function that takes in the alert message and sends it which ever way
                        # you want.
                        send_text_message_alert(alert_message)

                    # Capture the time that the scrape finished
                    end_time = time()

                    if telegram_bot_token:
                        # Sends the report message via Telegram
                        send_bot_message(alert_message, int(end_time - start_time), recipients, previous_hash,
                                         current_hash)
            else:
                # If Twilio is enabled a text message will be sent to the list of recipients.
                if use_twilio:
                    send_text_message_alert(alert_message)
                # Capture the time that the scrape finished
                end_time = time()

                if telegram_bot_token:
                    # Sends the report message via Telegram
                    send_bot_message(alert_message, int(end_time - start_time), recipients, None, None)
