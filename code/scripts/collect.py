from imdbpie import Imdb
import numpy as np
import time
import sqlite3
import json
import sys
from multiprocessing import Process, Pool

MAX_REVIEWS = 5000
SMP_RATE = 0.01
MAX_IDS = 100000000

def save_title_info(title, conn):
    c = conn.cursor()
    # to do store in json
    info = [(title.imdb_id, title.title, title.type, title.year, title.tagline, \
        str(title.plots), title.plot_outline, title.rating, str(title.genres), title.votes,\
        title.runtime, title.poster_url, title.cover_url, title.release_date,\
        title.certification, str(title.trailer_image_urls), str(title.directors_summary),\
        str(title.creators), str(title.cast_summary), str(title.writers_summary), str(title.credits),\
        str(title.trailers))]

    c.executemany('''
        INSERT INTO movie
        (imdb_id, title, type, year, tagline, plots, plot_outline, 
        rating, genres, votes, runtime, poster_url, cover_url, release_date,
        certification, trailer_image_urls, directors_summary, creators, 
        cast_summary, writers_summary, credits, trailers) VALUES (?, ?, ?, ?, ?, ?, ?, ?
        , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', info)
    conn.commit()

def save_review(ttid, conn, imdb):
    c = conn.cursor()
    num_reviews = MAX_REVIEWS
    stop = False
    reviews = imdb.get_title_reviews(ttid, max_results=num_reviews)
    while not stop:
        num_reviews *= 2
        reviews_new = imdb.get_title_reviews(ttid, max_results=num_reviews)
        if len(reviews_new) == len(reviews):
            stop = True
        elif len(reviews_new) < len(reviews):
            print >> sys.stderr, 'retrieval less reviews! %s' % ttid
        else:
            reviews = reviews_new
    for r in reviews:
        info = [(ttid, r.username, r.text, r.date, r.rating, r.summary,\
            r.status, r.user_location, r.user_score, r.user_score_count)]
        c.executemany('''
            INSERT INTO review
            (imdb_id, username, content, postdate, rating,
            summary, status, user_location, user_score,
            user_score_count) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', info)
    conn.commit()

def save_all_info(ttid, imdb, conn):
    if imdb.title_exists(ttid):
        try:
            title = imdb.get_title_by_id(ttid)
            save_title_info(title, conn)
            save_review(ttid, conn, imdb)
        except:
            print >> sys.stderr, 'some error when saving %s' % ttid
        return True
    else:
        return False

def create_table(conn):
    c = conn.cursor()
    c.execute('''
        DROP TABLE IF EXISTS movie
        ''')
    c.execute('''
        DROP TABLE IF EXISTS review
        ''')
    c.execute('''
        CREATE TABLE movie
        (imdb_id TEXT, title TEXT, type TEXT, year INTEGER, tagline TEXT,
        plots TEXT, plot_outline TEXT, rating INTEGER, genres TEXT, votes INTEGER,
        runtime INTEGER, poster_url TEXT, cover_url TEXT, release_date TEXT, 
        certification TEXT, trailer_image_urls TEXT, directors_summary TEXT,
        creators TEXT, cast_summary TEXT, writers_summary TEXT, credits TEXT, 
        trailers TEXT, PRIMARY KEY(imdb_id ASC))
        ''')
    c.execute('''
        CREATE TABLE review
        (imdb_id TEXT, username TEXT, content TEXT, postdate TEXT, rating INTEGER,
        summary TEXT, status TEXT, user_location TEXT, user_score INTEGER, 
        user_score_count INTEGER)
        ''')
    conn.commit()

def create_subdatabase(paras):
    start = paras[0]
    end = paras[1] 
    dbname = paras[2]
    print 'iterate over %d to %d and save to %s' % (start, end, dbname)
    conn = sqlite3.connect(dbname)
    create_table(conn)
    imdb = Imdb(anonymize=True)
    np.random.seed(0)
    cnt = 0
    for i in range(start, end):
        ttid = 'tt'+str(i).zfill(7)
        if i % 1000000 == 0:
            print 'iterate %d' % i
        if np.random.rand() < SMP_RATE and save_all_info(ttid, imdb, conn):
            time.sleep(1)
            cnt += 1
            if cnt % 100 == 0:
                print 'save %d' %cnt
    print '%d movies in %s' % (cnt, dbname)

if __name__ == "__main__":
    start = 0
    size = 8
    step = MAX_IDS / size
    paras = []
    for i in range(size):
        start = i * step
        end = start + step
        name = 'imdb'+str(i)+'.db'
        paras.append((start, end, name))

    p = Pool(size)
    p.map(create_subdatabase, paras)

    




