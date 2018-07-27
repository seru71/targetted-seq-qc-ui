from flask import Flask, render_template
import os


DATA_FOLDER = 'test-data/results-archive'


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/runs")
def runs():
    runs = os.listdir(DATA_FOLDER)
    return render_template('runs.html', runs=runs)


@app.route("/runs/<run_id>")
def specific_run(run_id):
    return run_id


if __name__ == '__main__':
    app.run(debug=True)
