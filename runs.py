import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

from data_preparation import get_sample_summary, get_sample_gene_summary, prepare_mean_columns_df


def run_information():
    sample_summary = get_sample_summary()
    sample_gene_summary = get_sample_gene_summary()
    unique_genes = set([x.split('_')[0] for x in sample_gene_summary.Gene])

    app = dash.Dash()

    app.layout = html.Div(children=[
        html.H2('1. Coverage summary'),

        dt.DataTable(rows=sample_summary.to_dict('records'),
                     columns=sample_summary.columns),

        html.H2('2. Gene coverage'),

        dcc.Dropdown(
            id='gene',
            options=[{'label': gene_name, 'value': gene_name} for gene_name in unique_genes],
            multi=True,
        ),
        html.Div(id='gene_selection'),

        html.H2('3. Variants')
    ])

    @app.callback(
        dash.dependencies.Output('gene_selection', 'children'),
        [dash.dependencies.Input('gene', 'value')])
    def generate_gene_summary(value):
        if value is None:
            return "Genes will appear after selection."

        sample_gene_summary['gene_name'] = sample_gene_summary.Gene.apply(lambda x: x.split('_')[0])
        df = sample_gene_summary.loc[sample_gene_summary['gene_name'].isin(value)]

        df.drop(columns=['gene_name'], inplace=True)

        df = prepare_mean_columns_df(df)

        table = dt.DataTable(rows=df.to_dict('records'), columns=df.columns)

        return table

    return app


if __name__ == '__main__':
    app = run_information()
    app.run_server(debug=True)
