# K-AutoBook

## Overview

This program downloads web comics.

## Description

Types available.

|site|method|image|size|note|sample url|
|----|------|-----|----|----|----------|
|[alphapolis](http://www.alphapolis.co.jp/)|meta|direct file|auto| |[⚓](http://www.alphapolis.co.jp/manga/viewManga/46) [⚓](http://www.alphapolis.co.jp/manga/viewOpening/138000030/)|
|[ebookjapan](http://ebookjapan.yahoo.co.jp/)|paging|screen capture|manual|need to specify size for every volume|[⚓](https://ebookjapan.yahoo.co.jp/books/145222/A000100547)|
|[bookpass](https://bookpass.auone.jp/)|paging|canvas data|auto| |[⚓](https://bookpass.auone.jp/pack/detail/?iid=BT000069318400100101&cs=top_freecomics_reco_670&pos=2&tab=1&ajb=3)|
|[bookwalker](https://bookwalker.jp/)|paging|canvas data|auto| |[⚓](https://viewer.bookwalker.jp/browserWebApi/03/view?cid=57c84cf2-7062-4ef9-9071-45fb249c926e)|
|[comicdays](https://comic-days.com/)|meta|direct file (re-rendered)|auto| |[⚓](https://comic-days.com/volume/13932016480030155016)|
|[comicwalker](https://comic-walker.com/)|meta|direct file (decrypted)|auto| |[⚓](https://comic-walker.com/viewer/?tw=2&dlcl=ja&cid=KDCW_MF09000001010005_68)|
|[ganganonline](https://www.ganganonline.com/)|paging|direct file (blob)|auto| |[⚓](https://viewer.ganganonline.com/manga/?chapterId=15502)|
|[linemanga](https://manga.line.me/)|paging|screen capture|auto|need to update cookie|[⚓](https://manga.line.me/book/viewer?id=92dc0b4e-c5d4-4518-9fba-d78fb1e6b0f0)|
|[webace](https://web-ace.jp/)|meta|direct file|auto| |[⚓](https://web-ace.jp/youngaceup/contents/1000053/episode/1092/)|
|[zebrackcomic](https://zebrack-comic.com/)|paging|direct file (blob)|auto| |[⚓](https://zebrack-comic.com/title/37/volume/1498/viewer)|
|[booklive](https://booklive.jp/)|paging|direct file (blob, re-rendered)|auto| |[⚓]('https://booklive.jp/bviewer/s/?cid=208562_003&rurl=https%3A%2F%2Fbooklive.jp%2Findex%2Fno-charge%2Fcategory_id%2FC)|
|[jumpplus](https://shonenjumpplus.com/)|meta|direct file (re-rendered)|auto|use comicdays manager|[⚓](https://shonenjumpplus.com/episode/13932016480031086197)|
## Requirement

* `Python` Python 3 (tested on 3.7.6)
* `pip` (tested on 20.0.2)
* `ChromeDriver` (tested on 80.0.3987.106)

## Install

```shell
    $ git clone https://github.com/umjammer/K-AutoBook.git
    $ cd K-AutoBook
    $ pip install -r requirements.txt
```

## Usage

```shell
    $ pwd
    .../K-AutoBook
    $ ./k_auto_book.py
    Input URL > <specify the url or python script starts with '?'> <option>
```

or

```shell
    $ ./k_auto_book.py <specify the url or python script starts with '?'> <option>
```

### Examples

As input data

```shell
Input URL > https://manga.line.me/book/viewer?id=001si9is
 :
Input URL > https://ebookjapan.yahoo.co.jp/books/154784/A002338262/ {"window_size":{"width":900,"height":1352}}
 :
Input URL > ?[f'https://web-ace.jp/youngaceup/contents/1000032/episode/{n}/' for n in range(615, 655)]
```

As a command line argument

```shell
$ ./k_auto_book.py 'https://zebrack-comic.com/title/1591/volume/9727' 
```

## Author

[kuroneko](https://github.com/amu-kuroneko),
umjammer (modifier)