import scipy.sparse as sp
import numpy as np
from util import *
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

class ContentBased:
    def __init__(self, dbname, movies, users):
        self.movies = movies
        self.users = users

    def movie_to_vec():
        # gen all plots
        plots = load_movie_plot(self.dbname, self.movies)
        all_plots = []
        for i in range(len(self.movies)):
            p = ''
            for plot in plots[self.movies[i]]:
                p += plot + ' '
            all_plots.append(p)
        # tokenizing
        count_vect = CountVectorizer()
        plot_counts = count_vect.fit_transform(all_plots)
        # tfidf
        tf_transformer = TfidfTransformer().fit(plot_counts)
        self.plot_tfidf = tf_transformer.transform(plot_counts)





if __name__ == "__main__":
    # load from file
    rating = load_sparse_csr(DATA_DIR+'rating.npz')
    movies = np.load(DATA_DIR+'movies.npy')
    users = np.load(DATA_DIR+'users.npy')
    print rating.shape, type(rating), movies.shape, users.shape

    # split into trian, valid, test set
    train, valid, test = split_dataset(rating)
    print train.shape, valid.shape, test.shape

    ContentBased(DB_NAME, movies, users)
    
            