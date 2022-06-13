import logging
import calculations as calc
from os import path

from flask import Flask, make_response, render_template, request, flash, redirect
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}


def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = '8f42a73054b1749f8f58848be5e6502c'

    @app.route("/", methods=['GET', 'POST'])
    def main_page():
        """
        Return web page with choose file form
        """
        if request.method == 'GET':
            response = make_response(render_template("index.html"))
            response.headers["Content-type"] = "text/html; charset=utf-8"
            return response

        else:
            if 'file' not in request.files:
                flash('Error. No file part.')
                return redirect(request.url)
            file = request.files['file']

            if file.filename == '':
                flash('Error. No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                logger.info(filename)
                quotes = calc.get_quotes_from_csv(file_path=file_path)
                quotes_with_seasonality = calc.get_quotes_with_seasonality(quotes=quotes)
                quotes_for_send = calc.get_quotes_for_send(quotes_with_seasonality)
                response = make_response(render_template("seasonality.html", quotes=quotes_for_send))
                response.headers["Content-type"] = "text/html; charset=utf-8"

                return response
            else:
                flash('Error. File extension must be .csv')
                return redirect(request.url)

    return app


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    application = create_app()
    application.run()
