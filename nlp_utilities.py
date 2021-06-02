from transformers import pipeline
from spacy.util import load_model
from typing import List
from os.path import join as p_join
from os import walk
import pandas as pd
import numpy as np
import yaml


class NewsCorpusParser:
    def __init__(self, lang_proc, sentence_filter_terms: List, filter_sentences=True):
        """

        :param lang_proc: some spacy pipeline to process the text
        :param sentence_filter_terms:
        """
        self.lg_processor = lang_proc
        self.filter_terms = sentence_filter_terms

        self.filter = filter_sentences

    def make_sentence_tokens_for_articles(self, article_iterable):
        articles_sent_tokenized = []
        for index, art in enumerate(article_iterable):
            if index % 1000 == 1:
                print(f"now at article {index}")
            try:
                processed = self.lg_processor(art)
                article = [x for x in processed.sents]
                articles_sent_tokenized.append(article)
            except TypeError:
                articles_sent_tokenized.append(None)
                continue

        return articles_sent_tokenized

    def filter_sentences(self, article_iterable_sent_tok):
        articles_filtered = []

        for art in article_iterable_sent_tok:
            if art is None:
                art = ""
            else:
                art = [sent for sent in art if any(term in sent.text for term in self.filter_terms)]

            articles_filtered.append(art)

        return articles_filtered

    def process_articles(self, article_iterable):
        article_iterable = self.make_sentence_tokens_for_articles(article_iterable)

        article_iterable = self.filter_sentences(article_iterable)
        num_mentions = [len(x) for x in article_iterable]

        return article_iterable, num_mentions


def define_language_processing_object():
    nlp = load_model('ja_ginza')
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer, first=True)
    nlp.pipeline = [x for x in nlp.pipeline if x[0] == 'sentencizer']

    return nlp
