import os
from os.path import join as p_join
import pandas as pd
import datetime
from anomaly_detection_utilities import NewsCycleAggregator, AnomalyDetector, stationarize_ts
import seaborn as sns
import numpy as np
from factiva_formatter import FactivaFormatter
from time_series_analyzer import TimeSeriesAnalyzer
import matplotlib.pyplot as plt


def main():
    path_to_articles = 'agency_articles'

    agency_files = []
    for path, subdir, files in os.walk(path_to_articles):
        for file in files:
            if 'yomiuri' in file:
                agency_files.append(p_join(path, file))

    path_to_output_data = 'formatted_data'

    path_to_output_figures = 'plots_and_figures'
    stationarized_subdir = 'stationarized_ts'
    raw_count_subdir = 'raw_ts'

    formatter = FactivaFormatter()
    ts_analyzer = TimeSeriesAnalyzer()

    for agency_file in agency_files:
        print(f"now processing {agency_file}")
        with open(agency_file, 'r', encoding='utf-8') as f:
            agency_raw_file = f.readlines()

        current_agency = agency_file.split("\\")[-2]
        current_filename = agency_file.split("\\")[-1]

        agency_df = formatter(agency_raw_file)

        agency_ts_info = ts_analyzer.find_residual_values(agency_df)

        ts_plot = sns.lineplot(x=agency_ts_info.date, y=agency_ts_info.window_count).get_figure()

        ts_plot_file = p_join(path_to_output_figures, stationarized_subdir, f"{current_agency}_stationarized_ts.png")
        ts_plot.savefig(ts_plot_file)

        plt.close()

        raw_counts_plot = sns.lineplot(x=agency_ts_info.date, y=agency_ts_info.raw_art_window_count).get_figure()

        raw_count_plot_file = p_join(path_to_output_figures, raw_count_subdir, f"{current_agency}_raw_counts_ts.png")
        raw_counts_plot.savefig(raw_count_plot_file)
        plt.close()

        output_data_file = p_join(path_to_output_data, f"{current_filename.replace('.txt', '')}_formatted.csv")
        agency_ts_info.to_csv(output_data_file, encoding='utf-8', index=False)


if __name__ == "__main__":
    main()




