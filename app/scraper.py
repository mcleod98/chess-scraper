import os, asyncio
import time
from pyppeteer import launch

class Scraper():
    def __init__(self, config, session):
        self.session = session
        self.scrape_root = config.SCRAPER_URL
        self.account_name = config.ACCOUNT_NAME
        self.password = config.ACCOUNT_PASSWORD

        self.download_path = os.path.abspath(config.SCRAPER_DOWNLOAD_PATH)
        self.temp_path = os.path.abspath(config.SCRAPER_TEMP_PATH)
        self.browser = None
        self.download_filename = None
        self.init_download_name()
        self._downloads = []
        self.move_new_downloads()
        self.start_date = config.START_DATE
        self.end_date = config.END_DATE

    async def get_browser(self):
        if self.browser == None:
            self.browser = await launch({"headless": False,})
        return self.browser

    async def get_page(self, url):
        print('opening new page')
        browser = await self.get_browser()
        page = await browser.newPage()

        await page.goto(url, timeout=0)
        return page

    async def scrape(self):
        page = await self.get_page(f'{self.scrape_root}/login')
        await self.login(page)
        await self.scrape_archive(page)
        await self.browser.close()

    async def login(self, page):
        homepage = page
        try:
            acc_field, password_field = await homepage.querySelectorAll('.login-input')
            await acc_field.type(self.account_name)
            await password_field.type(self.password)
            time.sleep(1)
            await homepage.click('.ui_v5-button-component')
            time.sleep(1)
            await homepage.click('.ui_v5-button-component')
            time.sleep(1)

        except:
            print('Couldnt find login button')
            pass
    
    def init_download_name(self):
        #searches download folder for the last name used
        last = 0
        for f in os.listdir(self.download_path):
            fname, ext = os.path.splitext(f)
            if ext and int(fname) >= last:
                last = int(fname) + 1
        self.download_filename = str(last)
        return

    def wait_for_new_downloads(self):
        tries = 0
        while len(os.listdir(self.temp_path)) == 0:
            time.sleep(1)
            tries += 1
            if tries > 10:
                raise Exception
        self.move_new_downloads()

    def move_new_downloads(self):
        for f in os.listdir(self.temp_path):
            fname, ext = os.path.splitext(f)
            os.rename(f'{self.temp_path}/{f}', f'{self.download_path}/{self.download_filename}{ext}')
            self._downloads.append(f'{self.download_filename}{ext}')
            self.download_filename = str(int(self.download_filename) + 1)


    async def scrape_archive(self, page):
        #set download destination
        page._client.send('Page.setDownloadBehavior', {'behavior': 'allow', 'downloadPath': self.temp_path})
        pagenum = 1
        while pagenum <= 100:
            url = self.get_archive_url(pagenum, self.end_date, self.start_date)
            await page.goto(url, timeout=0)
            
            # if page loads slowly this may fail because the buttons aren't loaded yet
            # for some reason sleeping to wait for the page to load does not always fix this, this is a reported issue with puppeteer
            # trying multiple times seems to be a good work-around, after the first exception it will find the button properly
            tries = 0
            while tries < 10 and not await self.try_click_buttons(page):
                time.sleep(2)
                tries += 1
            pagenum += 1
            self.wait_for_new_downloads()

    async def try_click_buttons(self, page):
        try:
            await page.click('.archive-games-check-all')
            await page.click('.archive-games-download-button')
            return True
        except:
            return False
    

    def get_archive_url(self, page, end_date, start_date):
        if page:
            page = f'&page={page}'
        else:
            page=''
        if end_date:
            end_date = f'&endDate[date]={end_date}'
        if start_date:
            end_date = f'&startDate[date]={start_date}'
        else:
            start_date = ''
        return f'{self.scrape_root}/games/archive?gameOwner=my_game&gameType=recent&timeSort=desc{start_date}{end_date}{page}'

    def get_recent_downloads(self):
        return self._downloads
    
    def clear_recent_downloads(self):
        self._downloads = []

