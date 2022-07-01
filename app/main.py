import logging
from os import path

from flask import Flask, flash, redirect, render_template, request
from werkzeug.utils import secure_filename

from seasonality import get_quotes_for_send

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}


def create_app():
    app = Flask(__name__)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    # For demo only. In prod use environment variable and decouple
    app.config["SECRET_KEY"] = '2356782959278652876'

    @app.route("/", methods=["GET"])
    def main_page():
        return render_template("index.html")

    @app.route("/", methods=["POST"])
    def seasonality_page():
        """
        Return template with seasonality chart
        """
        if "file" not in request.files:
            flash("Error. No file part.")
            return redirect(request.url)
        file = request.files["file"]

        if file.filename == "":
            flash("Error. No selected file")
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = path.join(app.config["UPLOAD_FOLDER"], filename)
            try:
                file.save(file_path)
            except Exception as e:
                logger.info(f"File save error. {e}")
                flash("Internal server error")
                return redirect(request.url)

            quotes_for_send = get_quotes_for_send(file_path=file_path)
            return render_template("seasonality.html", quotes=quotes_for_send)
        else:
            flash("Error. File extension must be .csv")
            return redirect(request.url)

    return app


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == "__main__":
    application = create_app()
    application.run(host='0.0.0.0', port=80)
