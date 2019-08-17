import sys
from datetime import datetime
import time
import pymysql
import pymysql.cursors
import logging as logme


def Conn(config, print_msg=True):
    # hostname, mysqldatabase, db_user, db_pwd, print_msg = True):
    logme.debug(__name__ + ':Conn')
    if config.mysqldatabase:
        if print_msg:
            if config.Username is not None:
                print(f"[+] Inserting into MySqlDatabase: {str(config.mysqldatabase)} for {config.Username}")
            else:
                print(f"[+] Inserting into MySqlDatabase: {str(config.mysqldatabase)}")
        conn = init(config.hostname, config.mysqldatabase, config.DB_user, config.DB_pwd)
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
        # print("dbmysql/def follow query= " + str(query))
        cursor.execute(query, entry)
        conn.commit()
    except pymysql.IntegrityError:
        pass


def user(conn, Username, tbl_name, User):
    try:
        if tbl_name is None:
            tbl_name = "followers"
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
        query = 'INSERT INTO {} VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(uTable(tbl_name))
        # print("dbmysql:user:query ", str(query))
        cursor.execute(query, entry)
        conn.commit()

    except pymysql.IntegrityError:
        pass


def tweets(conn, Tweet, config):
    try:
        date_time = str(datetime.now())
        time_ms = round(time.time() * 1000)
        cursor = conn.cursor()

        entry = (
                 Tweet.id_str,
                 Tweet.tweet,
                 Tweet.conversation_id,
                 Tweet.datetime,
                 Tweet.datestamp,
                 Tweet.timestamp,
                 Tweet.timezone,
                 Tweet.place,
                 Tweet.replies_count,
                 Tweet.likes_count,
                 Tweet.retweets_count,
                 Tweet.user_id,
                 Tweet.user_id_str,
                 Tweet.username,
                 Tweet.name,
                 Tweet.link,
                 ",".join(Tweet.mentions),
                 ",".join(Tweet.hashtags),
                 ",".join(Tweet.cashtags),
                 ",".join(Tweet.urls),
                 ",".join(Tweet.photos),
                 Tweet.quote_url,
                 Tweet.video,
                 Tweet.geo,
                 Tweet.near,
                 Tweet.source)
        # cursor.execute('INSERT INTO tweets VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', entry)
        insert_stmt = (
            "INSERT IGNORE INTO tweets (id_str, tweet, conversation_id, created_at, date, time, timezone, place, "
            "replies_count, likes_count, retweets_count, user_id, user_id_str, screen_name, name, link,"
            "mentions, hashtags, cashtags, urls, photos, quote_url, video, geo, near, source)"
            " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        )

        cursor.execute(insert_stmt, entry)
        conn.commit()
    except Exception as e:
        print(f"entry= {entry}")
        logme.critical(__name__ + ':dbmysql:' + str(e))


def loadusersfromdatabase(config, conn=None, _type=None):
    """ usersfromdatabase option
    """
    try:
        if conn:
            con = pymysql.connect(config.hostname,
                                  config.DB_user,
                                  config.DB_pwd,
                                  config.mysqldatabase,
                                  charset='utf8mb4')

            with con:
                cur = con.cursor()
                cur.execute(config.usersfromdatabase)
                rows = cur.fetchall()

                if _type == "search":
                    un = ""
                    for row in rows:
                        un += "%20OR%20from%3A" + row[0]
                    return un[15:]
                userlist = rows
        if not conn:
            cur = con.cursor()
            cur.execute(config.usersfromdatabase)
            rows = cur.fetchall()
        return userlist
    except Exception as e:
        logme.critical(__name__ + ':dbmysql:' + str(e))


def query_rows(config, conn=None):

    # config.Query = "select photos from tweets where photos >'' limit 3"
    try:
        if conn:
            con = pymysql.connect(config.hostname,
                                  config.DB_user,
                                  config.DB_pwd,
                                  config.mysqldatabase,
                                  charset='utf8mb4')

            with con:
                cur = con.cursor()
                cur.execute(config.Query)
                rows = cur.fetchall()
                returnlist = rows
        if not conn:
            cur = con.cursor()
            cur.execute(config.Query)
            rows = cur.fetchall()
            returnlist = rows

        return returnlist
    except Exception as e:
        logme.critical(__name__ + ':queryrows:' + str(e))


def non_query(config, query=None):
    try:
        if not query:
            if config.Query:
                query = config.Query
    except:
        raise
    try:
        con = pymysql.connect(config.hostname,
                              config.DB_user,
                              config.DB_pwd,
                              config.mysqldatabase,
                              charset='utf8mb4')
        with con:
            cur = con.cursor()
            cur.execute(query)
    except Exception as e:
        logme.critical(__name__ + ':dbmysql:' + str(e))