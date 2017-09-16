from urllib.parse import urlencode
import time

from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver

chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chromeOptions.add_experimental_option("prefs", prefs)
chromeOptions.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
chromeOptions.add_argument("--start-maximized")


def get_website(site, web):
    """


    :param site: A url.
    :param web:
    """
    web.get(site)
    # There are some query parameters sent in the
    if web.find_element_by_css_selector('body > h1').text == 'Access Denied':
        web.refresh()


def close_if_open_survey(web):
    """
    Checks if a specific survey window is visible. If it is, will execuite Javascript to close it.

    :param web: A web driver object.
    """
    try:
        if web.find_element_by_id('IPEinvL'):
            web.execute_script('clWin();')
            return
    except NoSuchElementException as e:
        return


def create_date_string(start_date, end_date):
    # Check in formatting
    c_in = start_date.split("-")
    c_in_day = c_in[2]
    c_in_month = int(c_in[1])
    if c_in_month < 10:
        c_in_month = '0{}'.format(c_in_month - 1)
    c_in_month_year = "{}{}".format(c_in_month, c_in[0])
    # Check out formatting
    c_out = end_date.split("-")
    c_out_day = c_out[2]
    c_out_month = int(c_out[1])
    if c_out_month < 10:
        c_out_month = '0{}'.format(c_out_month - 1)
    c_out_month_year = "{}{}".format(c_out_month, c_out[0])
    return c_in_day, c_in_month_year, c_out_day, c_out_month_year


def build_website_string(check_in_date, check_out_date, hotel_code):
    dates = create_date_string(check_in_date, check_out_date)
    params = {
        'method': 'roomRate',
        'qAdlt': '2',
        'qBrs': 'hi.ex.rs.ic.cp.in.sb.cw.cv.6c.vn.ul.ki.sp.nd.ct',
        'qChld': '0',
        'qCiD': dates[0],
        'qCiMy': dates[1],
        'qCoD': dates[2],
        'qCoMy': dates[3],
        'qGRM': '0',
        'qHtlC': hotel_code.lower(),
        'qPSt': '0',
        'qRRSrt': 'rt',
        'qRef': 'df',
        'qRmP': 'K.O.T.X',
        'qRms': '1',
        'qRpn': '1',
        'qRpp': '20',
        'qRtP': 'IVANI',
        'qSHp': '1',
        'qSlH': hotel_code.lower(),
        'qSmP': '3',
        'qSrt': 'sBR',
        'qWch': '0',
        'srb_u': '1'
    }
    site_string = "https://www.ihg.com/intercontinental/hotels/us/en/reservation/book?{}".format(urlencode(params))
    return site_string


def book_nights(credentials, dates, hotel_code, web):
    assert isinstance(credentials, dict)
    assert 'username' in credentials.keys()
    assert 'pin' in credentials.keys()

    assert isinstance(dates, dict)
    assert 'in' in dates.keys()
    assert 'out' in dates.keys()

    assert isinstance(hotel_code, str)
    hotel_code_upper = hotel_code.upper()

    get_website(build_website_string(dates['in'], dates['out'], hotel_code_upper), web)

    close_if_open_survey(web)

    room_rates_button = web.find_element_by_css_selector(
        '#roomRateRoomType > div:nth-child(1) > div.roomTypeLineItem > div.headerWrapper > div.roomRatesPrice > span.rateTypeLineItemDisplayLink > img')
    room_rates_button.click()

    close_if_open_survey(web)

    time.sleep(2)

    book_room_button = web.find_element_by_css_selector(
        '#roomRateRoomType > div:nth-child(1) > div.rateTypeLineItems > div:nth-child(1) > div > div.rateTypeLineItemRight > div.rateSelectionArea > input')

    close_if_open_survey(web)

    book_room_button.click()

    time.sleep(.5)
    login_form_username = web.find_element_by_id('UHF_username')
    login_form_username.send_keys(credentials['username'])

    close_if_open_survey(web)

    login_form_password = web.find_element_by_id('UHF_password')
    login_form_password.send_keys(credentials['pin'])

    login_button = web.find_element_by_css_selector(
        '#uhf_headerWrapper > div.wallet.walletTransition.show > div.wallet-state.wallet-login-shared.wallet-view > form:nth-child(1) > fieldset > div:nth-child(16) > div > div > button')
    login_button.click()
    time.sleep(5)

    close_if_open_survey(web)

    # web.execute_script("scroll(0, 1000)")
    # time.sleep(.5)
    #
    # save_to_cc_check = web.find_element_by_xpath('//*[@id="guaranteeType6PM1"]')
    # save_to_cc_check.click()
    # time.sleep(.5)
    #
    # terms_and_cond_check = web.find_element_by_id('authorizeTerm')
    # terms_and_cond_check.click()
    #
    # confirm_btn = web.find_element_by_id('btnNext')
    # confirm_btn.click()

    time.sleep(500)

    web.close()
