import fasttext
import fasttext.util
from sklearn.metrics.pairwise import cosine_similarity
import nlp_utilities
from nlp_utilities import NewsCorpusParser
from spacy.util import load_model
from path_management import make_paths
import os
import sklearn
import fugashi
import pandas as pd
import pickle
from os.path import join as p_join

tagger = fugashi.Tagger()
paths_to_data = make_paths('formatted_data')

for agency in paths_to_data:

    print(f'now analyzing {agency}')
    articles = pd.read_csv(agency, low_memory=False)
    articles = articles.loc[~articles.text.isna(), :]

    articles_arr = articles.text.values


    articles_text = []
    for art in articles_arr:
        tokenized = tagger(art)

        [len(tt.surface) for tt in tokenized]
        articles_text.append(tokenized)

    path_to_processed_text_files = 'processed_text_files'
    current_processing = "tokenized_text"
    file_name = os.path.split(agency)[-1]
    file_name = file_name.replace('.csv', '.pkl')



    with open(p_join(path_to_processed_text_files, current_processing, file_name), 'wb') as f:
        pickle.dump(articles_text, f)



