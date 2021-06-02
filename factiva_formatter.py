import pandas as pd
from typing import List, Dict
import datetime


class FactivaFormatter:
    def __init__(self):
        self.header_conversion = {
            'HD': 'headline',
            'BY': 'newspaper',
            'WC': 'word_count',
            'PD': 'date',
            'SN': 'precise_source',
            'LA': 'language',
            'LP': 'leading_par',
            'TD': 'text',
            'NS': 'topics',
            'RE': 'region',
            'PUB': 'publisher',
            'CO': 'mentioned_organization',
            'AN': 'doc_id'
        }

    def format_header(self, input_df: pd.DataFrame) -> pd.DataFrame:
        input_df.columns = [self.header_conversion.get(x, x) for x in input_df.columns]
        return input_df

    def concatenate_lead_par_and_text(self, input_df: pd.DataFrame) -> pd.DataFrame:
        concatenated_text = input_df.leading_par.str.cat(input_df.text, sep=' ')
        input_df.loc[:, 'text'] = concatenated_text
        return input_df

    def format_raw_text_file(self, raw_text_file: List):
        def format_one_artice(article: str) -> Dict:
            break_up_article = article.split(' SEP ')
            break_up_article = [elem.split(' TAGBREAK ') for elem in break_up_article]

            article_dict = {tag.strip(): val.strip() for tag, val in break_up_article}

            return article_dict

        formatted_articles_list = []
        for article in raw_text_file:
            formatted_article = format_one_artice(article)
            formatted_articles_list.append(formatted_article)

        articles_df = pd.DataFrame(formatted_articles_list)
        articles_df = articles_df.drop_duplicates()

        return articles_df

    def format_date_column(self, formatted_df: pd.DataFrame) -> pd.DataFrame:

        formatted_df.loc[:, 'date'] = pd.to_datetime(formatted_df.date, format='%d %B %Y')

        post_half_2002_mask = formatted_df.date > datetime.datetime(2002, 6, 1)
        formatted_df = formatted_df.loc[post_half_2002_mask, :]

        return formatted_df

    def __call__(self, input_raw_articles: List, **kwargs) -> pd.DataFrame:

        input_df = self.format_raw_text_file(input_raw_articles)
        input_df = self.format_header(input_df)
        input_df = self.concatenate_lead_par_and_text(input_df)
        input_df = self.format_date_column(input_df)

        return input_df








