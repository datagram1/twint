import logging as logme
import asyncio
from asyncio import get_event_loop, TimeoutError, ensure_future
from datetime import timedelta, datetime
import threading
import twint
from twint import dbmysql, run, Config
from twint import datelock, feed, get, output, verbose, storage
from twint.storage import db
from twint import threadfactory
from twint.cli import config
from twint.cli import loadUserList

def CFollowing(username):
    c = config.Config()
    c.hostname = "localhost"
    c.mysqldatabase = "twintmysql"
    c.DB_user = "root"
    c.DB_pwd = "password"
    c.Username = username

    run.Following(c)


def CSearch(Search):
    c = config.Config()
    c.hostname = "localhost"
    c.mysqldatabase = "twintmysql"
    c.DB_user = "root"
    c.DB_pwd = "password"
    c.search_name = str(Search)
    c.Limit = "5"
    c.Since = "2019-04-11"
    c.Until = "2019-08-10"
    c.Search = Search
    run.Search(c)


def CProfile(username):
    c = config.Config()
    c.User_full = True
    c.hostname = "localhost"
    c.mysqldatabase = "twintmysql"
    c.DB_user = "root"
    c.DB_pwd = "password"


def CUsersfromdatabase(query):
    c = config.Config()
    c.hostname = "localhost"
    c.mysqldatabase = "twintmysql"
    c.DB_user = "root"
    c.DB_pwd = "password"
    c.User_full = True
    # c.Hide_output = True
    c.Stats = True
    c.Count = True
    # c.Username = _user
    c.usersfromdatabase = query
    # test = dbmysql.loadusersfromdatabase(c.hostname, c.DB_user, c.DB_pwd, c.mysqldatabase, c.usersfromdatabase, "mop")
    print("done")
    run.Followers(c)


def Cuserlist():
    try:

        c = config.Config()
        c.User_full = True
        # c.Profile_full = True
        # c.Hide_output = True
        c.Stats = True
        c.Count = True
        c.pandas_clean = True
        c.userlist = 'test.csv'
        c.Username = 'electr1k'
        # c.favorites = False
        # c.following = False
        # c.followers = False
        # c.retweets = False
        c.usersfromdatabase = False
        # cli.loadUserList('test.csv', "followers")
        _userlist = twint.cli.loadUserList(c.userlist, "profile")
        run.Lookup(c)
        # twint.cli.main(c)
        # run.Followers(c)
        #    c.Query = loadUserList("test.csv", "search")

    except Exception as e:
        logme.critical(__name__ + ':Cuserlist:' + str(e))

def Clookup(username):
    c = config.Config()
    c.User_full = True
    c.hostname = "localhost"
    c.mysqldatabase = "twintmysql"
    c.DB_user = "root"
    c.DB_pwd = "password"
    c.Username = username
    run.Lookup(c)

def Cthread_lookup_fromlist(query):
    c = config.Config()
    c.usersfromdatabase = query
    c.User_full = True
    c.Stats = True
    c.Count = True
    c.hostname = "localhost"
    c.mysqldatabase = "twintmysql"
    c.DB_user = "root"
    c.DB_pwd = "password"
    c.thread_qty = 20
    c.thread_type = "lookup_profile"
    # add type to threadfactory for simultaneous find followers from multiple users
    get_event_loop().run_until_complete(threadfactory.start(c))
    # wait until we wrap up everything else...
    # pending = asyncio.Task.all_tasks()
    # get_event_loop().loop.run_until_complete(asyncio.gather(*pending))
    print("Start Finished")

def CFollow(username):
    c = config.Config()
    c.hostname = "localhost"
    c.mysqldatabase = "twintmysql"
    c.DB_user = "root"
    c.DB_pwd = "password"
    c.Username = username
    #c.User_full = True
    # c.Format =
    c.Hide_output = True
    c.Stats = True
    c.Count = True
    run.Followers(c)


# this is the code to use to get profiles from a mysql query
Clookup('electr1k')

# fill in full profiles from a query with only a username column
# Cthread_lookup_fromlist("select user from followers_names limit 400")
query = "select user from followers_names limit 10"
Cthread_lookup_fromlist(query)
# this pulls the followers names only or full profiles
# just take off c.User_full = True to get the names only  c.Hide_output = True to blank output


# CFollow("user")

