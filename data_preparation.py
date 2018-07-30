import pandas as pd
import os

from index import DATA_FOLDER, DATA_SUMMARY_FOLDER


def get_summary(run_id):
    columns = ['sample_id', 'total', 'mean', '%_bases_above_5', '%_bases_above_10', '%_bases_above_20']
    new_columns = ['Sample ID', 'Total', 'Mean', 'Above 5%', 'Above 10%', 'Above 20%']

    summary_path = os.path.join(DATA_FOLDER, run_id, DATA_SUMMARY_FOLDER, f'{run_id}.sample_coverage')

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
    summary_path = os.path.join(DATA_FOLDER, run_id, DATA_SUMMARY_FOLDER, f'{run_id}.gene_coverage')

    sample_gene_summary = pd.read_csv(summary_path, delimiter='\t', index_col=False)
    return sample_gene_summary


if __name__ == '__main__':
    # all_metrics = pd.read_csv(os.path.join(DATA_FILE, 'all_sample.alignment_metrics'), delimiter='\t')
    print(get_summary('171030_NB551023_0034_AHYF5YBGX2'))
    print(get_gene_summary('171030_NB551023_0034_AHYF5YBGX2'))
