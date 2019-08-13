# threadfactory
# multi_threaded capabilities for twint
import datetime
from datetime import datetime
import queue, asyncio, bs4
import logging as logme
from . import get
from . import dbmysql,  user
from bs4 import BeautifulSoup


async def lookup_user(conn, config, connector, username, thread, q):
        try:
            # placing conn here opens 1 connection per thread / doesn't appear to be quicker than one overall conn
            # msg = False
            # conn = dbmysql.Conn(config.hostname, config.mysqldatabase, config.DB_user, config.DB_pwd, msg)

            config.Username = str(username)
            url = f"https://twitter.com/{username}?lang=en"

            response = await get.Request(url, connector)
            # print("response", str(response))
            u = user.User(BeautifulSoup(response, "html.parser"))
            date_time = str(datetime.now())
            cursor = conn.cursor()

            # entry = (u.id, u.name, u.username, u.bio, u.location, u.url, u.join_date, u.join_time, u.tweets,
            # u.following,
            #        u.followers, u.likes, u.media_count, u.is_private, u.is_verified, u.avatar, date_time, username,)
            # replace into acts as an update routing on the same code block
            # query = 'REPLACE INTO followers VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' # followers

            # fix date to mysql YYYY-MM-DD 00:00:00 format
            # print(f"u.joineddate {u.join_date}")
            joined_date = datetime.strptime(u.join_date, "%d %b %Y")
            # print("joined_date: ",  joined_date.strftime("%Y-%m-%d 00:00:00"))

            # for table users
            entry = (u.id, u.name, u.username, u.bio, u.location, u.url, joined_date, u.tweets,
                    u.following, u.followers, u.likes, u.media_count, u.is_private, u.is_verified, u.avatar, username)
            insert_stmt = (
                "REPLACE INTO users (id_str, name, user, bio, location, url, joined, tweets, following,"
                "followers, likes, media, private, verified, avatar, username) "
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            )

            cursor.execute(insert_stmt, entry)
            # for followers
            # cursor.execute(query, entry)
            conn.commit()
            print("lookup_user Thread=", thread, "\t", "\t", "Username: ", username, "\t")
            # print("lookup_user: in try block ", str(username))
            q.task_done()

        except Exception as e:
            logme.critical(__name__ + ':lookup_user:' + str(username) + '  ' + str(e))


async def process_queue(conn, connector, config, q, i):
    while not q.empty():
        work = q.get()
        logme.debug("process_queue (i=", str(i), ")", "\t", str(work[0]), "\t")
        if str(work[0]) is not None:
            await lookup_user(conn, config, connector, str(work[0]), i, q)
        logme.debug(f"q-task-{i} done q-size= {q.qsize()}")


async def start(config):
    try:
        if config.thread_qty is None:
            config.thread_qty = 1
        q = queue.Queue()
        _type = "user_list"
        user_list = dbmysql.loadusersfromdatabase(config.hostname, config.DB_user, config.DB_pwd, config.mysqldatabase,
                                                  config.usersfromdatabase, _type)
        users_to_process = len(user_list)
        num_threads = min(int(config.thread_qty), users_to_process)
        # print(f"num threads= {num_threads}")
        connector = get.get_connector(config)
        msg = False
        conn = dbmysql.Conn(config, msg)
        # conn = None
        for i in range(users_to_process):
            q.put_nowait(user_list[i])

        for i in range(num_threads):
            task = asyncio.create_task(process_queue(conn, connector, config, q, i))
        done, pending = await asyncio.wait({task})

    except Exception as e:
        logme.critical(__name__ + ':User:' + str(e))
