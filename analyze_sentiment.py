from transformers import pipeline
from spacy.util import load_model
from typing import List
from os.path import join as p_join
from os import walk
import pandas as pd
import numpy as np
import yaml


class NewsCorpusParser:
    def __init__(self, lang_proc, sentence_filter_terms: List):
        """

        :param lang_proc: some spacy pipeline to process the text
        :param sentence_filter_terms:
        """
        self.lg_processor = lang_proc
        self.filter_terms = sentence_filter_terms

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


def make_paths(input_folder):
    walker = walk(input_folder)
    paths = []
    for directory, subdir, files in walker:
        if directory == input_folder:
            for file in files:
                file_path = p_join(directory, file)
                paths.append(file_path)
    return paths


def analyze_sentiment(processed_text, num_mentions, sentiment_pipeline, mention_treshold=3):
    def parse_pipeline_output(pipeline_output):
        parsed_sentiment_scores = []
        for result in pipeline_output:
            if result is np.nan:
                parsed_sentiment_scores.append(np.nan)
            else:
                mean_sent = np.mean([x['label'] == 'ポジティブ' for x in result])
                parsed_sentiment_scores.append(mean_sent)
        return parsed_sentiment_scores

    sentiment_analysis_result = []
    for index, (article, mentions) in enumerate(zip(processed_text, num_mentions)):
        if mentions >= mention_treshold:
            try:
                analysis_result = sentiment_pipeline(article)
                sentiment_analysis_result.append(analysis_result)

                if index % 2000 == 1:
                    print(f'now at {index}')
            except (RuntimeError, ValueError) as e:
                print(f'encountered {e}')
                sentiment_analysis_result.append(np.nan)
        else:
            sentiment_analysis_result.append(np.nan)

    sentiment_scores = parse_pipeline_output(sentiment_analysis_result)

    return sentiment_scores


def main():
    path_to_articles = make_paths('formatted_data')
    path_to_filter_terms = 'filter_terms.yaml'

    with open(path_to_filter_terms, 'r', encoding='utf-8') as f:
        filter_terms = yaml.safe_load(f)

    sentiment_analyzer = pipeline('sentiment-analysis',
                                  model='daigo/bert-base-japanese-sentiment',
                                  tokenizer='daigo/bert-base-japanese-sentiment',
                                  use_fast=False,
                                  device=0)

    ja_processor = define_language_processing_object()

    agencies = list(filter_terms.keys())

    for agency in agencies:
        print(f'now analyzing {agency}')

        cur_ag_filter_terms = filter_terms[agency]

        parser = NewsCorpusParser(ja_processor,
                                  sentence_filter_terms=cur_ag_filter_terms)

        agency_articles_path = next(path for path in path_to_articles if agency in path)
        articles = pd.read_csv(agency_articles_path, low_memory=False)

        processed_text, num_mentions = parser.process_articles(articles.text)
        articles.loc[:, 'num_mentions'] = num_mentions

        print('finished processing text')

        str_text = [[x.text for x in art] for art in processed_text]

        sentiment_scores = analyze_sentiment(str_text, num_mentions, sentiment_analyzer, mention_treshold=3)

        print('finished processing sentiment')

        articles.loc[:, 'sentiment_score'] = sentiment_scores

        articles.loc[:, 'agency_mention'] = [''.join(art) for art in str_text]
        articles.to_csv(agency_articles_path, index=False)

        print(f'finished analzing {agency}')


if __name__ == "__main__":
    main()