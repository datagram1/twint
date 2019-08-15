# threadfactory
# multi_threaded capabilities for twint
import datetime
from datetime import datetime
import queue, asyncio, bs4
import logging as logme
from time import gmtime, strftime

from . import get,dbmysql
from . import dbmysql,  user
from bs4 import BeautifulSoup
from tqdm import tqdm, trange


def safe_print(content):
    print(f"{content}")


async def lookup_user(conn, config, connector, username, thread, q):
        try:
            # placing conn here opens 1 connection per thread / doesn't appear to be quicker than one overall conn
            msg = False
            conn = dbmysql.Conn(config, msg)
            timeupdate = str(datetime.now())
            config.Username = username
            url = f"https://twitter.com/{username}?lang=en"
            # test url to see if suspended
            response = await get.Request(url, connector)
            date_time = str(datetime.now())

            if response.find("This account has been suspended") !=-1:
                safe_print(f"https://twitter.com/{username} - account suspended")
                try:
                    dbmysql.non_query(config, f"insert ignore into users (id_str, user) VALUES (0, '{username}')")
                    # insert_stmt0 = (f"insert ignore into users (id_str, user) VALUES (0, '{username}')")
                    insert_stmt = (f"Update users  set suspended = b'1' where user='{username}' ")
                    # print(insert_stmt)
                    cursor = conn.cursor()
                    # cursor.execute(insert_stmt0)
                    cursor.execute(insert_stmt)
                    conn.commit()
                    q.task_done()
                    return
                except RuntimeError as e:
                    logme.critical(__name__ + ':lookup_user: ' + str(e))

            if response.find("Sorry, that page doesn’t exist") !=-1:
                try:
                    safe_print(f"https://twitter.com/{username} - doesn't exist")
                    dbmysql.non_query(config, f"insert ignore into users (id_str, user) VALUES (0, '{username}')")
                    # insert_stmt0 = (f"insert ignore into users (id_str, user) VALUES (0, '{username}')")
                    insert_stmt = (f"Update users set doesntexist = b'1' where user='{username}' ")
                    # print(f"doesn't exist: {insert_stmt}")
                    cursor = conn.cursor()
                    # cursor.execute(insert_stmt0)
                    cursor.execute(insert_stmt)
                    conn.commit()
                    conn.close()
                    q.task_done()
                    return
                except RuntimeError as e:
                    logme.critical(__name__ + ':lookup_user: ' + str(e))
            u = user.User(BeautifulSoup(response, "html.parser"))
            joined_date = datetime.strptime(u.join_date, "%d %b %Y")   # fix date to mysql YYYY-MM-DD 00:00:00 format
            # print(f"***** u_join date: {joined_date}")
            # for table users
            entry = (u.id, u.name, u.username, u.bio, u.location, u.url, joined_date, u.tweets,
                    u.following, u.followers, u.likes, u.media_count, u.is_private, u.is_verified, u.avatar, username,
                     timeupdate)
            insert_stmt = (
                "REPLACE INTO users (id_str, name, user, bio, location, url, joined, tweets, following,"
                "followers, likes, media, private, verified, avatar, username, time_update) "
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            )
            # print(f"sql: {insert_stmt} {entry}")
            cursor = conn.cursor()
            cursor.execute(insert_stmt, entry)
            conn.commit()
            safe_print(f"lookup_user Thread= {thread}\t\t Username: {username}")

            q.task_done()

        except RuntimeError as e:
            logme.critical(__name__ + ':lookup_user: ' + str(e))


async def process_queue(conn, connector, config, q, i):
    try:
        while not q.empty():
            conn = None
            work = q.get()
            userwork = str(work[0])

            if len(userwork) > 0:
                logme.debug("process_queue (i=", str(i), ")", "\t", userwork, "\t")
                await lookup_user(conn, config, connector, userwork, i, q)
                # loop = loop.call_soon_threadsafe(callback, *args)
                # future = asyncio.run_coroutine_threadsafe(lookup_user(conn, config, connector, userwork, i, q), loop)
                # result = future.result()
            logme.debug(f"q-task-{i} done q-size= {q.qsize()}")
    except RuntimeError as e:
            logme.critical(__name__ + ':process_queue: ' + str(e))
    #except Exception as e:
    #    logme.critical(__name__ + ':lookup_user:' + str(e))


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
        if not users_to_process:
            safe_print("No Users to process Exiting...")
            return
        # print(f"num threads= {num_threads}")
        connector = get.get_connector(config)
        # msg = False
        # conn = dbmysql.Conn(config, msg)
        conn = None
        for i in range(users_to_process):
            q.put_nowait(user_list[i])

        for i in range(num_threads):
            task = asyncio.create_task(process_queue(conn, connector, config, q, i))
            # TODO more parallel processes start here
        # TODO add progress bar call back to here
        done, pending = await asyncio.wait({task})

    except Exception as e:
        logme.critical(__name__ + ':User:' + str(e))


async def bar(target, size, position):
        progressbar=tqdm.tqdm(
            desc=target, total=size, position=position, leave=False)

