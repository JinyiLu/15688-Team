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


def split_dataset(rating, seed=0, th=(0.6,0.2)):
    """split the rating dataset into 3 set
    
    Args:
        rating: rating matrix #user * #movie
        seed: random seed
        th: split threshold, th[0] means the per centage of data used for training, th[1] for validation, rest for test
        
    Returns:
        train, valid, test, user_mask
    """
    np.random.seed(seed)

    train = np.zeros(rating.shape)
    valid = np.zeros(rating.shape)
    test = np.zeros(rating.shape)
    
    for i in range(rating.shape[0]):
        cnt = 0
        for j in (np.random.permutation(rating.shape[1])):
            if rating[i,j] > 0:
                cnt+=1
                if np.sum(train[i,:]) == 0.0:
                    train[i,j] = rating[i,j]
                elif np.sum(valid[i,:]) == 0.0:
                    valid[i,j] = rating[i,j]
                elif np.sum(test[i,:]) == 0.0:
                    test[i,j] = rating[i,j]
                else:
                    if j % 100 <= th[0] * 100:
                        train[i,j] = rating[i,j]
                    elif j % 100 <= (th[0] + th[1]) * 100:
                        valid[i,j] = rating[i,j]
                    else:
                        test[i,j] = rating[i,j]
                        
#     return train, valid, test
    
    # remove no rating users
    user_mask_train = (np.sum(train, axis=1) == 0)
    user_mask_valid = (np.sum(valid, axis=1) == 0)
    user_mask_test = (np.sum(test, axis=1) == 0)

    user_mask = np.logical_not(user_mask_train | user_mask_valid | user_mask_test)
#     print np.sum(user_mask_train), np.sum(user_mask_valid), np.sum(user_mask_test), np.sum(user_mask)
    print 'Number of user delete %d' % (rating.shape[0] - np.sum(user_mask))
    train = train[user_mask,:]
    test = test[user_mask,:]
    valid = valid[user_mask,:]

    return train, valid, test, user_mask




def rating_filter(rating_m, user_names, movie_names, th=(5,5)):
    """filter out users and movies with small number of ratings
    
    Args:
        rating_m: rating matrix #user * #movie
        user_names: a list of user names
        movie_names: a list of movie names
        th: threshold for filtring, the first one is for user and the second one is for movie
    
    """
    mask = rating_m > 0
    mask_user = mask.sum(axis=1) > th[0]
    mask_movie = mask.sum(axis=0) > th[1]
    
    print mask_user.shape, mask_movie.shape
    print 'Original #rating %d' % (np.sum(mask))
    print 'Remaining #user %d #movie %d' % (np.sum(mask_user), np.sum(mask_movie))
    
    new_rating_m = rating_m[mask_user, :][:, mask_movie]
    
    print new_rating_m.shape
    print 'Remaining #rating %d' % (np.sum(new_rating_m > 0))
    
    new_movie_names = movie_names[mask_movie]
    new_user_names = user_names[mask_user]

    # compute the sparsity 
    sparsity = len(new_rating_m.nonzero()[0]) * 1.0
    sparsity /= (new_rating_m.shape[0] * new_rating_m.shape[1])
    sparsity *= 100
    print 'Sparsity for the rating matrix : {:4.2f}%'.format(sparsity)
        
    return new_rating_m, new_user_names, new_movie_names

if __name__ == "__main__":
    movies, users, rating_m = db_to_matrix(DB_NAME)
    np.save('movies', movies)
    np.save('users', users)
    save_sparse_csr('rating', rating_m)
    print 'num of users %d' % len(users)
    print 'num of movies %d' % len(movies)
    print 'rating m shape %s' % str(rating_m.shape)

