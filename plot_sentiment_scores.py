import pandas as pd
import seaborn as sns
from os import walk
import yaml
from os.path import join as p_join
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def make_paths(input_folder):
    walker = walk(input_folder)
    paths = []
    for directory, subdir, files in walker:
        if directory == input_folder:
            for file in files:
                file_path = p_join(directory, file)
                paths.append(file_path)
    return paths


path_to_output_plots = 'plots_and_figures'

path_to_articles = make_paths('formatted_data')
path_to_filter_terms = 'filter_terms.yaml'

with open(path_to_filter_terms, 'r', encoding='utf-8') as f:
    filter_terms = yaml.safe_load(f)

agencies = list(filter_terms.keys())
path_to_ministry_info = 'formatted_minister_file.csv'

ministry_file = pd.read_csv(path_to_ministry_info)
ministry_file_mofa = ministry_file[ministry_file.agency == 'houmu']
ministry_file_mofa = ministry_file_mofa[ministry_file_mofa.days > 15]
for agency in agencies:
    break
    agency = '法務省'
    print(f'now analyzing {agency}')

    cur_ag_filter_terms = filter_terms[agency]

    agency_articles_path = next(path for path in path_to_articles if agency in path)
    articles = pd.read_csv(agency_articles_path, low_memory=False)

    article_day_df = articles.groupby('date').mean().reset_index()
    article_day_df.loc[:, 'rolling_sentiment_score'] = article_day_df.sentiment_score.rolling(
        window=50, min_periods=10).mean()

    xaxis_dates = DateFormatter("%Y-%m-%d")
    sentiment_plot = sns.lineplot(x=article_day_df.date, y=article_day_df.rolling_sentiment_score).get_figure()

    for x in ministry_file_mofa.resign.iloc[:-1]:
        plt.axvline(x, color='red')

    sentiment_plot_file = p_join(path_to_output_plots, f"{agency}.png")

    sentiment_plot.set_size_inches(30, 12)
    sentiment_plot.savefig(sentiment_plot_file)

    plt.close()


