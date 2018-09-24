import os

from glob import glob
from flask import url_for


FOLDER_WITH_RUNS = os.path.join(*['test-data', 'results-archive'])
DATA_SUMMARY_FOLDER = 'qc'
FASTQ = 'fastqs'
READ_QC = 'read_qc'


def check_existence(path):
    return os.path.isfile(get_system_path(path))


def get_url_for(path):
    if check_existence(path):
        return url_for('static', filename=path.replace(os.sep, '/'))
    return False


def get_system_path(path):
    return os.path.join('static', path)


def get_coverage_sample_summary_path(run_id, sample_id):
    sample_path = os.path.join(FOLDER_WITH_RUNS, run_id, sample_id)
    return os.path.join(sample_path, '{}.coverage.sample_summary'.format(sample_id))


def get_sample_coverage_path(run_id):
    return os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER, f'{run_id}.sample_coverage')


def get_sample_gene_coverage_path(run_id):
    return os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER, f'{run_id}.gene_coverage')


def get_sample_gene_summary_path(run_id, sample_id):
    sample_path = os.path.join(FOLDER_WITH_RUNS, run_id, sample_id)
    return os.path.join(sample_path, '{}.coverage.sample_gene_summary'.format(sample_id))


def get_fastq_paths(run_id, sample_id):
    run_path = os.path.join(FOLDER_WITH_RUNS, run_id)
    fastq_path_r1 = os.path.join(run_path, FASTQ, '{}_S1_R1_001.fastq.gz'.format(sample_id))
    fastq_path_r2 = os.path.join(run_path, FASTQ, '{}_S1_R2_001.fastq.gz'.format(sample_id))
    return fastq_path_r1, fastq_path_r2


def get_run_path(run_id):
    return os.path.join(FOLDER_WITH_RUNS, run_id)


def get_sample_path(run_id, sample_id):
    return os.path.join(get_run_path(run_id), sample_id)


def get_bam_path(run_id, sample_id):
    return os.path.join(get_sample_path(run_id, sample_id), '{}.dedup.bam'.format(sample_id))


def get_vcf_path(run_id, sample_id):
    return os.path.join(get_sample_path(run_id, sample_id), '{}.vcf'.format(sample_id))


def get_fq_fastqc_path(run_id, sample_id, fq):
    reports_path = os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER, READ_QC)
    return os.path.join(reports_path, '{}.fq{}_fastqc.html'.format(sample_id, fq))


def get_fastqc_report_path(run_id, sample_id, r):
    reports_path = os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER, READ_QC)
    try:
        r_filename = glob(os.path.join('static', reports_path) + '/{}*R{}_001_fastqc.html'.format(sample_id, r))[0].split(os.sep)[-1]
        r_001_fastqc = os.path.join(reports_path, r_filename)
        return r_001_fastqc
    except IndexError:
        pass
    return False


def get_multisample_vcf_stats_path(run_id):
    return os.path.join(get_run_path(run_id), DATA_SUMMARY_FOLDER, '{}.multisample.vcf.stats'.format(run_id))
