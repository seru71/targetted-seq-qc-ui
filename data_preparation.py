import pandas as pd

import paths_processing

from os.path import join as path_join


def get_summary(run_id):
    columns = ['sample_id', 'total', 'mean', '%_bases_above_5', '%_bases_above_10', '%_bases_above_20']
    new_columns = ['Sample ID', 'Total', 'Mean', 'Above 5%', 'Above 10%', 'Above 20%']

    summary_path = paths_processing.get_system_path(paths_processing.get_sample_coverage_path(run_id))

    sample_summary = pd.read_csv(summary_path, delimiter='\t', index_col=False, usecols=columns)
    sample_summary.rename(columns=dict(zip(columns, new_columns)), inplace=True)

    sample_summary.drop(sample_summary.index[-1], inplace=True)

    return sample_summary[new_columns]


def prepare_mean_columns_df(df):
    columns = df.columns.tolist()
    unique_columns = list(set(["_".join(col.split('_')[1:]) for col in columns[3:]]))

    for column in unique_columns:
        columns_for_mean = [original_column_name for original_column_name in df.columns if
                            column in original_column_name]
        df[column] = df[columns_for_mean].mean(axis=1)

    return df.drop(columns=columns[3:])


def get_gene_summary(run_id):
    summary_path = paths_processing.get_system_path(paths_processing.get_sample_gene_coverage_path(run_id))

    sample_gene_summary = pd.read_csv(summary_path, delimiter='\t', index_col=False)
    return sample_gene_summary


def extract_data_from_multisample_stats(path):
    lines = []
    with open(path, 'r') as file:
        for line in file.readlines():
            if line.startswith('PSC'):
                lines.append(line.strip().split('\t'))

    return lines


def get_multisample_stats_df(run_id):
    path = paths_processing.get_multisample_vcf_stats_path(run_id)

    if not paths_processing.check_existence(path):
        return False, False

    lines = extract_data_from_multisample_stats(paths_processing.get_system_path(path))
    labels = ['PSC', 'id', 'Sample', 'nRefHom', 'nNonRefHom', 'nHets', 'nTransitions', 'nTransversions', 'nIndels',
              'average depth', 'nSingletons', 'nHapRef', 'nHapAlt', 'nMissing']

    df = pd.DataFrame(lines, columns=labels)
    df.drop(columns=['PSC', 'id'], axis=1, inplace=True)
    df['Total'] = df['nNonRefHom'] + df['nHets'] + df['nIndels']

    return df.to_html(classes='table table-sm table-hover', index=False), df


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

    IMPORTANT_COLUMNS = ['#CHROM', 'POS', 'REF', 'ALT', 'QUAL', 'GT', 'AD', 'DP']

    path = paths_processing.get_sample_variations_path(run_id, sample_id)
    system_path = paths_processing.get_system_path(path)

    sample_folder_path = paths_processing.get_system_path(paths_processing.get_sample_path(run_id, sample_id))

    pickle_path = path_join(sample_folder_path, f'{sample_id}.sample_variants.pkl')

    if paths_processing.check_existence(pickle_path, system_path=True):
        return pd.read_pickle(pickle_path)[IMPORTANT_COLUMNS].iloc[:10]

    lines = read_data(system_path)
    df = process_sample_vcf(lines)

    s = [process_row(row) for index, row in df.iterrows()]
    data = pd.DataFrame(s).drop('INFO', axis=1)

    df = data[['#CHROM', 'POS', 'REF', 'ALT', 'QUAL', 'GT', 'AD', 'DP']]

    if save_pickle:
        df.to_pickle(path_join(sample_folder_path, f'{sample_id}.sample_variants.pkl'))

    return data[IMPORTANT_COLUMNS].iloc[:10]
