import os
import datetime
import environs

env = environs.Env(eager=False)
env.read_env()
dirname = os.path.dirname(__file__)
class Config():
    def __init__(self):
        self.POSTGRES_USER = env.str("POSTGRES_USER", default='postgres')
        self.POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD", default='password')
        self.POSTGRES_DB = env.str("POSTGRES_DB", default='postgres')
        self.POSTGRES_HOST = env.str("POSTGRES_HOST", default='localhost')
        self.POSTGRES_PORT = env.int("POSTGRES_PORT", default=5432)

        self.SCRAPER_URL = env.str('SCRAPER_URL', default='https://www.chess.com')
        self.ACCOUNT_NAME = env.str('ACCOUNT_NAME')
        self.ACCOUNT_PASSWORD = env.str('ACCOUNT_PASSWORD')
        self.SCRAPER_DOWNLOAD_PATH = env.str('DOWNLOAD_PATH', default=dirname +  '/downloads')
        self.SCRAPER_TEMP_PATH =  env.str('DOWNLOAD_PATH', default=dirname + '/downloads/temp')
        self.START_DATE = env.str('START_DATE', default=None)
        self.END_DATE = env.str('END_DATE', default=None)

        env.seal()
    
    def postgres_dsn(self):
        return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'