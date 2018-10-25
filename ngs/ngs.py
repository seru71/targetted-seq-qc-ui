import json
import plotly
import logging
import os
import time

from Crypto.Cipher import AES

import pandas as pd
from flask import Flask, render_template, send_from_directory, redirect, url_for, jsonify, request, abort

from ngs.graphs import *

import data_preparation
import path_processing as pp


server = Flask(__name__)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s:%(name)s:%(funcName)s:%(message)s')

file_handler = logging.FileHandler('logs/ngs.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


@server.route("/")
@server.route("/runs")
def runs():
    runs = pp.get_all_runs_names()
    logger.info("Runs page rendered.")
    return render_template('runs/runs.html', runs=runs)


@server.route("/runs/<run_id>", methods=['GET'])
def specific_run(run_id):
    runs = pp.get_all_runs_names()

    if run_id not in runs:
        logger.info('Redirected for incorrect run_id {}'.format(run_id))
        return redirect(url_for('runs'))

    # target coverage
    path = pp.get_sample_coverage_path(run_id)
    if pp.check_existence(path):
        sample_summary_table = data_preparation.get_summary(run_id)
    else:
        sample_summary_table = False

    # presenting plot
    path = pp.get_multisample_vcf_stats_path(run_id)
    if pp.check_existence(path):
        variants, variants_df = data_preparation.get_multisample_stats_df(run_id)
    else:
        variants, variants_df = False, False

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

    data = {'sample_summary_table': data_preparation.prepare_sample_summary_html_table(sample_summary_table, run_id),
            'graphJSON': graphJSON,
            'ids': ids,
            'variants': variants if variants else False,
            'variants_annotations': variants_annotations_df if variants_annotations_df is False else True,
            'coverage_sample_list': False,
            'run_id': run_id,
            'runs': runs,
            }

    # gene coverage
    summary_path = pp.get_sample_gene_coverage_path(run_id)
    if pp.check_existence(summary_path):
        data['coverage_sample_list_exists'] = True
        mean_cols_df = data_preparation.get_gene_summary(run_id)
        df = data_preparation.prepare_mean_columns_df(mean_cols_df)
        df.fillna(-1, inplace=True)
        data['coverage_sample_list'] = df.round(2).values.tolist()[:100]

    logger.info('Specific run_id page rendered correctly. {}'.format(run_id))
    return render_template('runs/run.html', **data)


@server.route('/download/<path:path>')
def download(path):
    logger.info('Access to file: {}'.format(path))
    return send_from_directory('data/runs/', path)


@server.route("/samples")
def samples():
    runs = pp.get_all_runs_names()
    samples = pp.samples_paths(runs)
    logger.info('Samples page rendered.')
    return render_template('samples/samples.html', samples=samples)


@server.route("/runs/<run_id>/<sample_id>", methods=['GET'])
def specific_sample(run_id, sample_id):
    if run_id not in pp.get_all_runs_names() or sample_id not in pp.get_samples_from_run_name(run_id):
        logger.info('Invalid sample_id or run_id.')
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

    logger.info('Specific sample loaded correctly. {} {}'.format(run_id, sample_id))
    return render_template('samples/sample.html', **data)


@server.errorhandler(404)
def page_not_found(error):
    logger.error('Page not found.')
    return render_template('page_not_found.html'), 404


@server.route("/sample_data")
def send_data():
    encryption_key = os.environ.get('ENCRYPTION_KEY')
    obj = AES.new(encryption_key, AES.MODE_CBC, 'This is an IV456')

    message = "The answer is no " * 32

    ciphertext = obj.encrypt(message)
    response = {
        'data': ciphertext.hex(),
        "signature": "dawid",
    }

    return jsonify(response), 200


@server.route("/data", methods=['GET', 'POST'])
def receive_data():
    def decrypt_data(data):
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        obj = AES.new(encryption_key, AES.MODE_CBC, 'This is an IV456')
        hex_data = bytes.fromhex(data)
        return obj.decrypt(hex_data).decode()

    def validate_signature(signature):
        return signature == 'dawid'

    if request.method == 'POST':
        data = json.loads(request.get_json())
        if not validate_signature(data['signature']):
            logger.info("Invalid signature.")
            abort(403, "Invalid signature.")

        # do something with
        decoded_information = decrypt_data(data['data'])
        with open(os.path.join('data_acquisition', '{}.txt'.format(time.time())), 'w') as incoming_data_file:
            incoming_data_file.write(decoded_information)
            logger.info("Data saved.")

        return "Successful data acquisition", 200
    else:
        abort(403)

    # obj = AES.new(encryption_key, AES.MODE_CBC, 'This is an IV456')
    # message = "The answer is no" * 32
    #
    # ciphertext = obj.encrypt(message)
    # response = {
    #     'data': ciphertext.hex(),
    # }
