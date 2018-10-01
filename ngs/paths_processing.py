import os

from glob import glob
from flask import url_for


FOLDER_WITH_RUNS = os.path.join(*['ngs', 'data', 'runs'])
DATA_SUMMARY_FOLDER = 'qc'
FASTQ = 'fastqs'
READ_QC = 'read_qc'


def get_system_path(file_path):
    return os.path.join(FOLDER_WITH_RUNS, file_path)


def check_existence(path):
    return os.path.isfile(path)


def get_url_for(path):
    if check_existence(path):
        return path.replace(os.sep, '/')
    return False


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


def get_fastq_r1_download_path(run_id, sample_id):
    return os.path.join(run_id, FASTQ, '{}_S1_R1_001.fastq.gz'.format(sample_id))


def get_fastq_r2_download_path(run_id, sample_id):
    return os.path.join(run_id, FASTQ, '{}_S1_R2_001.fastq.gz'.format(sample_id))


def get_bam_download_path(run_id, sample_id):
    return os.path.join(run_id, sample_id, '{}.dedup.bam'.format(sample_id))


def get_vcf_download_path(run_id, sample_id):
    return os.path.join(run_id, sample_id, '{}.vcf'.format(sample_id))


def get_fastq_fq1_download_path(run_id, sample_id):
    return os.path.join(run_id, DATA_SUMMARY_FOLDER, READ_QC, '{}.fq1_fastqc.html'.format(sample_id))


def get_fastq_fq2_download_path(run_id, sample_id):
    return os.path.join(run_id, DATA_SUMMARY_FOLDER, READ_QC, '{}.fq2_fastqc.html'.format(sample_id))


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


def get_annotated_variants_stats_path(run_id):
    reports_path = os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER)
    return os.path.join(reports_path, '{}.annotated_variant_stats'.format(run_id))


def get_fastqc_report_path(run_id, sample_id, r):
    reports_path = os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER, READ_QC)
    try:
        r_filename = glob(os.path.join(reports_path) + '/{}*R{}_001_fastqc.html'.format(sample_id, r))[0].split(os.sep)[-1]
        r_001_fastqc = os.path.join(run_id, DATA_SUMMARY_FOLDER, READ_QC, r_filename)
        return r_001_fastqc
    except IndexError:
        pass
    return False


def get_multisample_vcf_stats_path(run_id):
    return os.path.join(get_run_path(run_id), DATA_SUMMARY_FOLDER, '{}.multisample.vcf.stats'.format(run_id))


def get_sample_variations_path(run_id, sample_id):
    return os.path.join(get_sample_path(run_id, sample_id), '{}.vcf'.format(sample_id))

