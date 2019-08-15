from __future__ import print_function
import logging as logme
import asyncio, tqdm
from asyncio import get_event_loop, TimeoutError, ensure_future
from datetime import datetime
from bs4 import BeautifulSoup
import twint
from twint import dbmysql, run, Config, user
from twint import datelock, feed, get, output, verbose, storage
from twint.dbmysql import non_query
from twint import threadfactory, dbmysql
from twint.cli import config
from time import sleep, strftime, gmtime
from multiprocessing import Pool, freeze_support, RLock
from timeit import timeit
from tqdm import trange


def dbaseconfig():
    c = config.Config()
    c.hostname = "192.168.0.1"
    c.mysqldatabase = "twintdb"
    c.DB_user = "root"
    c.DB_pwd = "pass123"
    return c

def CFollow(username):
    c = dbaseconfig()
    c.Username = username
    # c.User_full = True
    c.Hide_output = True
    c.Stats = True
    c.Count = True
    run.Followers(c)


def CFollowing(username):
    c = dbaseconfig()
    c.Username = username
    c.Hide_output = True
    run.Following(c)


def CUsersfromdatabase(query):
    c = dbaseconfig()
    c.User_full = True
    # c.Hide_output = True
    c.Stats = True
    c.Count = True
    # c.Username = _user
    c.usersfromdatabase = query
    print("done")
    run.Followers(c)


def Clookup(username):
    c = dbaseconfig()
    c.Username = username
    run.Lookup(c)


# get tweets from search
def CSearch(Search):
    c = dbaseconfig()
    c.search_name = str(Search)
    c.Limit = "20000"
    c.Since = "2019-04-13"
    c.Until = "2019-08-15"
    c.Search = Search
    run.Search(c)


# mysql threaded function updates to user_full to users table from query
def Cthread_lookup_fromlist(query):
    c = dbaseconfig()
    c.usersfromdatabase = query
    c.User_full = True
    c.Stats = True
    c.Count = True
    c.thread_qty = 50
    c.thread_type = "lookup_profile"
    # TODO add type to threadfactory for simultaneous find followers from multiple users
    get_event_loop().run_until_complete(threadfactory.start(c))
    print("Finished")


def multi_test():
    group = asyncio.gather(CFollow("wbpnetdotorg"), CFollow("munacra"))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(group)


# do everything before an auto follow / un-follow query
def update_me(username):
    c = dbaseconfig()
    my_user = ClookupUser(username)
    print(f"{username} Following= {my_user.following}  Followers= {my_user.followers}  ")
    CFollow(username)
    CFollowing(username)
    # Cthread_lookup_fromlist("Select * from get_my__missing_followers_profiles")
    # non_query(c, "call youruserupdate")

# pulls user constructor
def ClookupUser(username):
    c = dbaseconfig()
    c.Username = username
    url = f"https://twitter.com/{username}?lang=en"
    loop = asyncio.get_event_loop()
    response = loop.run_until_complete(get.Request(url))
    usr = user.User(BeautifulSoup(response, "html.parser"))
    return usr

def logtwint(query):
    c = dbaseconfig()
    non_query(c, query)


# this gets all profiles from a mssql query
# Cthread_lookup_fromlist("select user from followers_names limit 10")

# update users table using threadfactory to fetch full user profiles
query = "select * from users"

Cthread_lookup_fromlist(query)


# todo add logging to twintmysql functions
# query2 = "insert into logtwint (message) values ('test')"
# logtwint(query2)

# this is the code to use to get single profiles
# Clookup('username')


# this pulls the followers names only or full profiles
# just take off c.User_full = True to get the names only  c.Hide_output = True to blank output
# to do :
# get followers from 1 shot at profile in User
# use a progress bar with followers as 100%

# ***************************
# updates my profile and does everything for follow / un-follower
# update_me("datagram1")
# ***************************

# my_user = ClookupUser("me")
# print(f"me Following= {my_user.following}  Followers= {my_user.followers}  ")


# CFollowing("testuser")

# pull tweets to database tweets table
# daily schedule to monitor
# CSearch("news")


# todo progress bar
# Some decorations basic bar
# import tqdm
# for i in tqdm.trange(int(1e8), miniters=int(1e6), ascii=True,
#                     desc="Followers", dynamic_ncols=True):
#    pass


# simple progress bar
# for j in trange(66, leave=True):
#    sleep(0.1)
#    pass