# -*- coding: utf-8 -*-
import selenium
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from time import sleep
from os.path import join as p_join
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
import pandas as pd
import argparse
import os

"""
Message: no such element: Unable to locate element: {"method":"xpath","selector":".//a[@class="nextItem"]"}
  (Session info: headless chrome=83.0.4103.61)

"""


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-source',
        help="journals to search from (keyword that will have it come up first in suggestions) split with AND")

    parser.add_argument('-journal_name', help='journal name to format the output file name')
    parser.add_argument('-query', help='query to enter')
    parser.add_argument('-region', help='restrict region of results', default='japan')
    parser.add_argument('-agency_folder', help="which jp agency is being scraped")
    parser.add_argument('-headless', default=True, type=bool)
    args = parser.parse_args()

    return args


class FactivaScraper:
    def __init__(self, query, source, region, output_file, driver, *args, **kwargs):

        self.DateFormatter = None
        self.driver = driver
        self.mcgill_us = 'etienne.gagnon4@mail.mcgill.ca'
        self.mcgill_pass = "Welikemarth1"

        self.output_file = output_file

        self.end_date = self.find_last_dl_date()
        self.start_date = datetime.date(2000, 1, 1)

        self.query_dict = {
            'search_q': query,
            'start_d': self.start_date,
            'end_d': self.end_date,
            'source': source,
            'region': region
        }

    def mcgill_login(self):
        driver = self.driver
        driver.get(
            'http://proxy.library.mcgill.ca/login?'
            'url=http://global.factiva.com/en/sess/login.asp'
            '?xsid=S001WNd3WvyMTZyMTAoNDUuMp6pMdmm5DFHY96oYqZlNFFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFB')

        user_name_box = WebDriverWait(driver, 60).until(EC.presence_of_element_located(
            (By.XPATH, './/input[@name="j_username"]')))

        user_name_box.send_keys(self.mcgill_us)

        password_box = driver.find_element_by_xpath('.//input[@type="password"]')
        password_box.send_keys(self.mcgill_pass)

        submit_button = driver.find_element_by_xpath('.//input[@type="submit"]')
        submit_button.click()

        sleep(30)

    def enter_search_terms(self):
        def enter_date_range():

            date_range = driver.find_element_by_xpath('.//option[@value="Custom"]')
            date_range.click()

            date_range_panel = driver.find_element_by_xpath('.//div[@id="datePnl"]')

            from_d = date_range_panel.find_element_by_xpath('.//input[@id="frd"]')
            from_m = date_range_panel.find_element_by_xpath('.//input[@id="frm"]')
            from_y = date_range_panel.find_element_by_xpath('.//input[@id="fry"]')
            to_d = date_range_panel.find_element_by_xpath('.//input[@id="tod"]')
            to_m = date_range_panel.find_element_by_xpath('.//input[@id="tom"]')
            to_y = date_range_panel.find_element_by_xpath('.//input[@id="toy"]')

            from_d.send_keys(str(self.query_dict['start_d'].day))
            from_m.send_keys(str(self.query_dict['start_d'].month))
            from_y.send_keys(str(self.query_dict['start_d'].year))

            to_d.send_keys(str(self.query_dict['end_d'].day))
            to_m.send_keys(str(self.query_dict['end_d'].month))
            to_y.send_keys(str(self.query_dict['end_d'].year))

            print('selected all dates')

        def enter_source():
            formatted_source = self.query_dict["source"].split(' AND ')

            sleep(2)

            source_arrow = driver.find_element_by_xpath('.//tr[@id="scTrTab"]//div[@class="pnlTabArrow"]')
            source_arrow.click()

            sleep(1)

            for source in formatted_source:
                source_box = driver.find_element_by_xpath('.//tr[@id="sc"]')
                source_name_search = source_box.find_element_by_xpath('.//input[@type="text"]')

                source_name_search.send_keys(source)

                sleep(2)

                source_autosuggest_box = driver.find_element_by_xpath(
                    './/div[@class="dj_emg_autosuggest_results scResultPopup"]')
                first_link = source_autosuggest_box.find_element_by_xpath('.//div')
                first_link.click()

        def enter_search_term():
            sleep(5)
            factiva_search_box = driver.find_element_by_xpath('.//textarea[@name="ftx"]')
            factiva_search_box.send_keys(self.query_dict['search_q'])

            sleep(2)

            print('entered search term')

        def enter_language():
            lang_arrow = driver.find_element_by_xpath('.//tr[@id="laTrTab"]//div')
            lang_arrow.click()

            sleep(1)

            en_filter = driver.find_element_by_xpath('.//a[@code="la_en"]')
            en_filter.click()

            print('english filter is off')

            sleep(4)

            jp_filter = driver.find_element_by_xpath('.//a[@code="la_ja"]')
            jp_filter.click()

            print('jp filter is on')
            sleep(3)

        def enter_region():
            region_search = driver.find_element_by_xpath('.//tr[@id="reTrTab"]')
            region_arrow = region_search.find_element_by_xpath('.//div[@class="pnlTabArrow"]')
            region_arrow.click()

            region_search_box = driver.find_element_by_xpath('.//tr[@id="re"]//input[@type="text"]')
            region_search_box.send_keys(self.query_dict['region'])

            sleep(2)

            japan_suggestion = driver.find_element_by_xpath('.//a[@title="Get details for Japan "]')
            suggestion_clicker = japan_suggestion.find_element_by_xpath('./..')
            suggestion_clicker.click()

            print('clicked region')

            sleep(1)
            search_button = driver.find_element_by_xpath('.//input[@value="Search"]')
            search_button.click()
            sleep(2)

            print('clicked search button')

        driver = self.driver

        enter_search_term()
        enter_language()
        enter_date_range()

        if self.query_dict['region'] is not None:
            enter_region()

        if self.query_dict['source'] is not None:
            enter_source()

        """        
        company_arrow = driver.find_element_by_xpath('.//tr[@id="coTrTab"]//div[@class="pnlTabArrow"]')
        company_arrow.click()

        sleep(2)
        company_search = driver.find_element_by_xpath('.//tr[@id="co"]//input[@type="text"]')
        company_search.send_keys('Japan Ministry of Foreign Affairs')
        sleep(2)
    
        ministry_info = driver.find_element_by_xpath('.//a[@title="Get details for Japan Ministry of Foreign Affairs "]')
        ministry = ministry_info.find_element_by_xpath('./..')
        ministry.click()
    
        print('picked ministry')
        """

    def set_display(self):
        driver= self.driver
        display_type_arrow = driver.find_element_by_xpath('.//span[@id="articleViewAs"]//div[@class="pnlTabArrow"]')
        display_type_arrow.click()

        menu = driver.find_elements_by_xpath('.//div[@class="viewAsMenu"]//li')
        menu[2].click()

    def find_last_dl_date(self):
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                last_dl_file = f.readlines()[-1]

            last_file_split = last_dl_file.split(' SEP ')
            date_field = [field for field in last_file_split if field.startswith('PD')][0]
            last_dl_date = date_field.split(' TAGBREAK ')[1]
            last_dl_date = datetime.datetime.strptime(last_dl_date, '%d %B %Y').date()

            return last_dl_date
        except FileNotFoundError:
            return datetime.date.today()

    def last_date_on_page(self):
        driver = self.driver

        lead_fld = driver.find_elements_by_xpath('.//div[@class="leadFields"]')
        last_article_lead = lead_fld[-1].text
        last_article_date = last_article_lead.split(',')[1]
        last_article_date = last_article_date.strip()

        last_article_datetime = datetime.datetime.strptime(last_article_date, "%d %B %Y")
        date_format = last_article_datetime.date()
        return date_format

    def get_to_remaining_articles(self):
        driver = self.driver
        date_to_reach = self.find_last_dl_date()

        last_date = self.last_date_on_page()
        while last_date > date_to_reach:
            print('skipping 100')

            sleep(5)
            try:
                next_button = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, './/a[@class="nextItem"]')))
                next_button.click()

            except selenium.common.exceptions.ElementClickInterceptedException:
                sleep(15)
                next_button = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, './/a[@class="nextItem"]')))
                next_button.click()
            except selenium.common.exceptions.StaleElementReferenceException as e:
                print(e)
                sleep(15)
                next_button = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, './/a[@class="nextItem"]')))
                next_button.click()

            sleep(5)
            last_date = self.last_date_on_page()

    def scrape_articles_from_page(self, headlines, save_file):
        driver = self.driver
        for one_headline in headlines:
            try:
                one_headline.click()
            except selenium.common.exceptions.NoSuchElementException:
                print('article was not loaded')
                sleep(10)
                one_headline.click()

            article = WebDriverWait(driver, 260).until(EC.presence_of_element_located(
                (By.XPATH, './/div[@class="article jaArticle"]')))


            article_table = article.find_element_by_xpath('.//tbody')
            article_contents = article_table.find_elements_by_xpath('.//tr')

            field_contents = []
            for tr in article_contents:
                td_elems = tr.find_elements_by_xpath('.//td')

                field_val = td_elems[0].text

                if field_val == 'TD':

                    value_content = td_elems[1].find_elements_by_xpath('.//p')
                    value_content = [par.text for par in value_content]
                    value_content = " PARAGRAPHBREAK ".join(value_content)
                else:
                    value_content = td_elems[1].text

                field_write = " TAGBREAK ".join([field_val, value_content])
                field_contents.append(field_write)

            article_string = ' SEP '.join(field_contents)
            article_string = article_string.replace('\n', '')

            save_file.write(article_string)
            save_file.write('\n')
        print('scraped 100 articles')

    def num_articles_cycled(self):
        driver = self.driver
        article_cycled_text = driver.find_element_by_xpath('.//span[@class="resultsBar"]').text
        article_cycled_text = article_cycled_text.split(' of ')[0]
        article_cycled_text = article_cycled_text.replace('Headlines ', '')
        article_cycled_text = article_cycled_text.split(' - ')[1]
        article_cycled_text = article_cycled_text.replace(',', '')
        article_cycled_text = int(article_cycled_text)
        return article_cycled_text

    def cycle_through_pages(self):
        driver = self.driver

        with open(self.output_file, 'a', encoding='utf-8', newline='') as f:
            articles_cycled = self.num_articles_cycled()
            while articles_cycled < 9500:
                try:
                    sleep(3)
                    WebDriverWait(driver, 60).until(EC.presence_of_element_located(
                        (By.XPATH, './/a[@class="jaHeadline"]')))

                    headlines = driver.find_elements_by_xpath('.//a[@class="jaHeadline"]')

                    try:
                        self.scrape_articles_from_page(headlines, f)
                    except selenium.common.exceptions.StaleElementReferenceException:
                        sleep(5)
                        WebDriverWait(driver, 60).until(EC.presence_of_element_located(
                            (By.XPATH, './/a[@class="jaHeadline"]')))
                        refresh_headlines = driver.find_elements_by_xpath('.//a[@class="jaHeadline"]')
                        self.scrape_articles_from_page(refresh_headlines, f)

                    try:
                        sleep(10)
                        next_arrow = driver.find_element_by_xpath('.//a[@class="nextItem"]')
                        next_arrow.click()
                        sleep(10)
                    except selenium.common.exceptions.ElementClickInterceptedException:
                        print('click did not work once')
                        sleep(10)
                        next_arrow = driver.find_element_by_xpath('.//a[@class="nextItem"]')
                        next_arrow.click()
                        sleep(10)

                    articles_cycled = self.num_articles_cycled()
                except KeyboardInterrupt:
                    break
        end_date = self.last_date_on_page()
        return end_date

    def cycle_reset(self):
        driver = self.driver
        new_end_date = self.query_dict['end_d']
        try:
            while new_end_date > self.query_dict['start_d']:
                driver.get(
                    'http://proxy.library.mcgill.ca/login?'
                    'url=http://global.factiva.com/en/sess/login.asp'
                    '?xsid=S001WNd3WvyMTZyMTAoNDUuMp6pMdmm5DFHY96oYqZlNFFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFB')
                sleep(30)
                driver.save_screenshot('cycle_reset.png')
                self.enter_search_terms()
                self.set_display()
                self.get_to_remaining_articles()
                new_end_date = self.cycle_through_pages()
                self.query_dict['end_d'] = new_end_date

                print('resetting cycle')

        except selenium.common.exceptions.NoSuchElementException as e:
            driver.save_screenshot('no_such_elem.png')
            print('could not find element')
            print(e)

        print(f'finished scraping. files stored in {self.output_file}')


def setup_driver(headless=False):
    prefs = {'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             'safebrowsing.enabled': False,
             'safebrowsing.disable_download_protection': True}

    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')

    options.add_experimental_option('prefs', prefs)

    driver = Chrome(options=options)

    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    driver.desired_capabilities['browserName'] = 'my_browser'
    params = {
        'cmd': 'Page.setDownloadBehavior',
        'params': {
            'behavior': 'allow',
            'downloadPath': r'C:\Users\Etienne Gagnon\PycharmProjects\japanese_admin_scrape\agency_articles\外務省'
        }
    }
    driver.execute("send_command", params)

    return driver


def main():
    try:
        args = parse_arguments()

        path_to_agencies = 'agency_articles'

        output_folder = args.agency_folder
        output_file = f'{args.journal_name}_{output_folder}_articles.txt'

        if not os.path.exists(p_join(path_to_agencies, output_folder)):
            os.mkdir(p_join(path_to_agencies, output_folder))

        path_to_output_file = p_join(path_to_agencies, output_folder, output_file)

        driver = setup_driver(headless=args.headless)

        scraper_instructions = FactivaScraper(query=args.query,
                                              source=args.source,
                                              region=args.region,
                                              output_file=path_to_output_file,
                                              driver=driver)

        scraper_instructions.mcgill_login()
        scraper_instructions.cycle_reset()

        driver.save_screenshot('test_screen_shot.png')

    finally:
        driver.close()


if __name__ == "__main__":
    main()

