from path_management import make_paths
from os.path import join as p_join
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

path_to_processed_text = 'processed_text_files'
path_to_tokenized_files = 'tokenized_text'

tokenized_text_files = make_paths(p_join(path_to_processed_text, path_to_tokenized_files))

with open(tokenized_text_files[1], 'rb') as f:
    agency_articles = pickle.load(f)

agency_articles