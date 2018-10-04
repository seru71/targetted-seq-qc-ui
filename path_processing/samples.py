from glob import glob

from .runs import get_run_path

from .constants import *


def get_sample_path(run_id, sample_id):
    return os.path.join(get_run_path(run_id), sample_id)


def get_samples_from_run_name(run_id):
    def valid_sample(sample_name):
        try:
            return True if int(sample_name) else False
        except ValueError:
            return False

    run_path = get_run_path(run_id)

    return [sample_id for sample_id in os.listdir(run_path) if valid_sample(sample_id)]


# tables and graphs
def get_sample_variations_path(run_id, sample_id):
    return os.path.join(get_sample_path(run_id, sample_id), '{}.vcf'.format(sample_id))


def get_sample_gene_summary_path(run_id, sample_id):
    sample_path = os.path.join(FOLDER_WITH_RUNS, run_id, sample_id)
    return os.path.join(sample_path, '{}.coverage.sample_gene_summary'.format(sample_id))


def get_coverage_sample_summary_path(run_id, sample_id):
    sample_path = os.path.join(FOLDER_WITH_RUNS, run_id, sample_id)
    return os.path.join(sample_path, '{}.coverage.sample_summary'.format(sample_id))


# reports
def get_fastq_fq1_download_path(run_id, sample_id):
    return os.path.join(run_id, DATA_SUMMARY_FOLDER, READ_QC, '{}.fq1_fastqc.html'.format(sample_id))


def get_fastq_fq2_download_path(run_id, sample_id):
    return os.path.join(run_id, DATA_SUMMARY_FOLDER, READ_QC, '{}.fq2_fastqc.html'.format(sample_id))


def get_fastqc_report_path(run_id, sample_id, r):
    reports_path = os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER, READ_QC)
    try:
        r_filename = glob(os.path.join(reports_path) + '/{}*R{}_001_fastqc.html'.format(sample_id, r))[0].split(os.sep)[-1]
        r_001_fastqc = os.path.join(run_id, DATA_SUMMARY_FOLDER, READ_QC, r_filename)
        return r_001_fastqc
    except IndexError:
        pass
    return False


# download files
def get_fastq_r1_download_path(run_id, sample_id):
    return os.path.join(run_id, FASTQ, '{}_S1_R1_001.fastq.gz'.format(sample_id))


def get_fastq_r2_download_path(run_id, sample_id):
    return os.path.join(run_id, FASTQ, '{}_S1_R2_001.fastq.gz'.format(sample_id))


def get_bam_download_path(run_id, sample_id):
    return os.path.join(run_id, sample_id, '{}.dedup.bam'.format(sample_id))


def get_vcf_download_path(run_id, sample_id):
    return os.path.join(run_id, sample_id, '{}.vcf'.format(sample_id))
