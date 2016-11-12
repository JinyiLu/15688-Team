import scipy.sparse as sp
import numpy as np
import sqlite3
from util import *

if __name__ == "__main__":
    rating = load_sparse_csr('rating.npz')
    print rating.shape, type(rating)
    movies = np.load('movies.npy')
    users = np.load('users.npy')
    print movies.shape, users.shape