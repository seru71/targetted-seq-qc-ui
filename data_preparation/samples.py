import pandas as pd

import path_processing
import data_preparation

from os.path import join as path_join


def get_coverage_sample_summary_table(run_id, sample_id):
    path = path_processing.get_coverage_sample_summary_path(run_id, sample_id)
    coverage_sample_summary = pd.read_csv(path, delimiter='\t', index_col=False).dropna()
    return coverage_sample_summary.to_html(classes='table table-sm table-hover', index=False)


def get_variations_sample_df(run_id, sample_id, save_pickle=False):
    def read_data(sample_path):
        table, table_lines = False, []
        with open(sample_path, 'r') as f:
            for line in f.readlines():
                if line.startswith('#CHROM') or table:
                    table = True
                    table_lines.append(line.strip().split('\t'))
        return table_lines

    def process_sample_vcf(table_lines):
        df = pd.DataFrame(table_lines)
        df.drop([2, 6], axis=1, inplace=True)
        df.columns = df.iloc[0]
        df.drop(0, inplace=True)
        return df

    def process_row(row):
        new_cols = row.FORMAT.split(':')
        new_cols_value = row[row.keys()[-1]].split(':')
        external_information = pd.Series(new_cols_value, index=new_cols)
        return row.append(external_information)

    important_columns = ['#CHROM', 'POS', 'REF', 'ALT', 'QUAL', 'GT', 'AD', 'DP']

    path = path_processing.get_sample_variations_path(run_id, sample_id)

    sample_folder_path = path_processing.get_sample_path(run_id, sample_id)

    pickle_path = path_join(sample_folder_path, f'{sample_id}.sample_variants.pkl')

    if path_processing.check_existence(pickle_path):
        return pd.read_pickle(pickle_path)[important_columns]

    lines = read_data(path)
    df = process_sample_vcf(lines)

    s = [process_row(row) for index, row in df.iterrows()]
    data = pd.DataFrame(s).drop('INFO', axis=1)

    df = data[['#CHROM', 'POS', 'REF', 'ALT', 'QUAL', 'GT', 'AD', 'DP']]

    if save_pickle:
        df.to_pickle(path_join(sample_folder_path, f'{sample_id}.sample_variants.pkl'))

    return data[important_columns]


def get_gene_coverage_sample_summary(run_id, sample_id):
    gene_coverage_path = path_processing.get_sample_gene_summary_path(run_id, sample_id)

    coverage_sample_gene_summary = pd.read_csv(gene_coverage_path, delimiter='\t', index_col=False)

    df = data_preparation.prepare_mean_columns_df(coverage_sample_gene_summary)
    df.fillna(-1, inplace=True)

    return df
