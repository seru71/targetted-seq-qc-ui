import json
import plotly
import logging
import os
import datetime
import base64


import pandas as pd
from flask import Flask, render_template, send_from_directory, redirect, url_for, jsonify, request, abort

from ngs.graphs import *
from data_share.DataShare import DataShare

import data_preparation
import path_processing as pp
from tabix_wrapper import tabix_query


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


@server.route("/sample-data")
def send_data():
    encrypted = DataShare.encrypt_data("The message sdfsdlksjflksjflsdkj.")
    # response keys must be sorted
    response = {
        "data": encrypted,
        "name": 'Laboratory-Warsaw',
    }
    print('Data send: ' + json.dumps(response))

    response.update({'signature': DataShare.get_signature_for_message(response)})

    return jsonify(response), 200


@server.route("/data", methods=['GET', 'POST'])
def receive_data():
    if request.method == 'POST':
        data = json.loads(request.get_json())
        print('Data recivied: ' + json.dumps(data))
        if not DataShare.validate_signature(data):
            logger.info("Invalid signature.")
            abort(403, "Invalid signature.")

        decoded_information = DataShare.decrypt_data(data['data'])
        filename = str(datetime.datetime.now()).replace(':', "--")
        with open(os.path.join('data_acquisition', '{}.txt'.format(filename)), 'w') as incoming_data_file:
            incoming_data_file.write(decoded_information)
            logger.info("Data saved.")

        return "Successful data acquisition", 200
    else:
        abort(403)


@server.route('/sample-node', methods=['GET', 'POST'])
def sample_node():

    path = os.path.join('keys', 'public.key')
    with open(path, 'rb') as file:
        public_key = file.read()

    response = {
        'address': '0.0.0.0',
        'name': 'Laboratory-Warsaw2',
        'public_key': DataShare.encrypt_data(base64.b64encode(public_key).decode()),
    }

    response.update({'signature': DataShare.get_signature_for_message(response)})

    return jsonify(response), 200


@server.route('/add-node', methods=['GET', 'POST'])
def add_node():
    if request.method == 'POST':
        data = json.loads(request.get_json())
        if not DataShare.validate_signature(data):
            logger.info('Invalid signature add-node')
            abort(403, 'Invalid signature.')

        with open(os.path.join('nodes', '{}.json'.format(data['name'])), 'w') as file:
            json.dump(data, file)

        with open(os.path.join('nodes', '{}.key'.format(data['name'])), 'w') as file:
            file.write(base64.b64decode(DataShare.decrypt_data(data['public_key'])).decode())

        return 'Success', 200
    abort(403)


@server.route('/variants', methods=['GET', 'POST'])
def variants_public():

    variants_path = os.path.join(os.getcwd(), 'ngs', 'data', 'variants', 'ngs')

    chrom21 = os.path.join(variants_path, 'gnomad.exomes.r2.0.2.sites.ACAFAN.tsv.gz')

    chromosome_results = tabix_query(chrom21, 21, 9825797, 9825799)

    response = {'result': list(chromosome_results)}

    if request.method == 'POST':
        return "Dawiddddd", 200
    return json.dumps(response), 200
