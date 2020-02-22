#!/usr/bin/env python3

import os
import urllib.request
from xml.dom import minidom
import subprocess
import datetime
import collections
import logging
import re
import argparse


class Podcast(collections.namedtuple("Podcast", ["channel", "title", "description", "link", "pubDate", "enclosureUrl"])):

    @staticmethod
    def from_item(item, channel):
        try:
            tag_names = ['title', 'description', 'link', 'pubDate']
            attrs = {}
            for tag_name in tag_names:
                attrs[tag_name] = item.getElementsByTagName(tag_name)[0].firstChild.data
            attrs["enclosureUrl"] = item.getElementsByTagName('enclosure')[0].getAttribute("url")
            return Podcast(channel=channel, **attrs)
        except Exception as e:
            logging.debug("Cannot parse a podcast from the item {!r} because of {!r}.".format(item.toprettyxml(), e))
            return None


class Channel:
    def __init__(self, url, podsdir=None):
        self.url = url
        self.parse()
        self.poddir = os.path.join(podsdir, self.title)
        self.logfile = os.path.join(self.poddir, "podcasts.log")
        os.makedirs(self.poddir, exist_ok=True)
        os.chdir(self.poddir)

    def parse(self):
        dom = minidom.parse(urllib.request.urlopen(self.url))
        try:
            self.node = dom.getElementsByTagName('channel')[0]
            self.title = self.node.getElementsByTagName('title')[0].firstChild.data
        except IndexError:
            self.title = self.url.replace("/", "_")

    def get_items(self):
        return self.node.getElementsByTagName("item")

    def __str__(self):
        return "Channel \"%s\"" % (self.title)


class PodcastManager:
    def __init__(self, podslist="rss.conf", home=os.path.join(os.getenv("HOME"), "Podcasts")):
        self.podslist = podslist
        self.home = home
        self.incomplete_downloads = os.path.join(home, "incomplete downloads")
        os.makedirs(self.incomplete_downloads, exist_ok=True)

    def __add_to_store(self, podcast):
        if podcast.enclosureUrl is not None and podcast.enclosureUrl != "":
            podsstore = open(podcast.channel.logfile, "a+")
            podsstore.write(podcast.enclosureUrl + os.linesep)
            podsstore.close()

    def add_to_skipped(self, podcast):
        self.__add_to_store(podcast)

    def download(self, podcast):
        keepcharacters = (' ', '.', '_')
        d = datetime.datetime.strptime(podcast.pubDate, "%a, %d %b %Y %H:%M:%S %z").isoformat()
        ext = podcast.enclosureUrl.split('.')[-1]
        ext = re.sub("\?.*", "", ext)
        filename = ".".join([d, podcast.title, ext])
        filename = "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()
        if os.path.exists(filename):
            return
        subcommand = u"wget --content-disposition -nc -c \"{episode_url}\" -O \"{filename}\" && mv -v \"{filename}\" \"{channel_home}\" && echo \"{episode_url}\" >> \"{logfile}\"".format(episode_url=podcast.enclosureUrl, filename=filename, channel_home=podcast.channel.poddir, logfile=podcast.channel.logfile)
        subprocess.call(subcommand, cwd=self.incomplete_downloads, shell=True)

    def is_downloaded(self, podcast):
        if os.path.exists(podcast.channel.logfile):
            fd = open(podcast.channel.logfile, "r")
        else:
            return False
        result = False
        line = podcast.enclosureUrl
        for raw in fd:
            if line == raw.strip():
                result = True
                break
        fd.close()
        return result

    def check_channel(self, channel):
        skip_all = False
        download_all = False
        try:
            items = channel.get_items()
        except AttributeError:
            logging.warning("Cannot retrieve podcasts from {channel}!".format(channel=channel))
            return
        for item in items:
            podcast = Podcast.from_item(item, channel)
            if not podcast:
                continue
            if skip_all:
                self.add_to_skipped(podcast)
                continue
            if download_all:
                self.download(podcast)
                continue
            if not self.is_downloaded(podcast):
                action = self.prompt_for_action(podcast)
                if action == 1:
                    self.download(podcast)
                elif action == 2:
                    download_all = True
                    self.download(podcast)
                    continue
                elif action == 3:
                    self.add_to_skipped(podcast)
                elif action == 4:
                    skip_all = True
                    self.add_to_skipped(podcast)
                    continue
                else:
                    exit()

    def prompt_for_action(self, podcast):
        print("Title: %s\nLink: %s\nDate: %s" % (podcast.title, podcast.enclosureUrl, podcast.pubDate))
        return int(input("Choose an action for this podcast (1. Download, 2. Download All, 3. Skip, 4. Skip All 5. Abort): "))

    def check_all_channels(self):
        with open(self.podslist, "r") as channels_file:
            for url in channels_file.readlines():
                channel = Channel(url, self.home)
                logging.info("Checking for new episodes in %s" % (channel))
                self.check_channel(channel)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A simple podcast manager in Python")
    parser.add_argument("-v", "--verbose", help="Enable verbose diagnostics", action="store_true")
    args = parser.parse_args()
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level)
    PodcastManager().check_all_channels()
