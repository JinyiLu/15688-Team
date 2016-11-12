import scipy.sparse as sp
import numpy as np
import sqlite3

DB_NAME = '../../data/imdb_m_notv_withvote.db'

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

    return movies, users, rating_m

if __name__ == "__main__":
    movies, users, rating_m = db_to_matrix(DB_NAME)
    np.save('movies', movies)
    np.save('users', users)
    save_sparse_csr('rating', rating_m)
    print 'num of users %d' % len(users)
    print 'num of movies %d' % len(movies)
    print 'rating m shape %s' % str(rating_m.shape)

