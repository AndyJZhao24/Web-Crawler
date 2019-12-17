from utils import get_logger
from crawler.frontier import Frontier
from crawler.worker import Worker

class Crawler(object):
    def __init__(self, config, restart, wordFreq, wordCount, subDom, stopwords, frontier_factory=Frontier, worker_factory=Worker):
        self.config = config
        self.logger = get_logger("CRAWLER")
        self.frontier = frontier_factory(config, restart)
        self.workers = list()
        self.worker_factory = worker_factory
        self.wordFreq = wordFreq
        self.wordCount = wordCount
        self.subDom = subDom
        self.stopwords = stopwords

    def start_async(self):
        self.workers = [
            self.worker_factory(worker_id, self.config, self.frontier, self.wordFreq, self.wordCount, self.subDom, self.stopwords)
            for worker_id in range(self.config.threads_count)]
        for worker in self.workers:
            worker.start()

    def start(self):
        self.start_async()
        self.join()

    def join(self):
        for worker in self.workers:
            worker.join()
