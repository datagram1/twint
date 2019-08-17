import asyncio
import concurrent.futures
import logging
import queue
import sys
import time
import urllib
from twint import dbmysql
from urllib.request import urlopen, Request, urlretrieve
from urllib.error import HTTPError
import re


def blocks(n, q, config):
    log = logging.getLogger('blocks({})'.format(n))
    # log.info('running')
    work = q.get()
    userwork = str(work[0])
    # log.info(f"userwork= {userwork}")
    urls = userwork.split(',')
    if urls:
        for url in urls:
            # log.info(f"matched urls: {url}")
            pics = re.findall('[^/]+.jpg|[^/]+.png', url)
            if pics:
                for pic in pics:
                    try:
                        urlretrieve(url, config.path + pic)
                        dbmysql.non_query(config, f"update tweets set downloadedphotos = b'1' where photos='{userwork}'")
                        log.info(f"downloaded to: {config.path}{pic}")
                    except urllib.error.HTTPError as e:
                        dbmysql.non_query(config,
                                          f"update tweets set photourlerror = b'1' where photos='{userwork}'")
                        log.info(f"HTTPError: {url}")
    # log.info('done')
    q.task_done()
    return n ** 2


def testpath(path):
    print(f"Test path= {path}")


def fillq(config):
    log = logging.getLogger('fillq')
    q = queue.Queue()
    picture_list = dbmysql.query_rows(config)
    qsize = len(picture_list)
    for i in range(qsize):
         q.put(picture_list[i])
    q.join
    log.info(f"blocking tasks to create from qsize= {qsize}")
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
    blocking_tasks = [
        loop.run_in_executor(executor, blocks, i, q, config)
        for i in range(int(qsize))
    ]
    log.info('waiting for executor tasks')
    completed, pending = await asyncio.wait(blocking_tasks)
    # results = [t.result() for t in completed]
    # log.info('results: {!r}'.format(results))

    log.info('exiting')


