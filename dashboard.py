import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd
import sqlite3
import plotly.graph_objects as go

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css?family=Roboto+Mono:400,700&display=swap",
        "https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap"
    ]
)

period_options = [
    {"label": "1年", "value": "1Y_Ann_Return"},
    {"label": "3年", "value": "3Y_Ann_Return"},
    {"label": "5年", "value": "5Y_Ann_Return"},
    {"label": "15年", "value": "15Y_Ann_Return"},
    {"label": "20年", "value": "20Y_Ann_Return"},
]
period_labels = [p['label'] for p in period_options]
period_keys = [p['value'] for p in period_options]

TECH_STYLE = {
    "fontFamily": "'Roboto Mono', 'Roboto', 'Consolas', 'Arial', sans-serif",
    "backgroundColor": "#181A20",
    "color": "#e0e4e8",
    "letterSpacing": "0.05em",
    "fontSize": "19px",
}

def get_years(ticker):
    conn = sqlite3.connect("C:/Users/a0102/OneDrive/桌面/所有程式/STOCKDATA/newstock_data/newstock_data.db")
    df = pd.read_sql_query(f"SELECT DISTINCT Year FROM {ticker}", conn)
    conn.close()
    years = sorted(df['Year'].dropna().unique())
    return years

app.layout = html.Div(style=TECH_STYLE, children=[
    html.Link(href="https://fonts.googleapis.com/css?family=Roboto+Mono:400,700&display=swap", rel="stylesheet"),
    html.Link(href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap", rel="stylesheet"),
    dbc.Container([
        dbc.Row([
            dbc.Col(
                html.H1("臺灣股市儀錶板 DashBoard",
                    className="my-4 text-center fw-bold",
                    style={"color": "#00d2ea", "textShadow": "0 0 12px #00eaff, 0 0 1px #222", "fontSize": "2.6rem"}
                ),
                width=14
            )
        ], justify="center", style={"marginBottom": "33px"}),

        dbc.Row([
            # 左側選單
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H4("選擇商品與期間", className="text-center",
                                style={"color": "#21f9be", "fontWeight":700, "background":"#1c1f25", "fontSize": "31px", "padding":"17px 0"})
                    ),
                    dbc.CardBody([
                        html.Div([
                            html.Label("商品一", style={"color":"#c7d0de", "fontSize":"29px", "marginBottom":"3px"}),
                            dcc.Dropdown(
                                id='ticker1-dropdown',
                                options=[
                                    {'label': '台積電', 'value': 'TSMC_2330_metrics'},
                                    {'label': '元大台灣50', 'value': 'ETF_0050_metrics'},
                                    {'label': '加權指數', 'value': 'INDEX_TWII_metrics'},
                                ],
                                value='TSMC_2330_metrics',
                                style={"background": "#fff", "color": "#111", "border": "1px solid #ccc",
                                       "fontWeight": "bold", "fontSize":"26px", "height": "2rem"}
                            ),
                            html.Br(),
                            html.Label("商品二", style={"color":"#c7d0de", "fontSize":"29px", "marginBottom":"3px"}),
                            dcc.Dropdown(
                                id='ticker2-dropdown',
                                options=[
                                    {'label': '台積電', 'value': 'TSMC_2330_metrics'},
                                    {'label': '元大台灣50', 'value': 'ETF_0050_metrics'},
                                    {'label': '加權指數', 'value': 'INDEX_TWII_metrics'},
                                ],
                                value='ETF_0050_metrics',
                                style={"background": "#fff", "color": "#111", "border": "1px solid #ccc",
                                       "fontWeight": "bold", "fontSize":"26px", "height": "2rem"}
                            ),
                        ], style={"marginBottom": "12px"}),
                        html.Hr(style={"borderTop":"1.5px solid #444", "marginTop":"20px","marginBottom":"25px"}),
                        html.Div(id='metrics-output', style={"marginBottom":"20px"}),
                        html.Hr(style={"borderTop":"1.5px solid #444", "marginTop":"24px","marginBottom":"29px"}),
                        html.Div(id='correlation-output', style={"marginBottom":"30px"})
                    ])
                ], className="mb-5 shadow", style={"background":"#232630","border": "none",
                                                    "minHeight":"800px", "paddingBottom": "20px"})
            ], width=4),

            # 右側
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("年化報酬率", className="text-center",
                                           style={"color":"#fff", "fontWeight":700, "background":"#232630", "fontSize":"31px"})),
                    html.Div([
                        html.Div(
                            id="year-slider-label",
                            style={"textAlign":"center", "fontWeight":"bold", "fontSize":"27px", "marginBottom":"10px",
                                   "color":"#00eaff", "letterSpacing":"0.02em"}
                        ),
                        dcc.Slider(
                            id='year-slider', min=0, max=100, step=1, value=2022,
                            marks={}, tooltip={"placement": "bottom", "always_visible": True},
                            updatemode="drag",
                            included=False,
                            vertical=False,
                            className="custom-year-slider",
                        ),
                    ], style={"width":"94%","margin":"15px auto 17px auto"}),
                    dbc.CardBody([
                        dcc.Graph(id='annual-returns-bar', config={'displayModeBar': False},
                                  style={'height': '400px', 'backgroundColor':'#24273c'})
                    ])
                ], className="mb-5 shadow", style={"background":"#232630","border": "none","minHeight":"540px"}),
                dbc.Card([
                    dbc.CardHeader(html.H5("月均價相關性", className="text-center",
                                           style={"color":"#fff", "fontWeight":700, "background":"#232630", "fontSize":"31px"})),
                    dbc.CardBody([
                        dcc.Graph(id='correlation-plot', config={'displayModeBar': False},
                                  style={'height': '320px', 'backgroundColor':'#24273c'}),
                    ])
                ], className="mb-4 shadow", style={"background":"#232630","border": "none", "minHeight":"390px"}),
                dbc.Row([
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader("歷年夏普比率", className="text-center",
                                style={"color": "#81f7e6","background":"#232630", "fontSize":"30px", "fontWeight":700}),
                            dbc.CardBody(
                                dcc.Graph(id='sharpe-line', config={'displayModeBar': False},
                                          style={'height': '320px', 'backgroundColor':'#24273c'})
                            )
                        ], className="mb-4 shadow", style={"background":"#232630","border": "none", "minHeight":"355px"}),
                        width=6
                    ),
                    dbc.Col(
                        dbc.Card([
                            dbc.CardHeader("歷年最大回撤", className="text-center",
                                style={"color": "#e441db","background":"#232630", "fontSize":"30px", "fontWeight":700}),
                            dbc.CardBody(
                                dcc.Graph(id='maxdrawdown-line', config={'displayModeBar': False},
                                          style={'height': '320px', 'backgroundColor':'#24273c'})
                            )
                        ], className="mb-4 shadow", style={"background":"#232630","border": "none", "minHeight":"365px"}),
                        width=6
                    )
                ])
            ], width=8)
        ], align="stretch", style={"marginBottom":"32px"})
    ], fluid=True)
])

@app.callback(
    [Output('year-slider', 'min'),
     Output('year-slider', 'max'),
     Output('year-slider', 'marks'),
     Output('year-slider', 'value'),
     Output('year-slider-label', 'children')],
    Input('ticker1-dropdown', 'value')
)
def update_slider_years(ticker1):
    years = get_years(ticker1)
    if not years:
        return 0, 100, {}, 2022, "年份"
    # 年分字體放到最大
    marks = {}
    maxyears = len(years)
    for i, y in enumerate(years):
        if (maxyears <= 10) or (i == 0 or i == len(years) - 1) or (maxyears >= 12 and i % 3 == 1):
            marks[int(y)] = {"label": str(y),
                             "style": {"color": "#00eaff", "fontWeight":"bold", "fontSize": "27px"}}
    label = f"指標年度：{years[-1]}" if years else "年份"
    return int(min(years)), int(max(years)), marks, int(maxyears and years[-1]), label

@app.callback(
    [Output('correlation-output', 'children'),
     Output('metrics-output', 'children'),
     Output('correlation-plot', 'figure'),
     Output('annual-returns-bar', 'figure'),
     Output('sharpe-line', 'figure'),
     Output('maxdrawdown-line', 'figure')],
    [Input('ticker1-dropdown', 'value'),
     Input('ticker2-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_dashboard(ticker1, ticker2, year):
    if not ticker1 or not ticker2 or ticker1 == ticker2 or (year is None):
        return "請選擇商品和年度", "", go.Figure(), go.Figure(), go.Figure(), go.Figure()
    try:
        conn = sqlite3.connect("C:/Users/a0102/OneDrive/桌面/所有程式/STOCKDATA/newstock_data/newstock_data.db")
        df1 = pd.read_sql_query(f"SELECT * FROM {ticker1}", conn)
        df2 = pd.read_sql_query(f"SELECT * FROM {ticker2}", conn)
        conn.close()
    except Exception as e:
        return f"讀取資料失敗: {str(e)}", "", go.Figure(), go.Figure(), go.Figure(), go.Figure()

    df1_y = df1[df1['Year']==year]
    df2_y = df2[df2['Year']==year]
    if df1_y.empty or df2_y.empty:
        return f"該年度({year})無資料", "", go.Figure(), go.Figure(), go.Figure(), go.Figure()
    row1 = df1_y.iloc[-1]
    row2 = df2_y.iloc[-1]

    metrics_html = dbc.Card([
        dbc.CardHeader(html.H5(f"📊 年度指標比較 ({year})", className="text-center",
                               style={"color":"#21f9be", "fontSize":"1.4rem"})),
        dbc.CardBody(html.Table([
            html.Tr([html.Th("指標", style={"color":"#00eaff", "fontSize":"1.3rem","paddingBottom":"12px"}), html.Th(ticker1, style={"fontSize":"1.1rem","paddingBottom":"12px"}), html.Th(ticker2, style={"fontSize":"1.1rem","paddingBottom":"12px"})]),
            html.Tr([html.Td("年度報酬率", style={"color":"#f6f7f9","fontSize":"1.3rem","paddingTop":"9px", "paddingBottom":"9px"}),
                     html.Td(f"{row1['year_return']*100:.2f}%" if pd.notna(row1['year_return']) else "N/A", style={"fontSize":"1.2rem"}),
                     html.Td(f"{row2['year_return']*100:.2f}%" if pd.notna(row2['year_return']) else "N/A", style={"fontSize":"1.2rem"})]),
            html.Tr([html.Td("夏普比率", style={"color":"#7dffc8", "fontSize":"1.3rem","paddingTop":"9px", "paddingBottom":"9px"}),
                     html.Td(f"{row1['sharpe']:.3f}" if pd.notna(row1['sharpe']) else "N/A", style={"fontSize":"1.2rem"}),
                     html.Td(f"{row2['sharpe']:.3f}" if pd.notna(row2['sharpe']) else "N/A", style={"fontSize":"1.2rem"})]),
            html.Tr([html.Td("最大回撤", style={"color":"#f441c4", "fontSize":"1.3rem","paddingTop":"9px", "paddingBottom":"9px"}),
                     html.Td(f"{row1['max_drawdown']*100:.2f}%" if pd.notna(row1['max_drawdown']) else "N/A", style={"fontSize":"1.2rem"}),
                     html.Td(f"{row2['max_drawdown']*100:.2f}%" if pd.notna(row2['max_drawdown']) else "N/A", style={"fontSize":"1.2rem"})]),
        ], className="table table-striped table-dark table-sm",  style={"fontSize":"1.3rem", "textAlign":"center"}))
    ], className="shadow-sm mb-2", style={"background":"#24273c","border":"none", "marginBottom":"25px"})

    vals1 = [row1[period]*100 if pd.notna(row1[period]) else None for period in period_keys]
    vals2 = [row2[period]*100 if pd.notna(row2[period]) else None for period in period_keys]
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(name=ticker1, x=period_labels, y=vals1, marker_color='#00eaff'))
    bar_fig.add_trace(go.Bar(name=ticker2, x=period_labels, y=vals2, marker_color='#fa00ff'))
    bar_fig.update_layout(
        template='plotly_dark',
        title=f"{year}年 年化報酬率比較",
        font=dict(family='Roboto Mono,Roboto,Arial,sans-serif', color='#e0e4e8', size=21),
        yaxis_title='年化報酬率(%)',
        barmode='group',
        height=400,
        margin=dict(t=60, l=32, r=32, b=50)
    )

    merged_df = pd.merge(
        df1[['Year', 'Month', 'month_avg_price']].dropna(),
        df2[['Year', 'Month', 'month_avg_price']].dropna(),
        on=['Year', 'Month'], suffixes=('_1', '_2'))
    if merged_df.shape[0] < 2:
        corr_text = '【無法計算相關係數：沒有足夠的資料點】'
        corr_fig = go.Figure()
        corr_fig.update_layout(
            title='相關散佈圖 (無資料)',
            xaxis=dict(title=ticker1, visible=True, font=dict(size=17)),
            yaxis=dict(title=ticker2, visible=True, font=dict(size=17)),
            template='plotly_dark',
            margin=dict(l=28, r=28, t=51, b=36),
            height=320
        )
    else:
        corr_val = merged_df['month_avg_price_1'].corr(merged_df['month_avg_price_2'])
        corr_text = f"月均價相關係數: {corr_val:.4f}"
        corr_fig = go.Figure()
        corr_fig.add_trace(go.Scatter(x=merged_df['month_avg_price_1'], y=merged_df['month_avg_price_2'],
                                      mode='markers', marker=dict(color='#00eaff', size=8)))
        corr_fig.update_layout(
            template='plotly_dark',
            title=f"{ticker1} vs {ticker2} 月均價相關性散佈圖",
            xaxis_title=f"{ticker1} 月均價",
            yaxis_title=f"{ticker2} 月均價",
            font=dict(family='Roboto Mono,Roboto,Arial,sans-serif', color='#e0e4e8', size=20),
            margin=dict(l=28, r=28, t=51, b=36),
            height=320
        )

    sharpes_fig = go.Figure()
    sharpes_fig.add_trace(go.Scatter(x=df1['Year'], y=df1['sharpe'],
        mode='lines+markers', name=ticker1, line=dict(width=3, color='#21f9be')))
    sharpes_fig.add_trace(go.Scatter(x=df2['Year'], y=df2['sharpe'],
        mode='lines+markers', name=ticker2, line=dict(width=3, color='#e441db')))
    sharpes_fig.update_layout(
        template='plotly_dark',
        title='歷年夏普比率比較',
        xaxis_title='年度',
        yaxis_title='Sharpe Ratio',
        font=dict(family='Roboto Mono,Roboto,Arial,sans-serif', color='#e0e4e8', size=18),
        margin=dict(l=18, r=18, t=40, b=28),
        height=300
    )

    maxdraw_fig = go.Figure()
    maxdraw_fig.add_trace(go.Scatter(
        x=df1['Year'], y=(df1['max_drawdown'] * 100),
        mode='lines+markers', name=ticker1, line=dict(width=3, color='#21f9be')))
    maxdraw_fig.add_trace(go.Scatter(
        x=df2['Year'], y=(df2['max_drawdown'] * 100),
        mode='lines+markers', name=ticker2, line=dict(width=3, color='#e441db')))
    maxdraw_fig.update_layout(
        template='plotly_dark',
        title='歷年最大回撤 (%)',
        xaxis_title='年度',
        yaxis_title='最大回撤 (%)',
        font=dict(family='Roboto Mono,Roboto,Arial,sans-serif', color='#e0e4e8', size=18),
        margin=dict(l=18, r=18, t=40, b=28),
        height=300
    )

    corr_info = dbc.Card([
        dbc.CardHeader(html.H5("相關係數分析", className="text-center",
                               style={"color":"#00eaff", "fontSize":"31px", "fontWeight":700})),
        dbc.CardBody([
            html.H5(corr_text, style={"color":"#00d2ea","fontWeight":700, "fontSize":"1.3rem"})
        ])
    ], className="mb-3 shadow-sm", style={"background":"#232630","border":"none",
                                            "marginBottom":"30px"})

    return corr_info, metrics_html, corr_fig, bar_fig, sharpes_fig, maxdraw_fig

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)

