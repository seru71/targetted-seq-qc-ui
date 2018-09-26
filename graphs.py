import plotly.graph_objs as go


def sample_summary_graph(df):
    x_label = ['Sample ' + x for x in df['Sample ID'].astype('str')]
    return dict(
        data=[
            dict(
                x=x_label,
                y=df['Mean'],
                name='Mean',
                type='bar'
            ),
            dict(
                x=x_label,
                y=df['Above 20%'],
                name='Above 20%',
                type='bar'
            )
        ]
    )


def variants_graph(df):
    if not type(df) == bool:
        x_label_variants = ['Sample ' + x for x in df['Sample'].astype('str')]
        return dict(
            data=[
                dict(
                    x=x_label_variants,
                    y=df.nNonRefHom,
                    name='nNonRefHom',
                    type='bar'
                ),
                dict(
                    x=x_label_variants,
                    y=df.nHets,
                    name='nHets',
                    type='bar'
                ),
                dict(
                    x=x_label_variants,
                    y=df.nIndels,
                    name='nIndels',
                    type='bar'
                )
            ],
            layout=go.Layout(
                barmode='stack'
            )
        )
    return None


def variants_annotations_graph(df):
    def get_trace(df, column):
        x_label = ['Sample ' + x for x in df['sample'].astype(str)]
        return dict(
            x=x_label,
            y=df[column],
            name=column,
            type='bar'
        )

    if df is False:
        return False

    columns = df.columns[1:]

    return dict(
        data=[get_trace(df, column) for column in columns]
    )