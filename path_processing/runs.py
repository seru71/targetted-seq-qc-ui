from .constants import *


def get_run_path(run_id):
    return os.path.join(FOLDER_WITH_RUNS, run_id)


def get_all_runs_names():
    return os.listdir(FOLDER_WITH_RUNS)


# tables and graphs
def get_sample_coverage_path(run_id):
    return os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER, f'{run_id}.sample_coverage')


def get_sample_gene_coverage_path(run_id):
    return os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER, f'{run_id}.gene_coverage')


def get_annotated_variants_stats_path(run_id):
    reports_path = os.path.join(FOLDER_WITH_RUNS, run_id, DATA_SUMMARY_FOLDER)
    return os.path.join(reports_path, '{}.annotated_variant_stats'.format(run_id))


def get_multisample_vcf_stats_path(run_id):
    return os.path.join(get_run_path(run_id), DATA_SUMMARY_FOLDER, '{}.multisample.vcf.stats'.format(run_id))
