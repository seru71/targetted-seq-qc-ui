import plotly.graph_objs as go


def sample_summary_graph(df):
    x_label = ['Sample ' + x for x in df['Sample ID'].astype('str')]
    return dict(
        data=[
            dict(
                go.Bar(
                    x=x_label,
                    y=df['Mean'],
                    name='Mean'
                )
            ),
            dict(
                go.Bar(
                    x=x_label,
                    y=df['Above 20%'],
                    name='Above 20%')
            )
        ]
    )


def variants_graph(df):
    if df:
        x_label_variants = ['Sample ' + x for x in df['Sample'].astype('str')]
        return dict(
            data=[
                dict(
                    go.Bar(
                        x=x_label_variants,
                        y=df.nNonRefHom,
                        name='nNonRefHom',
                    )
                ),
                dict(
                    go.Bar(
                        x=x_label_variants,
                        y=df.nHets,
                        name='nHets',
                    )
                ),
                dict(
                    go.Bar(
                        x=x_label_variants,
                        y=df.nIndels,
                        name='nIndels',
                    )
                )
            ],
            layout=go.Layout(
                barmode='stack'
            )
        )
    return None
