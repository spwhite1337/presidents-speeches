import os
import json

from urllib.request import urlopen
from bs4 import BeautifulSoup

from tqdm import tqdm

from config import Config, logger


class SpeechDownloader(object):
    """
    Scrape speech text for each president
    """
    url_path = os.path.join(Config.ROOT_DIR, 'presidents_speeches', 'utils', 'urls.json')
    save_dir = Config.RAW_DIR

    def __init__(self):
        # Load urls
        with open(self.url_path, 'r') as fp:
            self.urls = json.load(fp)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def download_speeches(self):
        """
        Scrape Speeches
        """
        logger.info('Downloading Speeches from Miller Center')
        speeches = {}
        for president, urls in tqdm(self.urls.items()):
            pres_speeches, downloaded_urls = [], []
            for url in tqdm(urls):
                # Scrape speech
                try:
                    html = urlopen(url, timeout=10).read()
                    soup = BeautifulSoup(html, features='lxml')
                except Exception as err:
                    logger.info(err)
                    continue
                # Skip first and last paragraphs that are fillers
                paragraphs = soup.findAll('p')[1:-2]
                # Join the text of the speech
                speech = ' '.join([p.text for p in paragraphs[2:] if p is not None])
                # Gather
                pres_speeches.append(speech)
                downloaded_urls.append(url)
            speeches[president] = {'speeches': pres_speeches, 'urls': downloaded_urls}

        logger.info('Saving Speeches')
        with open(os.path.join(self.save_dir, 'speeches.json'), 'w') as fp:
            json.dump(speeches, fp)

        return speeches


def download():
    downloader = SpeechDownloader()
    downloader.download_speeches()
