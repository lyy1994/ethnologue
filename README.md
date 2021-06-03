# Ethnologue Data
## Introduction
This repository contains the language family classification data of 7549 languages provided in [Ethnologue](http://www.ethnologue.com/) (until 2021 June 3rd). These data are stored in **JSON** format. Developers could easily import these data into their projects.

This repository also provides the ISO639-1 and ISO639-3 language code mapping data of 184 common languages. This should help developers to use the language family data, as most existing datasets are named based on ISO639-1 codes, yet the language family data is based on ISO639-3.

In addition, this repository offers the code to scrape the latest language family data from the website of [Ethnologue](http://www.ethnologue.com/) if necessary.

## Loading Data
The language family classification data is stored in the `lang2group.json` file. A Python example to load this data is shown below:

```python
import json
with open("lang2group.json", "r") as f:
    data: dict = json.load(f)
```

Then all the language family classification data are loaded into the `data` variable. It is a dictionary with the following format:

    {
        "ISO639-3 code of language 1": 
        [
            "The name of family category language 1 belongs to",
            "The name of family sub-category language 1 belongs to",
            "The name of family sub-sub-category language 1 belongs to",
            ...
        ],
        "ISO639-3 code of language 2":
        ...
    }

The ISO639-1 and ISO639-3 language code mapping data is stored in the `iso639-3to1.json` file. You can load this data in the same way as in the previous example. The loaded data is also a dictionary with the following format:

    {
        "ISO639-3 code": "ISO639-1 code",
        ...
    }

## Download Data
To download the latest language family data, you need to run `ethnologue_scraper.py`. This code file requires a Python 3.X environment and the `bs4` package installed. The command to download the data is as follows:

```commandline
python ethnologue_scraper.py
```

You can specify the path to store the scaped data by passing the `--path` argument to `ethnologue_scraper.py`. If the downloading process unfortunately failed (very likely due to some network issues), you can resume it by specifying which language (ISO639-3 code) the scraper should starts with, via the `--init` argument. You can find which language the previous unsuccessful download fails in from the log file `scraper.log`.

**IMPORTANT NOTE**: Once the scraper failed, the resumed process not longer visits web pages that belong to the previously failed attempt. In this case, the final generated `.json` file will not contain the crawled data from the previous attempt. To recover those lost data, you need to manually parse `scraper.log`. The following Python code should do this parsing job fine:

```python
data = {}
with open("scraper.log", "r") as f:
    for line in f.readlines():
        code, family = line.strip().split("|")[-1].split(":")
        data[code] = family.strip().split(" › ")
```