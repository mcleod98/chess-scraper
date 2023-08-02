import scraper, parser, config, db
from sqlalchemy import func
import models, db
import asyncio



def scrape_and_parse():
    ''' Runs programs for scraping new results and then parses new results'''
    conf = config.Config()
    session = db.get_session(conf)
    s = scraper.Scraper(config=conf, session=session)
    p = parser.Parser(config=conf, session=session)
    print('scrap')
    asyncio.run(s.scrape())
    print('par')
    p.parse_download_folder()
    session.commit()

if __name__ == '__main__':
    scrape_and_parse()