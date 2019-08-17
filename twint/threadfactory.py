import asyncio
import concurrent.futures
import datetime
import logging
import queue
import sys
import time
import urllib
from . import dbmysql,  user, get
from bs4 import BeautifulSoup
from tqdm import tqdm, trange
from twint import dbmysql, get
from urllib.request import urlopen, Request, urlretrieve
from urllib.error import HTTPError
from datetime import datetime
import asyncio
import logging as logme
import re
from time import gmtime, strftime
import pymysql



def blocks(n, q, config):
    # log.info('running')
    log = logging.getLogger('blocks({})'.format(n))
    # msg = False
    # conn = dbmysql.Conn(config, msg)
    conn = pymysql.connect(host=config.hostname,  # your host, usually localhost
                           user=config.DB_user,  # your username
                           passwd=config.DB_pwd,  # your password
                           db=config.mysqldatabase,  # name of the data base
                           charset='utf8mb4',
                           use_unicode=True)

    timeupdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # log.info(f"timeupdate: {timeupdate}")
    work = q.get()
    if not work:
        return n ** 2
    username = str(work[0])
    config.Username = username
    baduser = re.match('[^a-z,0-9,A-Z,_]', username)
    if baduser:
        return
    url = f"https://twitter.com/{username}?lang=en"
    # test url to see if suspended
    loop = asyncio.new_event_loop()
    response = loop.run_until_complete(get.Request(url))
    # response = get.Request(url)
    date_time = str(datetime.now())

    if response.find("This account has been suspended") != -1:
        log.info(f"https://twitter.com/{username} - account suspended")
        try:
            dbmysql.non_query(config, f"insert ignore into users (id_str, user) VALUES (0, '{username}')")
            # insert_stmt0 = (f"insert ignore into users (id_str, user) VALUES (0, '{username}')")
            insert_stmt = (f"Update users  set suspended = b'1' where user='{username}' ")
            # log.info(insert_stmt)
            cursor = conn.cursor()
            # cursor.execute(insert_stmt0)
            cursor.execute(insert_stmt)
            conn.commit()
            q.task_done()
            return
        except RuntimeError as e:
            log.critical(__name__ + ':blocks: ' + str(e))

    if response.find("Sorry, that page doesn’t exist") != -1:
        try:
            log.info(f"https://twitter.com/{username} - doesn't exist")
            dbmysql.non_query(config, f"insert ignore into users (id_str, user) VALUES (0, '{username}')")
            # insert_stmt0 = (f"insert ignore into users (id_str, user) VALUES (0, '{username}')")
            insert_stmt = (f"Update users set doesntexist = b'1' where user='{username}' ")
            # log.info(f"doesn't exist: {insert_stmt}")
            cursor = conn.cursor()
            # cursor.execute(insert_stmt0)
            cursor.execute(insert_stmt)
            conn.commit()
            conn.close()
            q.task_done()
            return
        except RuntimeError as e:
            log.critical(__name__ + ':blocks: ' + str(e))

    u = user.User(BeautifulSoup(response, "html.parser"))
    joined_date = str(
        datetime.strptime(u.join_date, "%d %b %Y"))  # fix date to mysql YYYY-MM-DD 00:00:00 format

    #cursor = conn.cursor()
    # cursor.execute(f"select user from users where user='{username}'")
    # rows = cursor.fetchall()
    # user_exists = rows

    # log.info(f"userexists: {str(user_exists[0])}   username: {username}")


    # log.info(entry)

    log.info(f"REPLACING:  {username}")
    entry = (u.id, u.name, u.username, u.bio, u.location, u.url, joined_date, u.tweets,
             u.following, u.followers, u.likes, u.media_count, u.is_private, u.is_verified, u.avatar, username,
             timeupdate)

    insert_stmt = (
        "REPLACE INTO users (id_str, name, user, bio, location, url, joined, tweets, following,"
        "followers, likes, media, private, verified, avatar, username, time_update) "
        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    )

    # log.info(f"sql: {insert_stmt}")
    # log.info(f"sql: {insert_stmt} {entry}")
    try:
        # dbmysql.non_query(config, insert_stmt2)
        cursor = conn.cursor()
        # cursor.execute(insert_stmt)
        cursor.execute(insert_stmt, entry)
        conn.commit()
        # log.info(str(insert_stmt) + str(entry))
    except Exception as e:  # cursor as e:
        log.info(f"DEADLOCK UPDATING:  {username}")
        entry = (u.id, u.name, username, u.bio, u.location, u.url, joined_date, u.tweets,
                  u.following, u.followers, u.likes, u.media_count, u.is_private, u.is_verified, u.avatar, username,
                  timeupdate, username)
        insert_stmt = (
            "UPDATE users SET "
            f"id_str = %s, name =  %s, user =  %s, bio =  %s, location =  %s, "
            f"url =  %s, joined =  %s, tweets =  %s,  following =  %s, "
            f"followers =  %s,  likes =  %s,  media =  %s, private =  %s,  "
            f"verified =  %s, avatar =  %s, username =  %s,  time_update =  %s"
            f" where user =  %s"
        )
        insert_stmt2 = (
            "UPDATE users SET "
            f"name =  '{u.name}', user =  '{username}', bio =  '{u.bio}', "
            f"location =  '{u.location}', url =  '{u.url}', joined =  '{joined_date}', "
            f"tweets =  '{u.tweets}',  following =  '{u.following}', "
            f"followers =  '{u.followers}',  likes =  '{u.likes}',  media =  '{u.media_count}', "
            f"private =  '{u.is_private}',  "
            f"verified =  '{u.is_verified}', avatar =  '{u.avatar}', username =  '{username}',  "
            f"time_update =  '{timeupdate}' where user =  '{username}'"
        )
        # dbmysql.non_query(config, insert_stmt2)
        cursor = conn.cursor()
        # cursor.execute(insert_stmt2)
        cursor.execute(insert_stmt, entry)
        conn.commit()
        # log.info(f"timeupdate= {timeupdate}")
        # log.info(f"deadlock sql: {insert_stmt2}")
        pass
        # raise Exception("\r \r Deadlock Username: " + u.username + "error:" + str(e) + "\r" + insert_stmt + "\r \r")

    # log.critical(__name__ + ':post query: ' + str(e))
    # log.info(f"lookup_user Thread= {thread}\t\t Username: {username}")

    # log.info(f"username: {username}")
    q.task_done()
    return n ** 2


def fillq(config):
    _type = "user_list"
    log = logging.getLogger('fillq')
    q = queue.Queue()
    user_list = dbmysql.loadusersfromdatabase(config, _type)
    qsize = len(user_list)
    for i in range(qsize):
         q.put(user_list[i])
    q.join
    log.info(f"qfill: blocking tasks to create from qsize= {qsize}")
    return q, qsize


async def run_blocking_tasks(executor, config):
    log = logging.getLogger('run_blocking_tasks')
    log.info('starting')
    log.info('creating executor tasks')
    q, qsize = fillq(config)
    if not qsize:
        log.info('nothing to download')
        return
    loop = asyncio.get_event_loop()
    try:
        blocking_tasks = [
            loop.run_in_executor(executor, blocks, i, q, config)
            for i in range(int(qsize))
        ]
    except Exception as e:
        log.critical(__name__ + ':run_blocking_tasks: ' + str(e))

    log.info('waiting for executor tasks')
    completed, pending = await asyncio.wait(blocking_tasks)
    # results = [t.result() for t in completed]
    # log.info('results: {!r}'.format(results))

    log.info('exiting')

    # cur.execute(""" INSERT INTO logs (1, 2, 3) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE 1=%s, 3=%s """,
    #            (line[0], line[1], line[2], line[0], line[2]))


