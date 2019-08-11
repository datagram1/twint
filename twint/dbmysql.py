import sys
from datetime import datetime

import pymysql
import pymysql.cursors
import logging as logme


def Conn(hostname, mysqldatabase, db_user, db_pwd):
    logme.debug(__name__ + ':Conn')
    if mysqldatabase:
        print("[+] Inserting into MySqlDatabase: " + str(mysqldatabase))
        conn = init(hostname, mysqldatabase, db_user, db_pwd)
        if isinstance(conn, str):
            print(str)
            sys.exit(1)
    else:
        conn = ""

    return conn


def init(hostname, mysqldatabase, db_user, db_pwd):
    logme.debug(__name__ + ':init')
    try:
        conn = pymysql.connect(host=hostname,  # your host, usually localhost
                               user=db_user,  # your username
                               passwd=db_pwd,  # your password
                               db=mysqldatabase,  # name of the data base
                               charset='utf8mb4',
                               use_unicode=True)

        cursor = conn.cursor()
        # here would be the code for creating the tables if them don't exist
        return conn
    except Exception as e:
        logme.critical(__name__ + ':dbmysql:' + str(e))


def fTable(Followers):
    logme.debug(__name__ + ':fTable')
    if Followers:
        table = "followers_names"
    else:
        table = "following_names"

    return table


def uTable(Followers):
    logme.debug(__name__ + ':uTable')
    if Followers:
        table = "followers"
    else:
        table = "following"

    return table


def follow(conn, Username, Followers, User):
    logme.debug(__name__ + ':follow')
    try:
        date_time = str(datetime.now())
        cursor = conn.cursor()
        entry = (User, date_time, Username,)
        query = 'INSERT INTO {} VALUES(%s,%s,%s)'.format(fTable(Followers))
        print("dbmysql/def follow query= " + str(query))
        cursor.execute(query, entry)
        conn.commit()
    except pymysql.IntegrityError:
        pass


def user(conn, Username, Followers, User):
    try:
        date_time = str(datetime.now())
        cursor = conn.cursor()
        entry = (User.id,
                 User.name,
                 User.username,
                 User.bio,
                 User.location,
                 User.url,
                 User.join_date,
                 User.join_time,
                 User.tweets,
                 User.following,
                 User.followers,
                 User.likes,
                 User.media_count,
                 User.is_private,
                 User.is_verified,
                 User.avatar,
                 date_time,
                 Username,)
        query = 'INSERT INTO {} VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(uTable(Followers))
        cursor.execute(query, entry)
        conn.commit()

    except pymysql.IntegrityError:
        pass


def tweets(conn, Tweet, config):
    try:
        date_time = str(datetime.now())
        cursor = conn.cursor()
        entry = (Tweet.id,
                 Tweet.user_id,
                 Tweet.datestamp,
                 Tweet.timestamp,
                 Tweet.timezone,
                 Tweet.location,
                 Tweet.username,
                 Tweet.tweet,
                 Tweet.replies,
                 Tweet.likes,
                 Tweet.retweets,
                 ",".join(Tweet.hashtags),
                 Tweet.link,
                 Tweet.retweet,
                 Tweet.user_rt,
                 ",".join(Tweet.mentions),
                 date_time,
                 config.search_name,)
        cursor.execute('INSERT INTO tweets VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', entry)
        conn.commit()
    except pymysql.IntegrityError:
        pass


def loadusersfromdatabase(hostname, db_user, db_pwd, mysql_database, query, _type):
    """ usersfromdatabase option
    """
    con = pymysql.connect(hostname,
                          db_user,
                          db_pwd,
                          mysql_database,
                          charset='utf8mb4',
                          cursorclass=pymysql.cursors.DictCursor)

    with con:
        cur = con.cursor()
        cur.execute(query)
        userlist = cur.fetchall()

        if _type == "search":
            un = ""
        for user in userlist:
            un += "%20OR%20from%3A" + user
        return un[15:]
    return userlist