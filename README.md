# ppodder

Small python "podcatcher" script, that checks for new favourite podcast episodes and prompts you for action if there are new ones.

# Requirements

ppodder designed to be as platform independent as possible to keep required tools and libraries to minimum. Anyway there is no point in inventing bicycle and not using some extremely great tools. List of dependencies:

* wget (best download manager ever)
* python
* bash shell (needed only for "&&" and "echo", so basically any modern shell)

So if you're running almost any Linux distro you should be good to go. In case you use other OS I'm sure it wouldn't be much of a problem to find and install these dependencies.

# Installation

Install all dependencies listed in "Requirements" section.
Download and drop script (and optionally rss.conf file with podcasts I watch) into desired folder.
By default podcasts will be stored in you home directory in Podcasts folder.
Every episode is stored under it's own folder (which name will be formed as a title of the channel).
List of downloaded and skipped podcasts are stored in podcasts.log file, so you can safely delete this file in case you want to be prompted for actions for episodes in this channel again. Every channel has its own independent log file.

# Usage

Drop url of your favourite podcast into rss.conf file

    echo my_favourite_podcast_url >> rss.conf

For convenience you can grant execution permission to the script

    chmod +x ppodder.py

Launch it

    ./ppodder.py

You'll be prompted for actions to apply for every episode that you haven't marked as skipped (by applying skip action) and haven't downloaded yet.
