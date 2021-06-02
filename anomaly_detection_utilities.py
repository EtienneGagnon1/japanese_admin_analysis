from statsmodels.tsa.seasonal import seasonal_decompose
import dateutil.relativedelta
from PyAstronomy.pyasl.asl.outlier import generalizedESD
from arch import arch_model
import pandas as pd


class NewsCycleAggregator:

    def __init__(self, period_length):
        self.period_length = period_length

    def aggregate_by_period(self, deseasonalized_ts):

        day_skip = range(self.period_length, len(deseasonalized_ts), self.period_length)

        resids = []
        prev_pointer = 0
        for i in day_skip:
            mean_resid = deseasonalized_ts.modified_resid.iloc[prev_pointer:i].mean()
            prev_pointer = i
            resids.append(mean_resid)

        days = list(day_skip)
        corresponding_day = deseasonalized_ts.day.iloc[days]

        aggregate_df = pd.DataFrame.from_dict({'aggregate_resid': resids,
                                               'day': corresponding_day.values})
        return aggregate_df

    def ma_standardize_variance(self, resid):
        ma_model = arch_model(resid, p=0, o=1, q=1)
        ma_mod_result = ma_model.fit()
        resid = ma_mod_result.std_resid
        return resid

    def nullify_neg(self, resid):
        resid = [max(0, res) for res in resid]
        return resid

    def aggregate_standardize(self, deseasonalized_ts):
        deseasonalized_ts['mod_resid'] = self.ma_standardize_variance(deseasonalized_ts.modified_resid)
        aggregate_ts = self.aggregate_by_period(deseasonalized_ts)

        # aggregate_ts['mod_resid'] = self.nullify_neg(resid)
        return aggregate_ts


class AnomalyDetector:
    def __init__(self, anomaly_range):
        self.range = anomaly_range

    def detect_anom(self, aggregated_ts, alpha, max_anom:int) -> pd.Series:
        test_result = generalizedESD(aggregated_ts.mod_resid, alpha=alpha, maxOLs=max_anom, fullOutput=False)

        print(f'detected {test_result[0]} anomalies')

        aggregated_ts['anomaly'] = False
        aggregated_ts.iloc[test_result[1], -1] = True

        return aggregated_ts

    def find_anomalies_day_ranges(self, ts_with_anomalies):
        """
        this output is used to subset the original articles that belong to an anomalous period.
        """

        anomaly_periods = ts_with_anomalies[ts_with_anomalies.anomaly]
        anomaly_days = anomaly_periods.day

        window = dateutil.relativedelta.relativedelta(days=self.range)
        anomaly_days = anomaly_days.apply(lambda x: pd.date_range(x - window, x + window))
        anomaly_days = [(day, anom_id) for (anom_id, anom) in enumerate(anomaly_days) for day in anom]

        return anomaly_days


def stationarize_ts(num_article_series, date_series, period=365):

    deseasonalized = seasonal_decompose(num_article_series,
                                        model='additive',
                                        period=period,
                                        extrapolate_trend='freq')

    trend_val = deseasonalized.trend
    resid_val = deseasonalized.resid
    season_val = deseasonalized.seasonal

    stationary_df = pd.concat([date_series, trend_val, resid_val, season_val], axis=1, ignore_index=True)
    stationary_df.columns = ['date', 'trend', 'resid', 'seasonal_component']
    return stationary_df