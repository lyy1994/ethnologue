from __future__ import division

import argparse
import logging
import json
import time
import os
import sys
import random
import urllib.error
from string import ascii_lowercase
from bs4 import BeautifulSoup
from urllib import request
from urllib.request import urlopen, Request


# proxy = {'http': '218.108.168.68:82'}  # set your own ip proxy
# proxy_support = request.ProxyHandler(proxy)
# opener = request.build_opener(proxy_support)
# request.install_opener(opener)


USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]


BASE_URL = "https://www.ethnologue.com/"
LINK = "https://www.ethnologue.com/browse/families"

lang2group = {}

# Define the root loggers
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=os.environ.get("LOGLEVEL", "INFO").upper(),
    stream=sys.stdout,
)
logger = logging.getLogger("ethnologue_scraper")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler("scraper.log", encoding="utf-8"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Tool to crawl language family information.",
    )
    # fmt: off
    parser.add_argument('--init', '-i', type=str, default=None, metavar='CODE',
                        help='The language code we start with (used to resume).')
    parser.add_argument('--path', '-p', type=str, default="lang2group.json", metavar='FILE',
                        help='The json file path that stores the dictionary.')
    # fmt: on
    args = parser.parse_args()
    print(args)

    init = args.init

    for alphabet in ascii_lowercase:
        while True:
            try:
                req = urlopen(Request(BASE_URL + "browse/codes/{}".format(alphabet), headers={'User-Agent': random.choice(USER_AGENTS)}))
                break
            except KeyboardInterrupt as e:
                raise e
            except urllib.error.HTTPError:
                continue
        page = BeautifulSoup(req).find("tbody")
        for row in page.find_all("tr"):
            for col in row.find_all("td"):
                link = col.find("a", href=True)
                if link is not None:
                    # time.sleep(random.randint(1, 3))  # Sleep for a random second to avoid ip blocking
                    if init is not None:
                        if link.text == init:
                            init = None
                        else:
                            continue
                    while True:
                        try:
                            tmp_req = urlopen(Request(BASE_URL + link["href"], headers={'User-Agent': random.choice(USER_AGENTS)}))
                            break
                        except KeyboardInterrupt as e:
                            raise e
                        except urllib.error.HTTPError:
                            continue
                    node = BeautifulSoup(tmp_req).find("div", class_="views-field views-field-field-subgroup")
                    if node is not None and node.span.text == 'Classification':
                        item_list = node.find("div", class_="field-content").find_all("span")
                        lang2group[link.text] = [item.text for item in item_list if item.text != "›"]
                        logger.info("{}: {}".format(link.text, " › ".join(lang2group[link.text])))  # separate by "›"
                    else:
                        lang2group[link.text] = None
                        logger.info("{}: {}".format(link.text, None))

    # Save the lang2group dictionary
    print("Save the dictionary to {}".format(args.path))
    json.dump(lang2group, open(args.path, "w"))
