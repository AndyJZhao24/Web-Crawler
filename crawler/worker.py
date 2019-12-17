from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time
import sys
import json

class Worker(Thread):
    def __init__(self, worker_id, config, frontier, wordFreq, wordCount, subDom, stopwords):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.wordFreq = wordFreq
        self.wordCount = wordCount
        self.subDom = subDom
        self.stopwords = stopwords
        super().__init__(daemon=True)
        
    def run(self):
        print("running worker")
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                with open('rsrc/wordFreq.json','w') as outfile:
                    json.dump(self.wordFreq, outfile)
                with open('rsrc/wordCount.json','w') as outfile:
                    json.dump(self.wordCount, outfile)
                with open('rsrc/subDom.json','w') as outfile:
                    json.dump(self.subDom, outfile)
                break
            try:
                resp = download(tbd_url, self.config, self.logger)
            except:
                print("Disconnected. Saving Files.")
                with open('rsrc/wordFreq.json','w') as outfile:
                    json.dump(self.wordFreq, outfile)
                with open('rsrc/wordCount.json','w') as outfile:
                    json.dump(self.wordCount, outfile)
                with open('rsrc/subDom.json','w') as outfile:
                    json.dump(self.subDom, outfile)
                sys.exit()
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper(tbd_url, resp, self.wordFreq, self.wordCount, self.subDom, self.stopwords)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
