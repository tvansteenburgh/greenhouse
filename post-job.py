#!/usr/bin/env python3

import argparse
import contextlib
import os
import time

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import selenium.webdriver.support.ui as ui


SSO_EMAIL = os.getenv('SSO_EMAIL')
SSO_PASSWORD = os.getenv('SSO_PASSWORD')
NO_AUTH = not (SSO_EMAIL and SSO_PASSWORD)

SITE = 'https://canonical.greenhouse.io'
JOB_BOARD = 'Canonical - Jobs'

REGIONS = {
    'americas': [
        # United States
        'Home based - Americas, Atlanta',
        'Home based - Americas, Austin',
        'Home based - Americas, Boston',
        'Home based - Americas, Chicago',
        'Home based - Americas, Colorado',
        'Home based - Americas, Dallas',
        'Home based - Americas, Los Angeles',
        'Home based - Americas, New York',
        'Home based - Americas, Raleigh',
        'Home based - Americas, San Francisco',
        'Home based - Americas, Seattle',
        # Canada
        'Home based - Americas, Calgary',
        'Home based - Americas, Montreal',
        'Home based - Americas, Ottawa',
        'Home based - Americas, Toronto',
        'Home based - Americas, Vancouver',
        'Home based - Americas, Victoria',
        # South America
        'Home based - Americas, Buenos Aires',
        'Home based - Americas, Mexico City',
        'Home based - Americas, Santiago',
        'Home based - Americas, São Paulo',
    ],
    'emea': [
        'Home based - Africa, Cairo',
        'Home based - Africa, Cape Town',
        'Home based - Africa, Lagos',
        'Home based - Africa, Nairobi',
        'Home based - Europe, Amsterdam',
        'Home based - Europe, Ankara',
        'Home based - Europe, Athens',
        'Home based - Europe, Barcelona',
        'Home based - Europe, Berlin',
        'Home based - Europe, Bratislava',
        'Home based - Europe, Brno',
        'Home based - Europe, Brussels',
        'Home based - Europe, Bucharest',
        'Home based - Europe, Budapest',
        'Home based - Europe, Cluj-Napoca',
        'Home based - Europe, Dublin',
        'Home based - Europe, Edinburgh',
        'Home based - Europe, Frankfurt',
        'Home based - Europe, Glasgow',
        'Home based - Europe, Helsinki',
        'Home based - Europe, Istanbul',
        'Home based - Europe, Kraków',
        'Home based - Europe, Lisbon',
        'Home based - Europe, Ljubljana',
        'Home based - Europe, Lyon',
        'Home based - Europe, Madrid',
        'Home based - Europe, Manchester',
        'Home based - Europe, Milan',
        'Home based - Europe, Moscow',
        'Home based - Europe, Munich',
        'Home based - Europe, Oslo',
        'Home based - Europe, Paris',
        'Home based - Europe, Plovdiv',
        'Home based - Europe, Prague',
        'Home based - Europe, Riga',
        'Home based - Europe, Rome',
        'Home based - Europe, Sofia',
        'Home based - Europe, St. Petersburg',
        'Home based - Europe, Stockholm',
        'Home based - Europe, Tallinn',
        'Home based - Europe, Timișoara',
        'Home based - Europe, Vienna',
        'Home based - Europe, Vilnius',
        'Home based - Europe, Warsaw',
        'Home based - Europe, Wrocław',
        'Home based - Europe, Zagreb',
    ],
    'apac': [
        'Home based - Asia Pacific, Auckland',
        'Home based - Asia Pacific, Bangalore',
        'Home based - Asia Pacific, Beijing',
        'Home based - Asia Pacific, Hong Kong',
        'Home based - Asia Pacific, Hyderabad',
        'Home based - Asia Pacific, Seoul',
        'Home based - Asia Pacific, Shanghai',
        'Home based - Asia Pacific, Singapore',
        'Home based - Asia Pacific, Sydney',
        'Home based - Asia Pacific, Taipei',
        'Home based - Asia Pacific, Tokyo',
    ]
}


def parse_args():
    parser = argparse.ArgumentParser(description='Duplicate Greenhouse job postings to multiple locations.')
    parser.add_argument(
        'job_ids', nargs='+',
        help='The numeric Greenhouse job id (the number in the URL when on the Job Dashboard)')
    parser.add_argument(
        '--region', dest='regions', nargs='+', choices=['americas', 'emea', 'apac'],
        help='The regions in which to create job postings')
    parser.add_argument(
        '--browser', dest='browser', choices=['chrome', 'firefox'], default='chrome',
        help='The browser to use (default is chrome)')

    return parser.parse_args()


def main():
    args = parse_args()

    if args.browser == 'firefox':
        browser = webdriver.Firefox()
    else:
        browser = webdriver.Chrome()
    browser.maximize_window()

    new_browser = True

    for job_id in args.job_ids:
        job_posts_page_url = f'{SITE}/plans/{job_id}/jobapp'
        browser.get(job_posts_page_url)

        if new_browser and not NO_AUTH:
            # click Accept Cookies button
            accept_cookies_btn = browser.find_elements_by_xpath('//*[@id="cookie-policy-button-accept"]')
            if accept_cookies_btn:
                accept_cookies_btn[0].click()

            # enter Ubuntu SSO email and password
            email_txt = browser.find_element_by_id("id_email")
            if email_txt:
                email_txt.send_keys(SSO_EMAIL)

            password_txt = browser.find_element_by_id("id_password")
            if password_txt:
                password_txt.send_keys(SSO_PASSWORD)

            continue_btn = browser.find_elements_by_xpath('//button[@name="continue"]')
            if continue_btn:
                continue_btn[0].click()
            new_browser = False

        # pause 60 seconds for 2-factor auth by user
        wait = ui.WebDriverWait(browser, 60) # timeout after 60 seconds
        results = wait.until(lambda browser: browser.find_elements_by_class_name('job-application__offices'))

        # accept cookies so the popup doesn't obstruct clicks
        cookie_accept_btn = browser.find_elements_by_css_selector('#inform-cookies button')
        for btn in cookie_accept_btn:
            try:
                # click can raise if element exists but is in a hidden block
                btn.click()
            except selenium.common.exceptions.ElementNotInteractableException:
                pass

        # click "Got it" button for new tips
        got_it_btn = browser.find_elements_by_xpath('//a[text()="Got it"]')
        if got_it_btn:
            got_it_btn[0].click()

        # minimize trays so they don't obstruct clicks
        trays = browser.find_elements_by_xpath('//div[@data-provides="tray-close"]')
        for tray in trays:
            tray.click()

        multipage = False
        existing_locations = []
        while True:
            # gather all existing job post locations from each page of results
            existing_locations += [result.text.strip('()') for result in results]
            next_page =  browser.find_elements_by_css_selector('a.next_page')
            if next_page:
                multipage = True
                next_page[0].click()
                results = wait.until(lambda browser: browser.find_elements_by_class_name('job-application__offices'))
            else:
                break

        # return to first page of job posts
        if multipage:
            browser.get(job_posts_page_url)

        for region in args.regions:
            region_locations = REGIONS[region]
            new_locations = set(region_locations) - set(existing_locations)
            for location_text in sorted(new_locations):
                publish_location_text = location_text.split(',')[-1].strip()

                duplicate_link = wait.until(lambda browser: browser.find_elements_by_xpath('//*[@id="job_applications"]//tr[1]//a[text()="Duplicate"]'))
                page = duplicate_link[0].get_attribute('href')
                browser.get(page)

                job_name_txt = browser.find_elements_by_xpath('//input[../label="Job Name"]')[0]
                job_name = job_name_txt.get_attribute('value').replace('Copy of ', '').strip()
                job_name_txt.clear()
                job_name_txt.send_keys(job_name)

                post_to = browser.find_elements_by_xpath('//label[text()="Post To"]/..//input[1]')[0]
                post_to.send_keys(JOB_BOARD)
                post_to.send_keys(Keys.ENTER)

                location = browser.find_elements_by_xpath('//label[text()="Location"]/..//input[1]')[0]
                location.send_keys(location_text)

                browser.find_elements_by_xpath('//label[text()="Glassdoor"]/input[1]')[0].click()
                browser.find_elements_by_xpath('//label[text()="Indeed"]/input[1]')[0].click()
                browser.find_elements_by_xpath('//label[text()="Remote"]/input[1]')[0].click()
                publish_location = browser.find_elements_by_xpath('//input[@placeholder="Select location"]')[0]
                publish_location.send_keys(publish_location_text)
                popup_menu_xpath = (
                    f'//ul[contains(@class, "ui-menu")]'
                    f'/li[contains(@class, "ui-menu-item")]'
                    f'/div[contains(text(), "{publish_location_text}")]'
                )
                location_choices = wait.until(lambda browser: browser.find_elements_by_xpath(popup_menu_xpath))
                publish_location.send_keys(Keys.DOWN)
                publish_location.send_keys(Keys.TAB)
                time.sleep(.5)

                # click the Save button
                save_btn = browser.find_elements_by_xpath('//a[text()="Save"]')[0]
                save_btn.click()

                #publish_btns = wait.until(lambda browser: browser.find_elements_by_css_selector('tr.job-application.draft img.publish-application-button'))
                wait.until(lambda browser: browser.find_elements_by_class_name('job-application__offices'))
                publish_btns = browser.find_elements_by_css_selector('tr.job-application.draft img.publish-application-button')
                for btn in publish_btns:
                    btn.click()
                    time.sleep(.2)

        while True:
            results = wait.until(lambda browser: browser.find_elements_by_class_name('job-application__offices'))
            publish_btns = browser.find_elements_by_css_selector('tr.job-application.draft img.publish-application-button')
            for btn in publish_btns:
                btn.click()
                time.sleep(.2)
            next_page =  browser.find_elements_by_css_selector('a.next_page')
            if next_page:
                next_page[0].click()
            else:
                break

if __name__ == '__main__':
    main()
