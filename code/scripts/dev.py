import scipy.sparse as sp
import numpy as np
import sqlite3
from util import *

if __name__ == "__main__":
    # load from file
    rating = load_sparse_csr(DATA_DIR+'rating.npz')
    print rating.shape, type(rating)
    movies = np.load(DATA_DIR+'movies.npy')
    users = np.load(DATA_DIR+'users.npy')
    print movies.shape, users.shape

    # split into trian, valid, test set
    train, valid, test = split_dataset(rating)
    print train.shape, valid.shape, test.shape
    print 'total num of ratings: %d' % rating.nonzero()[0].shape[0]
    print 'train num of ratings: %d' % train.nonzero()[0].shape[0]
    print 'valid num of ratings: %d' % valid.nonzero()[0].shape[0]
    print 'test num of ratings: %d' % test.nonzero()[0].shape[0]
