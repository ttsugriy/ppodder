#!/usr/bin/python

import os
import urllib
from xml.dom import minidom
import subprocess


class Podcast:
    def __init__(self, title=None, description=None, link=None, pubDate=None, enclosureUrl=None, valid=False):
        self.title = title
        self.description = description
        self.link = link
        self.pubDate = pubDate
        self.enclosureUrl = enclosureUrl
        self.valid = valid

    def fillFromItem(self, item):
        try:
            self.title = item.getElementsByTagName('title')[0].firstChild.data
            self.description = item.getElementsByTagName('description')[0].firstChild.data
            self.link = item.getElementsByTagName('link')[0].firstChild.data
            self.enclosureUrl = item.getElementsByTagName('enclosure')[0].getAttribute("url")
            self.pubDate = item.getElementsByTagName('pubDate')[0].firstChild.data
            self.valid = True
        except IndexError:
            self.valid = False


    def __str__(self):
        return "Podcast(title=%s)" % (self.title)

class Channel:
    def __init__(self, url, podsdir=None):
        self.url = url
        self.parse()
        self.poddir = os.path.join(podsdir, self.title)
        self.logfile = os.path.join(self.poddir,"podcasts.log")
        try:
            os.mkdir(self.poddir)
        except OSError:
            pass
        os.chdir(self.poddir)

    def parse(self):
        dom = minidom.parse(urllib.urlopen("http://" + url))
        try:
            self.node = dom.getElementsByTagName('channel')[0]
            self.title = self.node.getElementsByTagName('title')[0].firstChild.data
        except IndexError:
            self.title = url.replace("/","_")

    def get_items(self):
        return self.node.getElementsByTagName("item")

    def add_to_log(self, podcast):
        podsstore = open(self.logfile, "a+")
        podsstore.write(podcast.enclosureUrl + "\n")
        podsstore.close()

    def is_downloaded(self, podcast):
        fd = open(self.logfile, "r+")
        result = False
        line = podcast.enclosureUrl
        for raw in fd:
            if line == raw.strip():
                result = True
                break
        fd.close()
        return result

    def download(self, podcast):
            subprocess.Popen("wget -c %s" % (podcast.enclosureUrl), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.add_to_log(podcast)

podsdir = os.path.join(os.getenv("HOME"),"Podcasts")

rssfile = open("rss.conf", "r")
for url in rssfile:
    skip_all = False
    channel = Channel(url, podsdir)
    for item in channel.get_items():
        podcast = Podcast()
        podcast.fillFromItem(item)
        if skip_all:
            channel.add_to_log(podcast)
            continue
        if not channel.is_downloaded(podcast) and podcast.valid:
            print "Title: %s\nLink: %s\nDate: %s" % (podcast.title, podcast.enclosureUrl, podcast.pubDate)
            action = int(raw_input("Choose an action for this podcast (1. Download, 2. Skip, 3. Skip All 4. Abort): "))
            if action == 1:
                channel.download()
            elif action == 2:
                channel.add_to_log(podcast)
            elif action == 3:
                skip_all = True
                channel.add_to_log(podcast)
                continue
            else:
                exit()
