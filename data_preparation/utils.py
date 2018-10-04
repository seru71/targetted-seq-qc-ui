def prepare_mean_columns_df(df):
    columns = df.columns.tolist()
    unique_columns = list(set(["_".join(col.split('_')[1:]) for col in columns[3:]]))

    for column in unique_columns:
        columns_for_mean = [original_column_name for original_column_name in df.columns if
                            column in original_column_name]
        df.loc[:, column] = df[columns_for_mean].mean(axis=1)

    return df.drop(columns=columns[3:])
