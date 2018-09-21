import os
import glob
import pandas as pd

import json
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import data_preparation

import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request, url_for

DATA_FOLDER = os.path.join(*['static', 'test-data', 'results-archive'])
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
    x_label = ['Sample ' + x for x in sample_summary_table['Sample ID'].astype('str')]

    trace0 = go.Bar(
        x= x_label,
        y=sample_summary_table['Mean'],
        name='Mean'
    )
    trace1 = go.Bar(
        x=x_label,
        y=sample_summary_table['Above 20%'],
        name='Above 20%',
    )

    data = [trace0, trace1]
    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    unique_genes = set([x.split('_')[0] for x in mean_cols_df.Gene])

    with pd.option_context('display.max_colwidth', -1):
        sample_summary_table['Sample ID'] = sample_summary_table['Sample ID'].apply(
            lambda x: '<a href=\"/runs/{run_id}/{sample_id}">{sample_id}</a>'.format(sample_id=x, run_id=run_id))
        table = sample_summary_table.to_html(classes='table table-sm table-hover', escape=False, index=False)

    data = {'run_id': run_id,
            'sample_summary_table': table,
            'unique_genes': unique_genes,
            'runs': runs,
            'graphJSON': graphJSON}

    if request.method == 'POST' and request.form.get('gene_names'):
        try:
            data['genes'] = [x.strip() for x in request.form.get('gene_names').split(',')]

            mean_cols_df['gene_name'] = mean_cols_df.Gene.apply(lambda x: x.split('_')[0])
            df = mean_cols_df.loc[mean_cols_df['gene_name'].isin(data['genes'])]

            df.drop(columns=['gene_name'], inplace=True)
            df = data_preparation.prepare_mean_columns_df(df)
            data['selected_genes_df'] = df.to_html(classes='table table-sm table-hover', index=False)
        except Exception as e:
            print(e)
            pass

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


def get_coverage_sample_summary_path(run_id, sample_id):
    sample_path = os.path.join(DATA_FOLDER, run_id, sample_id)
    return os.path.join(sample_path, '{}.coverage.sample_summary'.format(sample_id))


def get_sample_gene_summary_path(run_id, sample_id):
    sample_path = os.path.join(DATA_FOLDER, run_id, sample_id)
    return os.path.join(sample_path, '{}.coverage.sample_gene_summary').format(sample_id)


def get_fastq_paths(run_id, sample_id):
    run_path = os.path.join(DATA_FOLDER, run_id)
    fastq_path_r1 = os.path.join(run_path, FASTQ, '{}_S1_R1_001.fastq.gz'.format(sample_id))
    fastq_path_r2 = os.path.join(run_path, FASTQ, '{}_S1_R2_001.fastq.gz'.format(sample_id))
    return fastq_path_r1, fastq_path_r2


def get_fastqc_report_path(run_id, sample_id, r):
    reports_path = os.path.join(DATA_FOLDER, run_id, DATA_SUMMARY_FOLDER, READ_QC)
    try:
        r_filename = glob.glob(reports_path + '/{}*R{}_001_fastqc.html'.format(sample_id, r))[0].split(os.sep)[-1]
        r_001_fastqc = os.path.join(reports_path, r_filename)
        return '../../' + r_001_fastqc.replace(os.sep, '/')
    except IndexError:
        pass
    return False


def get_fq_fastqc_path(run_id, sample_id, fq):
    reports_path = os.path.join(DATA_FOLDER, run_id, DATA_SUMMARY_FOLDER, READ_QC)
    return os.path.join(reports_path, '{}.fq{}_fastqc.html'.format(sample_id, fq))


@server.route("/runs/<run_id>/<sample_id>", methods=['GET', 'POST'])
def specific_sample(run_id, sample_id):
    data = {'run_id': run_id,
            'sample_id': sample_id,
            'fastq_path': None,
            'bam_path': None,
            'vcf_path': None,
            'samples': samples_paths(os.listdir(DATA_FOLDER))}

    coverage_sample_summary_path = get_coverage_sample_summary_path(run_id, sample_id)
    coverage_sample_gene_summary_path = get_sample_gene_summary_path(run_id, sample_id)

    sample_path = os.path.join(DATA_FOLDER, run_id, sample_id)

    # download files
    fastq_path_r1, fastq_path_r2 = get_fastq_paths(run_id, sample_id)

    data['fastq_path_r1'] = '../../' + fastq_path_r1.replace(os.sep, '/') if os.path.isfile(fastq_path_r1) else False
    data['fastq_path_r2'] = '../../' + fastq_path_r2.replace(os.sep, '/') if os.path.isfile(fastq_path_r2) else False

    bam_path = '{}/{}.dedup.bam'.format(sample_path.replace(os.sep, '/'), sample_id)
    bam_file_exists = os.path.isfile(bam_path.replace('/', os.sep))
    data['bam_path'] = '../../' + bam_path if bam_file_exists else False

    vcf_path = '{}/{}.vcf'.format(sample_path.replace(os.sep, '/'), sample_id)
    vcf_file_exists = os.path.isfile(vcf_path.replace('/', os.sep))
    data['vcf_path'] = '../../' + vcf_path if vcf_file_exists else False

    # reports
    fq1_fastqc = get_fq_fastqc_path(run_id, sample_id, 1)
    data['fq1_fastqc'] = '../../' + fq1_fastqc.replace(os.sep, '/') if os.path.isfile(fq1_fastqc) else False

    fq2_fastqc = get_fq_fastqc_path(run_id, sample_id, 2)
    data['fq2_fastqc'] = '../../' + fq2_fastqc.replace(os.sep, '/') if os.path.isfile(fq2_fastqc) else False

    data['R1_001_fastqc'] = get_fastqc_report_path(run_id, sample_id, 1)
    data['R2_001_fastqc'] = get_fastqc_report_path(run_id, sample_id, 2)

    coverage_sample_summary = pd.read_csv(coverage_sample_summary_path, delimiter='\t', index_col=False).dropna()
    coverage_sample_gene_summary = pd.read_csv(coverage_sample_gene_summary_path, delimiter='\t', index_col=False)

    data['coverage_sample_summary'] = coverage_sample_summary.to_html(classes='table table-sm table-hover', index=False)

    if request.method == 'POST' and request.form.get('gene_names'):
        try:
            data['genes'] = [x.strip() for x in request.form.get('gene_names').split(',')]

            coverage_sample_gene_summary['gene_name'] = coverage_sample_gene_summary.Gene.apply(lambda x: x.split('_')[0])
            df = coverage_sample_gene_summary.loc[coverage_sample_gene_summary['gene_name'].isin(data['genes'])]

            df.drop(columns=['gene_name'], inplace=True)

            df = data_preparation.prepare_mean_columns_df(df)

            with pd.option_context('display.max_colwidth', -1):
                data['coverage_sample_gene_summary'] = df.to_html(classes='table table-sm table-hover', index=False)
        except Exception as e:
            print(e)
            pass

    return render_template('sample.html', **data)


if __name__ == '__main__':
    if int(os.environ.get('FLASK_DEBUG', 0)):
        server.run(debug=True)
    else:
        server.run(host='0.0.0.0')
