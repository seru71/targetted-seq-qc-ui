import os
import pandas as pd

import data_preparation

from flask import Flask, render_template, request

DATA_FOLDER = os.path.join(*['static', 'test-data', 'results-archive'])
DATA_SUMMARY_FOLDER = 'qc'

server = Flask(__name__)


@server.route("/")
def index():
    return render_template('index.html')


@server.route("/runs")
def runs():
    runs = os.listdir(DATA_FOLDER)
    return render_template('runs.html', runs=runs)


@server.route("/samples")
def samples():
    runs = os.listdir(DATA_FOLDER)
    samples = {}

    def valid_sample(sample_name):
        try:
            return True if int(sample_name) else False
        except Exception:
            return False

    for run_id in runs:
        run_path = os.path.join(DATA_FOLDER, run_id)
        samples[run_id] = ([(run_id, sample_id) for sample_id in os.listdir(run_path) if valid_sample(sample_id)])

    return render_template('samples.html', samples=samples)


@server.route("/samples/<run_id>/<sample_id>", methods=['GET', 'POST'])
def specific_sample(run_id, sample_id):
    data = {'run_id': run_id, 'sample_id': sample_id, 'fastq_path': None, 'bam_path': None, 'vcf_path': None}

    sample_path = os.path.join(DATA_FOLDER, run_id, sample_id)
    coverage_sample_summary_path = (os.path.join(sample_path, '{}.coverage.sample_summary'.format(sample_id)))
    coverage_sample_gene_summary_path = (os.path.join(sample_path, '{}.coverage.sample_gene_summary').format(sample_id))

    data['fastq_path'] = None
    data['bam_path'] = '../../{}/{}.dedup.bam'.format(sample_path.replace(os.sep, '/'), sample_id)
    data['vcf_path'] = '../../{}/{}.vcf'.format(sample_path.replace(os.sep, '/'), sample_id)

    coverage_sample_summary = pd.read_csv(coverage_sample_summary_path, delimiter='\t', index_col=False).dropna()
    coverage_sample_gene_summary = pd.read_csv(coverage_sample_gene_summary_path, delimiter='\t', index_col=False)

    data['coverage_sample_summary'] = coverage_sample_summary.to_html(classes='table table-sm table-hover')

    if request.method == 'POST' and request.form.get('gene_names'):
        try:
            data['genes'] = [x.strip() for x in request.form.get('gene_names').split(',')]

            coverage_sample_gene_summary['gene_name'] = coverage_sample_gene_summary.Gene.apply(lambda x: x.split('_')[0])
            df = coverage_sample_gene_summary.loc[coverage_sample_gene_summary['gene_name'].isin(data['genes'])]

            df.drop(columns=['gene_name'], inplace=True)

            df = data_preparation.prepare_mean_columns_df(df)

            data['coverage_sample_gene_summary'] = df.to_html(classes='table table-sm table-hover')
        except Exception as e:
            print(e)
            pass

    return render_template('sample.html', **data)


@server.route("/runs/<run_id>", methods=['GET', 'POST'])
def specific_run(run_id):
    sample_summary_table = data_preparation.get_summary(run_id)
    mean_cols_df = data_preparation.get_gene_summary(run_id)

    unique_genes = set([x.split('_')[0] for x in mean_cols_df.Gene])

    data = {'run_id': run_id,
            'sample_summary_table': sample_summary_table.to_html(classes='table table-sm table-hover'),
            'unique_genes': unique_genes}

    if request.method == 'POST' and request.form.get('gene_names'):
        try:
            data['genes'] = [x.strip() for x in request.form.get('gene_names').split(',')]

            mean_cols_df['gene_name'] = mean_cols_df.Gene.apply(lambda x: x.split('_')[0])
            df = mean_cols_df.loc[mean_cols_df['gene_name'].isin(data['genes'])]

            df.drop(columns=['gene_name'], inplace=True)
            df = data_preparation.prepare_mean_columns_df(df)
            data['selected_genes_df'] = df.to_html(classes='table table-sm table-hover')
        except Exception as e:
            print(e)
            pass

    return render_template('run.html', **data)


if __name__ == '__main__':
    if int(os.environ.get('FLASK_DEBUG'), 0):
        server.run(debug=True)
    else:
        server.run(host='0.0.0.0')
