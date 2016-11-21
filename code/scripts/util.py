import scipy.sparse as sp
import numpy as np
import sqlite3
import ast
from collections import Counter

DATA_DIR = '../../data/'
# DB_NAME = '../../data/imdb_m_notv_withvote.db'
DB_NAME = '../../data/imdb_final.db'

def load_movie_plot(dbname, movies):
    movie_plot = {}

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    for r in c.execute('''
        SELECT imdb_id, plots
        FROM movie
        '''):
        if r[0] in movies:
            movie_plot[r[0]] = ast.literal_eval(r[1])
    return movie_plot


def save_sparse_csr(filename,array):
    np.savez(filename,data = array.data ,indices=array.indices,
             indptr =array.indptr, shape=array.shape )

def load_sparse_csr(filename):
    loader = np.load(filename)
    return sp.csr_matrix((  loader['data'], loader['indices'], loader['indptr']),
                         shape = loader['shape'])

def db_to_matrix(dbname):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    movies = []
    users = []
    rating = {}
    for r in c.execute('''
        SELECT imdb_id, username, rating
        FROM review
        WHERE imdb_id IS NOT NULL AND
            username IS NOT NULL AND
            rating IS NOT NULL
        '''):
        if r[0] not in movies:
            movies.append(r[0])
        if r[1] not in users:
            users.append(r[1])
        rating[(r[1], r[0])] = r[2]

    rating_m = sp.csr_matrix((len(users), len(movies)), dtype=int)
    for k in rating:
        rating_m[users.index(k[0]), movies.index(k[1])] = rating[k]

    conn.close()
    return movies, users, rating_m

def count_values(rating):
    user_mask = (rating != 0).sum(axis=1)
    user_mask = np.squeeze(np.asarray(user_mask))

    cnt = Counter(user_mask)
    print cnt
    return cnt


def split_dataset(rating):
    np.random.seed(0)
    # total = rating.nonzero()[0].shape[0]
    mask = np.random.rand(rating.shape[0], rating.shape[1])
    train = rating.multiply(mask<0.6)
    valid = rating.multiply(np.logical_and(mask >= 0.6, mask < 0.8))
    test = rating.multiply(mask > 0.8)

    # remove no rating users
    # user_mask_train = (np.sum(train, axis=1) == 0)
    # user_mask_valid = (np.sum(valid, axis=1) == 0)
    # user_mask_test = (np.sum(test, axis=1) == 0)

    # user_mask = (user_mask_train | user_mask_valid | user_mask_test)

    # print np.sum(user_mask_train), np.sum(user_mask_valid), np.sum(user_mask_test), np.sum(user_mask)

    return train, valid, test


if __name__ == "__main__":
    movies, users, rating_m = db_to_matrix(DB_NAME)
    np.save('movies', movies)
    np.save('users', users)
    save_sparse_csr('rating', rating_m)
    print 'num of users %d' % len(users)
    print 'num of movies %d' % len(movies)
    print 'rating m shape %s' % str(rating_m.shape)

