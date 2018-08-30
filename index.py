import os

from flask import Flask, render_template


DATA_FOLDER = 'test-data/results-archive'
DATA_SUMMARY_FOLDER = 'qc'

server = Flask(__name__)


@server.route("/")
def index():
    return render_template('index.html')


@server.route("/runs")
def runs():
    runs = os.listdir(DATA_FOLDER)
    return render_template('runs.html', runs=runs)


@server.route("/runs/<run_id>")
def specific_run(run_id):
    return render_template('run.html', run_id=run_id)


if __name__ == '__main__':
    server.run(debug=True)
