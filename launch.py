from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config
from crawler import Crawler
from collections import defaultdict
from functools import partial
import json
import os


def main(config_file, restart, wordFreq, wordCount, subDom, stopwords):
    cparser = ConfigParser()
    cparser.read(config_file)
    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)
    crawler = Crawler(config, restart, wordFreq, wordCount, subDom, stopwords)
    crawler.start()


if __name__ == "__main__":
    try:
        parser = ArgumentParser()
        parser.add_argument("--restart", action="store_true", default=False)
        parser.add_argument("--config_file", type=str, default="config.ini")
        args = parser.parse_args()
        
        if args.restart:
            if os.path.exists('rsrc/wordFreq.json'):
                os.remove('rsrc/wordFreq.json')
            if os.path.exists('rsrc/wordCount.json'):
                os.remove('rsrc/wordCount.json')
            if os.path.exists('rsrc/subDom.json'):
                os.remove('rsrc/subDom.json')

        if os.path.exists('rsrc/wordFreq.json'):
            with open('rsrc/wordFreq.json', 'r') as infile:
                wordFreq = defaultdict(int, json.load(infile))
        else:
            wordFreq = defaultdict(int)
        
        if os.path.exists('rsrc/wordCount.json'):
            with open('rsrc/wordCount.json', 'r') as infile:
                wordCount = defaultdict(int, json.load(infile))
        else:
            wordCount = defaultdict(int)
        
        if os.path.exists('rsrc/subDom.json'):
            with open('rsrc/subDom.json', 'r') as infile:
                subDom = defaultdict(int, json.load(infile))
        else:
            subDom = defaultdict(int)

        with open('rsrc/stopwords.txt', 'r') as infile:
            stopwords = {line.rstrip('\n') for line in infile}

        main(args.config_file, args.restart, wordFreq, wordCount, subDom, stopwords)
    except:
        print('Exit on exception. Saving Files.')
        with open('rsrc/wordFreq.json','w') as outfile:
            json.dump(wordFreq, outfile)
        with open('rsrc/wordCount.json','w') as outfile:
            json.dump(wordCount, outfile)
        with open('rsrc/subDom.json','w') as outfile:
            json.dump(subDom, outfile)
