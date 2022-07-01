import csv
import logging
from typing import Union

import pandas as pd
from scipy import signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_quotes_from_csv(file_path: str) -> Union[pd.DataFrame, tuple]:
    """
    Load quotes from csv file to pandas Dataframe

    :param file_path: path to file with quotes
    :type: str

    :return: quotes dataframe or tuple with error description and error code
    :type: pd.Dataframe
    """
    delimiter = get_delimiter(file_path)
    try:
        quotes = pd.read_csv(
            file_path, parse_dates=False, delimiter=delimiter, usecols=["Date", "Close"]
        )
        quotes["Date"] = pd.to_datetime(quotes["Date"], format="%d.%m.%Y")

        # if "Close" load as string (it happens when decimal is ",") then replace decimal to "."
        # and convert column to numeric
        if quotes["Close"].dtypes == "object":
            quotes["Close"] = quotes["Close"].str.replace(",", ".")
            quotes["Close"] = pd.to_numeric(quotes["Close"])

    except Exception as e:
        logger.error(f"Data loading error. {e}")
        return "Internal server error", 500

    return quotes


def get_seasonality(quotes: pd.DataFrame) -> pd.DataFrame:
    """
    Return dataframe with calculated seasonality

    :param quotes: quotes dataframe
    :type: pd.Dataframe

    return: Dataframe with calculated seasonality
    type: pd.Dataframe
    """
    quotes["delta"] = quotes.Close - quotes.Close.shift(1)
    quotes.at[0, "delta"] = 0
    quotes["day_of_year"] = pd.DatetimeIndex(quotes.Date).day_of_year
    mean_delta = quotes.groupby("day_of_year")["delta"].mean()
    cumulative_sum = mean_delta.cumsum()
    seasonality = pd.DataFrame(cumulative_sum)
    seasonality["delta"] = signal.detrend(seasonality["delta"])

    return seasonality


def get_quotes_with_seasonality(quotes: pd.DataFrame) -> pd.DataFrame:
    """
    Append seasonality series to quotes dataframe
    :param quotes: quotes dataframe
    :type: pd.Dataframe
    """
    seasonality = get_seasonality(quotes=quotes)
    quotes["day_of_year"] = pd.DatetimeIndex(quotes.Date).day_of_year
    quotes = quotes.merge(seasonality, on="day_of_year", how="left")
    quotes = quotes.drop(columns=["delta_x", "day_of_year"])
    quotes = quotes.rename(columns={"delta_y": "Seasonality"})

    return quotes


def get_quotes_for_send(file_path: str) -> object:
    """
    Return array of quotes for Google charts
    in format [ [close, seasonality], 'date'], [close, seasonality], 'date'], ....].
    for example [[102.45, 2.211825203856459, '2022-04-20'], [104.03, 2.0008669193674242, '2022-04-21'].....]

    :param file_path: quotes
    :type: pd.Dataframe

    :return: array of quotes
    :type: List[List]
    """
    # Load quotes to Dataframe
    quotes = get_quotes_from_csv(file_path=file_path)
    # Append seasonality to quotes dataframe
    quotes = get_quotes_with_seasonality(quotes=quotes)
    quotes["Date"] = quotes["Date"].dt.strftime("%Y-%m-%d")
    quotes_for_send = quotes.values.tolist()

    return quotes_for_send


def get_delimiter(file_path: str) -> str:
    """
    Return delimiter for csv file
    :param file_path. Path to file
    :type: str

    :return: delimiter for csv file
    :type: str
    """
    try:
        with open(file_path, "r") as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.readline())
            return str(dialect.delimiter)
    except FileNotFoundError:
        logger.info("Delimiter load failed.")

        return ";"
