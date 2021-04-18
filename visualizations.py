
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Develop tools for analyzing the performance of trading activity                            -- #
# -- script: visualizations.py : python script with data visualization functions                         -- #
# -- author: andreajimenezorozco, jofefloga                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/andreajimenezorozco/MyST_LAB3_1                                      -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import plotly.express as px
import plotly.graph_objects as go

def pie_chart(df2_ranking):

    labels = df2_ranking["symbol"].to_list()
    values = df2_ranking["rank (%)"].to_list()

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, pull=[0, 0, 0.2, 0])])
    fig.update_layout(
        title_text="Ranking de las Operaciones de Trading")

    return fig.show()

























