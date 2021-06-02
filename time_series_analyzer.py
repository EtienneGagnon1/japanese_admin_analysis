from anomaly_detection_utilities import stationarize_ts
import seaborn as sns
import pandas as pd


class TimeSeriesAnalyzer:
    def __init__(self):
        self.window_size = 10

    def find_residual_values(self, agency_df):

        article_count = agency_df.groupby('date').count().reset_index()
        article_count = article_count.iloc[:, 0:2]
        article_count.columns = ['date', 'article_count']

        stationarized_article_count = stationarize_ts(article_count.article_count, article_count.date)

        rolling_window = stationarized_article_count.resid.rolling(window=self.window_size).mean()
        stationarized_article_count.loc[:, 'window_count'] = rolling_window.values

        date_window_val = stationarized_article_count.loc[:, ['date', 'window_count']]

        agency_df_with_ts_info = agency_df.merge(date_window_val, how='left', on='date')

        num_articles_count_window = article_count.article_count.rolling(window=self.window_size).mean()
        article_count.loc[:, 'raw_art_window_count'] = num_articles_count_window

        agency_df_with_ts_info = agency_df_with_ts_info.merge(article_count, how='left', on='date')

        return agency_df_with_ts_info

