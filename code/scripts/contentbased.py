import scipy.sparse as sp
import numpy as np
from util import *

DATA_DIR = '../../data/'

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