import os
import json
import plotly

import pandas as pd
from flask import Flask, render_template, send_from_directory

from ngs.graphs import *

import data_preparation
import path_processing as pp


server = Flask(__name__)


@server.route("/")
@server.route("/runs")
def runs():
    runs = pp.get_all_runs_names()
    return render_template('runs/runs.html', runs=runs)


@server.route("/runs/<run_id>", methods=['GET', 'POST'])
def specific_run(run_id):
    sample_summary_table = data_preparation.get_summary(run_id)
    mean_cols_df = data_preparation.get_gene_summary(run_id)

    runs = pp.get_all_runs_names()

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


def samples_paths(runs):
    samples = {}

    def valid_sample(sample_name):
        try:
            return True if int(sample_name) else False
        except Exception:
            return False

    for run_id in runs:
        run_path = pp.get_run_path(run_id)
        samples[run_id] = ([(run_id, sample_id) for sample_id in os.listdir(run_path) if valid_sample(sample_id)])

    return samples


@server.route("/samples")
def samples():
    runs = pp.get_all_runs_names()
    samples = samples_paths(runs)
    return render_template('samples/samples.html', samples=samples)


@server.route("/runs/<run_id>/<sample_id>", methods=['GET', 'POST'])
def specific_sample(run_id, sample_id):
    data = {'run_id': run_id,
            'sample_id': sample_id,
            'samples': samples_paths(pp.get_all_runs_names())}

    # update dict with links to download files and reports
    data.update(links_to_external_download_data_and_reports(run_id, sample_id))

    data['coverage_sample_summary'] = data_preparation.get_coverage_sample_summary_table(run_id, sample_id)
    if pp.check_existence(pp.get_sample_variations_path(run_id, sample_id)):
        data['sample_variations'] = data_preparation.get_variations_sample_df(run_id, sample_id, True).values.tolist()[:100]
    else:
        data['sample_variations'] = False

    path = pp.get_sample_gene_summary_path(run_id, sample_id)
    coverage_sample_gene_summary = pd.read_csv(path, delimiter='\t', index_col=False)

    df = data_preparation.prepare_mean_columns_df(coverage_sample_gene_summary)
    df.fillna(-1, inplace=True)

    data['coverage_sample_list'] = df.values.tolist()[:100]

    return render_template('samples/sample.html', **data)


def links_to_external_download_data_and_reports(run_id, sample_id):
    data = {}

    # download files
    data['fastq_path_r1'] = pp.get_fastq_r1_download_path(run_id, sample_id).replace(os.sep, '/')
    data['fastq_path_r2'] = pp.get_fastq_r2_download_path(run_id, sample_id).replace(os.sep, '/')
    data['bam_path'] = pp.get_bam_download_path(run_id, sample_id).replace(os.sep, '/')
    data['vcf_path'] = pp.get_vcf_download_path(run_id, sample_id).replace(os.sep, '/')

    # reports
    data['fq1_fastqc'] = pp.get_fastq_fq1_download_path(run_id, sample_id).replace(os.sep, '/')
    data['fq2_fastqc'] = pp.get_fastq_fq2_download_path(run_id, sample_id).replace(os.sep, '/')
    data['R1_001_fastqc'] = pp.get_fastqc_report_path(run_id, sample_id, 1).replace(os.sep, '/')
    data['R2_001_fastqc'] = pp.get_fastqc_report_path(run_id, sample_id, 2).replace(os.sep, '/')

    return data
