import os
import pandas as pd

import json
import plotly

from ngs import paths_processing as pp, data_preparation

from ngs.graphs import *
from flask import Flask, render_template

DATA_FOLDER = os.path.join(*['ngs', 'data', 'runs'])
DATA_SUMMARY_FOLDER = 'qc'
FASTQ = 'fastqs'
READ_QC = 'read_qc'

server = Flask(__name__)


@server.route("/")
@server.route("/runs")
def runs():
    runs = os.listdir(DATA_FOLDER)
    return render_template('runs.html', runs=runs)


@server.route("/runs/<run_id>", methods=['GET', 'POST'])
def specific_run(run_id):
    sample_summary_table = data_preparation.get_summary(run_id)
    mean_cols_df = data_preparation.get_gene_summary(run_id)

    runs = os.listdir(DATA_FOLDER)

    # presenting plot
    variants, variants_df = data_preparation.get_multisample_stats_df(run_id)

    # variants annotations
    path = pp.get_annotated_variants_stats_path(run_id)
    if pp.check_existence(path, system_path=True):
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

    unique_genes = set([x.split('_')[0] for x in mean_cols_df.Gene])

    data = {'run_id': run_id,
            'sample_summary_table': data_preparation.prepare_sample_summary_html_table(sample_summary_table, run_id),
            'unique_genes': unique_genes,
            'runs': runs,
            'graphJSON': graphJSON,
            'ids': ids,
            'variants': variants if variants else False,
            'variants_annotations': variants_annotations_df if variants_annotations_df is False else True}

    df = data_preparation.prepare_mean_columns_df(mean_cols_df)
    df.fillna(-1, inplace=True)
    data['coverage_sample_list'] = df.values.tolist()

    return render_template('run.html', **data)


def samples_paths(runs):
    samples = {}

    def valid_sample(sample_name):
        try:
            return True if int(sample_name) else False
        except Exception:
            return False

    for run_id in runs:
        run_path = os.path.join(DATA_FOLDER, run_id)
        samples[run_id] = ([(run_id, sample_id) for sample_id in os.listdir(run_path) if valid_sample(sample_id)])

    return samples


@server.route("/samples")
def samples():
    runs = os.listdir(DATA_FOLDER)
    samples = samples_paths(runs)

    return render_template('samples.html', samples=samples)


@server.route("/runs/<run_id>/<sample_id>", methods=['GET', 'POST'])
def specific_sample(run_id, sample_id):
    data = {'run_id': run_id,
            'sample_id': sample_id,
            'samples': samples_paths(os.listdir(DATA_FOLDER))}

    # update dict with links to download files and reports
    data.update(links_to_external_download_data_and_reports(run_id, sample_id))

    data['coverage_sample_summary'] = get_coverage_sample_summary_table(run_id, sample_id)
    if pp.check_existence(pp.get_sample_variations_path(run_id, sample_id), system_path=False):
        data['sample_variations'] = data_preparation.get_variations_sample_df(run_id, sample_id, True).values.tolist()
    else:
        data['sample_variations'] = False

    path = pp.get_sample_gene_summary_path(run_id, sample_id)
    coverage_sample_gene_summary = pd.read_csv(path, delimiter='\t', index_col=False)

    df = data_preparation.prepare_mean_columns_df(coverage_sample_gene_summary)
    df.fillna(-1, inplace=True)

    data['coverage_sample_list'] = df.values.tolist()

    return render_template('sample.html', **data)


def get_coverage_sample_summary_table(run_id, sample_id):
    path = pp.get_coverage_sample_summary_path(run_id, sample_id)
    coverage_sample_summary = pd.read_csv(path, delimiter='\t', index_col=False).dropna()
    return coverage_sample_summary.to_html(classes='table table-sm table-hover', index=False)


def links_to_external_download_data_and_reports(run_id, sample_id):
    data = {}

    # download files
    fastq_path_r1, fastq_path_r2 = pp.get_fastq_paths(run_id, sample_id)

    data['fastq_path_r1'] = pp.get_url_for(fastq_path_r1)
    data['fastq_path_r2'] = pp.get_url_for(fastq_path_r2)
    data['bam_path'] = pp.get_url_for(pp.get_bam_path(run_id, sample_id))
    data['vcf_path'] = pp.get_url_for(pp.get_vcf_path(run_id, sample_id))

    # reports
    data['fq1_fastqc'] = pp.get_url_for(pp.get_fq_fastqc_path(run_id, sample_id, 1))
    data['fq2_fastqc'] = pp.get_url_for(pp.get_fq_fastqc_path(run_id, sample_id, 2))
    data['R1_001_fastqc'] = pp.get_url_for(pp.get_fastqc_report_path(run_id, sample_id, 1))
    data['R2_001_fastqc'] = pp.get_url_for(pp.get_fastqc_report_path(run_id, sample_id, 2))

    return data
