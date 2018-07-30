import os
import dash

import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

from flask import Flask, render_template
# from runs import run_information



DATA_FOLDER = 'test-data/results-archive'
DATA_SUMMARY_FOLDER = 'qc'

server = Flask(__name__)
# runs_dash = dash.Dash(__name__, server=server, url_base_pathname='/dash')
# runs_dash.layout = run_information('171030_NB551023_0034_AHYF5YBGX2')


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
    # run_info = run_information(run_id)
    # return run_info.index()


if __name__ == '__main__':
    server.run(debug=True)
