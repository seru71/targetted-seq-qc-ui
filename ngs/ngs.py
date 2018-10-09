import json
import plotly

import pandas as pd
from flask import Flask, render_template, send_from_directory, redirect, url_for

from ngs.graphs import *

import data_preparation
import path_processing as pp


server = Flask(__name__)


@server.route("/")
@server.route("/runs")
def runs():
    runs = pp.get_all_runs_names()
    return render_template('runs/runs.html', runs=runs)


@server.route("/runs/<run_id>", methods=['GET'])
def specific_run(run_id):
    runs = pp.get_all_runs_names()

    if run_id not in runs:
        return redirect(url_for('runs'))

    sample_summary_table = data_preparation.get_summary(run_id)
    mean_cols_df = data_preparation.get_gene_summary(run_id)

    # presenting plot
    variants, variants_df = data_preparation.get_multisample_stats_df(run_id)

    # variants annotations
    path = pp.get_annotated_variants_stats_path(run_id)
    if pp.check_existence(path):
        variants_annotations_df = pd.read_csv(path, delimiter='\t')
    else:
        variants_annotations_df = False

    graphs = [
        sample_summary_graph(sample_summary_table),
        variants_graph(variants_df),
        variants_annotations_graph(variants_annotations_df),
    ]

    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    data = {'run_id': run_id,
            'sample_summary_table': data_preparation.prepare_sample_summary_html_table(sample_summary_table, run_id),
            'runs': runs,
            'graphJSON': graphJSON,
            'ids': ids,
            'variants': variants if variants else False,
            'variants_annotations': variants_annotations_df if variants_annotations_df is False else True}

    df = data_preparation.prepare_mean_columns_df(mean_cols_df)
    df.fillna(-1, inplace=True)
    data['coverage_sample_list'] = df.round(2).values.tolist()[:100]

    return render_template('runs/run.html', **data)


@server.route('/download/<path:path>')
def download(path):
    return send_from_directory('data/runs/', path)


@server.route("/samples")
def samples():
    runs = pp.get_all_runs_names()
    samples = pp.samples_paths(runs)
    return render_template('samples/samples.html', samples=samples)


@server.route("/runs/<run_id>/<sample_id>", methods=['GET'])
def specific_sample(run_id, sample_id):
    if run_id not in pp.get_all_runs_names() or sample_id not in pp.get_samples_from_run_name(run_id):
        return redirect(url_for('samples'))

    data = {'run_id': run_id,
            'sample_id': sample_id,
            'samples': pp.samples_paths(pp.get_all_runs_names()),
            'gene_coverage_exists': True,
            'sample_variants_exists': True,
            'coverage_sample_summary_exists': True}

    # update data dict with tables and other data information
    data.update(data_preparation.prepare_tables_for_sample_page(run_id, sample_id))

    # update dict with links to download files and reports
    data.update(data_preparation.links_to_external_download_data_and_reports(run_id, sample_id))

    return render_template('samples/sample.html', **data)


@server.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
