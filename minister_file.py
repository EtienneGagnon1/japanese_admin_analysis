import pandas as pd
import datetime
import numpy as np
datetime.date
path_minister_file = 'minister_appointments.csv'

minister_file = pd.read_csv(path_minister_file)

minister_file.loc[:, 'appointment'] = pd.to_datetime(minister_file.appointment)

minister_file[minister_file == 'Incumbent'] = np.nan
minister_file.loc[:, 'resign'] = pd.to_datetime(minister_file.resign)

minister_file = minister_file[minister_file.appointment >= datetime.datetime(2000, 1, 1)]

minister_file.to_csv('formatted_minister_file.csv')



