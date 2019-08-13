# threadfactory
# multi_threaded capabilities for twint
import datetime
from datetime import datetime
import queue, asyncio, bs4
import logging as logme
from . import get
from . import dbmysql,  user
from bs4 import BeautifulSoup


async def issues(response):

    # This account has been suspended
    # Sorry, that page doesn’t exist





    return True


async def lookup_user(conn, config, connector, username, thread, q):
        try:
            # placing conn here opens 1 connection per thread / doesn't appear to be quicker than one overall conn
            # msg = False
            # conn = dbmysql.Conn(config.hostname, config.mysqldatabase, config.DB_user, config.DB_pwd, msg)

            config.Username = username
            url = f"https://twitter.com/{username}?lang=en"
            # test url to see if suspended
            response = await get.Request(url, connector)
            date_time = str(datetime.now())

            if response.find("This account has been suspended") !=-1:
                print(f"https://twitter.com/{username} - account suspended")
                try:
                    # entry = (username, bit(1))
                    insert_stmt = (f"REPLACE INTO users (id_str, user, suspended) VALUES (0,'{username}',b'1')")
                    insert_stmt = (f"Update users  set suspended = b'1' where user='{username}' ")
                    # print(insert_stmt)
                    cursor = conn.cursor()
                    cursor.execute(insert_stmt)
                    conn.commit()
                    q.task_done()
                    return
                except RuntimeError as e:
                    logme.critical(__name__ + ':lookup_user: ' + str(e))

            if response.find("Sorry, that page doesn’t exist") !=-1:
                try:
                    print(f"https://twitter.com/{username} - doesn't exist")
                    # insert_stmt = (f"REPLACE INTO users (id_str, user, doesntexist) VALUES (0,'{username}',b'1')")
                    insert_stmt = (f"Update users set doesntexist = b'1' where user='{username}' ")
                    # entry = (username, b'1')
                    # insert_stmt = ("REPLACE INTO users (user, doesntexist) VALUES (%s,%s)")
                    # print(insert_stmt)
                    cursor = conn.cursor()
                    cursor.execute(insert_stmt)
                    conn.commit()
                    q.task_done()
                    return
                except RuntimeError as e:
                    logme.critical(__name__ + ':lookup_user: ' + str(e))

            u = user.User(BeautifulSoup(response, "html.parser"))

            joined_date = datetime.strptime(u.join_date, "%d %b %Y")   # fix date to mysql YYYY-MM-DD 00:00:00 format
            # print("joined_date: ",  joined_date.strftime("%Y-%m-%d 00:00:00"))

            # for table users
            entry = (u.id, u.name, u.username, u.bio, u.location, u.url, joined_date, u.tweets,
                    u.following, u.followers, u.likes, u.media_count, u.is_private, u.is_verified, u.avatar, username)
            insert_stmt = (
                "REPLACE INTO users (id_str, name, user, bio, location, url, joined, tweets, following,"
                "followers, likes, media, private, verified, avatar, username) "
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            )
            cursor = conn.cursor()
            cursor.execute(insert_stmt, entry)
            # for followers
            # cursor.execute(query, entry)
            conn.commit()
            print("lookup_user Thread=", thread, "\t", "\t", "Username: ", username, "\t")
            # print("lookup_user: in try block ", str(username))
            q.task_done()

        except RuntimeError as e:
            logme.critical(__name__ + ':lookup_user: ' + str(e))


async def process_queue(conn, connector, config, q, i):
    try:
        while not q.empty():
            work = q.get()
            userwork = str(work[0])
            if len(userwork) > 1:
                logme.debug("process_queue (i=", str(i), ")", "\t", userwork, "\t")
                await lookup_user(conn, config, connector, userwork, i, q)
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
        # print(f"num threads= {num_threads}")
        connector = get.get_connector(config)
        msg = False
        conn = dbmysql.Conn(config, msg)
        # conn = None
        for i in range(users_to_process):
            q.put_nowait(user_list[i])

        for i in range(num_threads):
            task = asyncio.create_task(process_queue(conn, connector, config, q, i))
            # TODO more parallel processes start here
        # TODO add progress bar call back to here
        done, pending = await asyncio.wait({task})

    except Exception as e:
        logme.critical(__name__ + ':User:' + str(e))
