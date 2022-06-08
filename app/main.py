import logging
import calculations as calc
from settings import data_folder, file_name
from os import path

from flask import Flask, make_response, render_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    @app.route("/seasonality")
    def get_seasonality():
        """
        Return web page with seasonal chart
        """
        file_path = path.join(data_folder, file_name)
        quotes = calc.get_quotes_from_csv(file_path=file_path)
        quotes_with_seasonality = calc.get_quotes_with_seasonality(quotes=quotes)
        quotes_for_send = calc.get_quotes_for_send(quotes_with_seasonality)
        # print(quotes_for_send)

        resp = make_response(render_template("index.html", quotes=quotes_for_send))
        resp.headers["Content-type"] = "text/html; charset=utf-8"
        return resp

    return app


if __name__ == "__main__":
    application = create_app()
    application.run()
