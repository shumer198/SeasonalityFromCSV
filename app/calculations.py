import logging
import pandas as pd
from scipy import signal
from typing import List, Union

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
    try:
        header_list = ["market", "date", "open", "high", "low", "close"]
        quotes = pd.read_csv(
            file_path, parse_dates=False, delimiter=";", decimal=",", names=header_list
        )
        quotes["date"] = pd.to_datetime(quotes["date"], format="%d.%m.%Y")
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
    quotes["delta"] = quotes.close - quotes.close.shift(1)
    quotes.at[0, "delta"] = 0
    quotes["day_of_year"] = pd.DatetimeIndex(quotes.date).day_of_year
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
    quotes["day_of_year"] = pd.DatetimeIndex(quotes.date).day_of_year
    quotes = quotes.merge(seasonality, on="day_of_year", how="left")
    quotes = quotes.drop(columns=["delta_x", "day_of_year"])
    quotes = quotes.rename(columns={"delta_y": "seasonality"})
    return quotes


def get_quotes_for_send(quotes: pd.DataFrame) -> List[List]:
    """
    Return array of quotes for Google charts
    in format [ [close, seasonality], 'date'], [close, seasonality], 'date'], ....].
    for example [[102.45, 2.211825203856459, '2022-04-20'], [104.03, 2.0008669193674242, '2022-04-21'].....]

    :param quotes: quotes
    :type: pd.Dataframe

    :return: array of quotes
    :type: List[List]
    """
    quotes['date_as_str'] = quotes['date'].dt.strftime('%Y-%m-%d')
    quotes = quotes.drop(columns=["market", "date", "open", "high", "low"])
    quotes_for_send = quotes.values.tolist()

    return quotes_for_send
