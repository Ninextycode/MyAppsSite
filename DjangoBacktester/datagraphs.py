import matplotlib.pyplot as plt
import base64
import pandas as pd
import numpy as np

import os
import io

import MyAppsSite.settings as settings


def prepare_files(shares, start_date, end_date):
    for share in shares:
        data = pd.read_csv(os.path.join(settings.STATIC_ROOT, share+".csv"))
        data["DATETIME"] = pd.to_datetime(data["DATETIME"])
        data.set_index("DATETIME", inplace=True)

        start = pd.to_datetime(start_date)
        end =  pd.to_datetime(end_date) + pd.DateOffset(days=1)
        data = data[start:end]
        working_path = os.path.join(settings.MEDIA_ROOT, settings.TEMP_DATA_DIR)
        if not os.path.exists(working_path):
            os.mkdir(working_path)
        data.to_csv(os.path.join((working_path), share+".csv"))


def get_graphs(shares, start_date, end_date):
    images = {}
    for share in shares:
        plt.clf()

        df = pd.read_csv(os.path.join(settings.STATIC_ROOT, share+".csv"))
        df["CLOSE"] /= 100
        df.drop(['HIGH', 'LOW', 'OPEN'], 1, inplace=True)
        df['DATETIME'] = pd.to_datetime(df['DATETIME'])
        df = df.set_index('DATETIME')

        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date) + pd.DateOffset(days=1)
        df = df[start:end]

        df.reset_index(1, inplace=True)
        df.drop(['DATETIME'], 1, inplace=True)

        df["MA600"] = df["CLOSE"].rolling(600).apply(lambda x: np.mean(x))
        df["MA1800"] = df["CLOSE"].rolling(1800).apply(lambda x: np.mean(x))


        df.plot(legend=True, title=share)

        with io.BytesIO() as buf:
            plt.savefig(buf)
            buf.seek(0)
            images[share] = base64.b64encode(buf.getvalue()).decode("utf-8")


    return images


def images_from_data(data):
    images = {}
    for title, frame in data.items():
        plt.clf()

        offset = (frame.max() - frame.min())/4
        frame.plot(title=title, ylim = [frame.min() - offset, frame.max() +  offset])


        with io.BytesIO() as buf:
            plt.savefig(buf, format='png')
            buf.seek(0)
            images[title] = base64.b64encode(buf.getvalue()).decode("utf-8")

    return images
