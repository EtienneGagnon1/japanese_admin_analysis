from PyAstronomy.pyasl.asl.outlier import generalizedESD
from path_management import make_paths
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

path_to_formatted_files = 'formatted_data'

formatted_files_paths = make_paths(path_to_formatted_files)

for agency in formatted_files_paths:
    agency_articles = pd.read_csv(agency)
    agency_articles.loc[:, 'date'] = pd.to_datetime(agency_articles.date)

    week_aggregate = agency_articles.groupby(pd.Grouper(key='date', freq='W-FRI')).mean().reset_index()
    plt.plot(week_aggregate.date, week_aggregate.resid)
    plt.scatter(week_aggregate.date, week_aggregate.resid)

    week_aggregate.resid


