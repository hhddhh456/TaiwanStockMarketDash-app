# -*- coding: utf-8 -*-

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import pandas as pd
import sqlite3
import plotly.graph_objects as go

# 初始化 App，使用 DARKLY 主題作為基底，但會透過 CSS 覆蓋調整
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
    ]
)

# --- 設定變數 ---
period_options = [
    {"label": "1年", "value": "1Y_Ann_Return"},
    {"label": "3年", "value": "3Y_Ann_Return"},
    {"label": "5年", "value": "5Y_Ann_Return"},
    {"label": "15年", "value": "15Y_Ann_Return"},
    {"label": "20年", "value": "20Y_Ann_Return"},
]
period_labels = [p['label'] for p in period_options]
period_keys = [p['value'] for p in period_options]

# --- 專業風格配色系統 (Commercial Professional Palette) ---
COLORS = {
    "bg_main": "#1e2126",       # 極深灰背景 (比純黑更有質感)
    "bg_card": "#282c34",       # 卡片背景 (類似 VS Code 或現代儀表板)
    "text_main": "#e0e6ed",     # 主要文字 (柔和白)
    "text_sub": "#abb2bf",      # 次要文字 (淺灰)
    "accent_1": "#61afef",      # 專業藍 (Primary Ticker)
    "accent_2": "#e5c07b",      # 霧金色 (Secondary Ticker) - 更有金融感
    "success": "#98c379",       # 正向指標
    "danger": "#e06c75",        # 負向/警告
    "border": "#3b4048",        # 細微邊框
    "shadow": "0 4px 6px rgba(0, 0, 0, 0.3)" # 質感陰影，不發光
}

MAIN_STYLE = {
    "fontFamily": "'Roboto', 'Helvetica Neue', Arial, sans-serif",
    "backgroundColor": COLORS["bg_main"],
    "color": COLORS["text_main"],
    "minHeight": "100vh",
    "paddingBottom": "50px"
}

CARD_STYLE = {
    "backgroundColor": COLORS["bg_card"],
    "border": f"1px solid {COLORS['border']}",
    "borderRadius": "8px",
    "boxShadow": COLORS["shadow"],
    "padding": "20px"
}

HEADER_STYLE = {
    "backgroundColor": "transparent",
    "borderBottom": f"1px solid {COLORS['border']}",
    "paddingBottom": "15px",
    "marginBottom": "20px",
    "color": COLORS["text_main"],
    "fontSize": "1.4rem",
    "fontWeight": "500",
    "letterSpacing": "0.05em"
}

def get_years(ticker):
    try:
        conn = sqlite3.connect("newstock_data.db")
        df = pd.read_sql_query(f"SELECT DISTINCT Year FROM {ticker}", conn)
        conn.close()
        years = sorted(df['Year'].dropna().unique())
        return years
    except:
        return [2022] # Fallback for demo without DB

app.layout = html.Div(style=MAIN_STYLE, children=[
    dbc.Container([
        # --- 標題區 ---
        dbc.Row([
            dbc.Col(
                html.Div([
                    html.H1("Taiwan Stock Market Analytics", 
                            className="text-center",
                            style={"fontWeight": "300", "fontSize": "2.8rem", "color": COLORS["text_main"], "marginTop": "40px"}),
                    html.P("臺灣股市分析儀錶板", 
                           className="text-center",
                           style={"color": COLORS["text_sub"], "fontSize": "1.2rem", "letterSpacing": "2px", "marginBottom": "40px"})
                ]),
                width=12
            )
        ]),

        dbc.Row([
            # --- 左側控制面板 ---
            dbc.Col([
                html.Div(style=CARD_STYLE, children=[
                    html.Div("Configuration / 參數設定", style=HEADER_STYLE),
                    
                    html.Label("Benchmark / 商品一", style={"color": COLORS["accent_1"], "fontWeight":"bold", "fontSize": "0.9rem"}),
                    dcc.Dropdown(
                        id='ticker1-dropdown',
                        options=[
                            {'label': '台積電 (2330)', 'value': 'TSMC_2330_metrics'},
                            {'label': '元大台灣50 (0050)', 'value': 'ETF_0050_metrics'},
                            {'label': '加權指數 (TAIEX)', 'value': 'INDEX_TWII_metrics'},
                        ],
                        value='TSMC_2330_metrics',
                        clearable=False,
                        style={"color": "#333", "marginBottom": "20px"} # Dropdown 內部通常保持亮色以利閱讀
                    ),

                    html.Label("Comparison / 商品二", style={"color": COLORS["accent_2"], "fontWeight":"bold", "fontSize": "0.9rem"}),
                    dcc.Dropdown(
                        id='ticker2-dropdown',
                        options=[
                            {'label': '台積電 (2330)', 'value': 'TSMC_2330_metrics'},
                            {'label': '元大台灣50 (0050)', 'value': 'ETF_0050_metrics'},
                            {'label': '加權指數 (TAIEX)', 'value': 'INDEX_TWII_metrics'},
                        ],
                        value='ETF_0050_metrics',
                        clearable=False,
                        style={"color": "#333", "marginBottom": "30px"}
                    ),

                    html.Hr(style={"borderColor": COLORS["border"]}),
                    
                    # 數據摘要區塊 (Metrics)
                    html.Div(id='metrics-output'),

                    html.Hr(style={"borderColor": COLORS["border"], "marginTop": "20px"}),
                    
                    # 相關係數文字
                    html.Div(id='correlation-output')
                ])
            ], width=3), # 縮窄左側，讓圖表更寬

            # --- 右側圖表區 ---
            dbc.Col([
                # 上方：滑桿 + 年化報酬
                html.Div(style=CARD_STYLE, children=[
                    dbc.Row([
                        dbc.Col(html.Div("Annual Returns / 年化報酬率比較", style=HEADER_STYLE), width=8),
                        dbc.Col(html.Div(id="year-slider-label", style={"textAlign":"right", "color": COLORS["text_sub"], "paddingTop":"5px"}), width=4)
                    ]),
                    
                    html.Div([
                        dcc.Slider(
                            id='year-slider', min=0, max=100, step=1, value=2022,
                            marks={}, 
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="mb-4"
                        ),
                    ], style={"padding": "0 20px"}),

                    dcc.Graph(id='annual-returns-bar', config={'displayModeBar': False}, style={'height': '350px'})
                ], className="mb-4"),

                # 中間：散佈圖
                html.Div(style=CARD_STYLE, children=[
                    html.Div("Price Correlation / 月均價相關性分析", style=HEADER_STYLE),
                    dcc.Graph(id='correlation-plot', config={'displayModeBar': False}, style={'height': '320px'}),
                ], className="mb-4"),

                # 下方：兩張並排圖表
                dbc.Row([
                    dbc.Col(
                        html.Div(style=CARD_STYLE, children=[
                            html.Div("Historical Sharpe Ratio / 歷年夏普比率", style=HEADER_STYLE),
                            dcc.Graph(id='sharpe-line', config={'displayModeBar': False}, style={'height': '300px'})
                        ]), width=6
                    ),
                    dbc.Col(
                        html.Div(style=CARD_STYLE, children=[
                            html.Div("Max Drawdown / 歷年最大回撤", style=HEADER_STYLE),
                            dcc.Graph(id='maxdrawdown-line', config={'displayModeBar': False}, style={'height': '300px'})
                        ]), width=6
                    )
                ])

            ], width=9)
        ], align="start")
    ], fluid=True, style={"maxWidth": "1600px"}) # 限制最大寬度，避免在大螢幕過度拉伸
])

# --- Callbacks ---

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
        return 0, 100, {}, 2022, "No Data"
    
    # 簡化 Slider 標記，只顯示頭尾與重點，保持乾淨
    marks = {}
    maxyears = len(years)
    step = max(1, maxyears // 8) # 自動計算間隔，避免擁擠
    
    for i, y in enumerate(years):
        if i == 0 or i == maxyears - 1 or i % step == 0:
            marks[int(y)] = {"label": str(y), "style": {"color": COLORS["text_sub"]}}
            
    label = f"Selected Year: {years[-1]}" if years else "Select Year"
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
        return "請選擇不同商品", "", go.Figure(), go.Figure(), go.Figure(), go.Figure()
    
    # 模擬資料讀取 (若無 DB 則避免 crash)
    try:
        conn = sqlite3.connect("newstock_data.db")
        df1 = pd.read_sql_query(f"SELECT * FROM {ticker1}", conn)
        df2 = pd.read_sql_query(f"SELECT * FROM {ticker2}", conn)
        conn.close()
    except:
        # 這裡僅為了防呆，實際應顯示錯誤訊息
        return "DB Error", "", go.Figure(), go.Figure(), go.Figure(), go.Figure()

    df1_y = df1[df1['Year']==year]
    df2_y = df2[df2['Year']==year]
    
    if df1_y.empty or df2_y.empty:
        return f"無 {year} 年資料", "", go.Figure(), go.Figure(), go.Figure(), go.Figure()
        
    row1 = df1_y.iloc[-1]
    row2 = df2_y.iloc[-1]

    # --- 1. 數據摘要表格 (更現代化的排版) ---
    metrics_html = html.Div([
        html.Table([
            html.Thead(
                html.Tr([
                    html.Th("Metric", style={"color": COLORS["text_sub"], "fontWeight":"normal", "padding":"8px"}),
                    html.Th(ticker1.split('_')[0], style={"color": COLORS["accent_1"], "padding":"8px", "textAlign":"right"}),
                    html.Th(ticker2.split('_')[0], style={"color": COLORS["accent_2"], "padding":"8px", "textAlign":"right"})
                ])
            ),
            html.Tbody([
                html.Tr([
                    html.Td("Annual Return", style={"padding":"8px"}),
                    html.Td(f"{row1['year_return']*100:.1f}%", style={"textAlign":"right", "fontWeight":"bold"}),
                    html.Td(f"{row2['year_return']*100:.1f}%", style={"textAlign":"right", "fontWeight":"bold"})
                ], style={"borderTop": f"1px solid {COLORS['border']}"}),
                html.Tr([
                    html.Td("Sharpe Ratio", style={"padding":"8px"}),
                    html.Td(f"{row1['sharpe']:.2f}", style={"textAlign":"right"}),
                    html.Td(f"{row2['sharpe']:.2f}", style={"textAlign":"right"})
                ], style={"borderTop": f"1px solid {COLORS['border']}"}),
                html.Tr([
                    html.Td("Max Drawdown", style={"padding":"8px"}),
                    html.Td(f"{row1['max_drawdown']*100:.1f}%", style={"textAlign":"right", "color": COLORS["danger"]}),
                    html.Td(f"{row2['max_drawdown']*100:.1f}%", style={"textAlign":"right", "color": COLORS["danger"]})
                ], style={"borderTop": f"1px solid {COLORS['border']}"}),
            ])
        ], style={"width":"100%", "fontSize":"0.95rem", "color": COLORS["text_main"]})
    ])

    # --- 通用圖表設定 (減少重複代碼) ---
    common_layout = dict(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)', # 透明背景，沿用卡片色
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Roboto, Arial', color=COLORS["text_sub"]),
        margin=dict(t=30, l=40, r=20, b=40),
        xaxis=dict(showgrid=False, zeroline=False), # 簡潔的 X 軸
        yaxis=dict(showgrid=True, gridcolor=COLORS["border"], zeroline=False), # 淡淡的格線
    )

    # --- 2. Bar Chart ---
    vals1 = [row1[period]*100 if pd.notna(row1[period]) else 0 for period in period_keys]
    vals2 = [row2[period]*100 if pd.notna(row2[period]) else 0 for period in period_keys]
    
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(name=ticker1.split('_')[0], x=period_labels, y=vals1, marker_color=COLORS["accent_1"]))
    bar_fig.add_trace(go.Bar(name=ticker2.split('_')[0], x=period_labels, y=vals2, marker_color=COLORS["accent_2"]))
    bar_fig.update_layout(**common_layout)
    bar_fig.update_layout(barmode='group', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    # --- 3. Correlation Plot ---
    merged_df = pd.merge(
        df1[['Year', 'Month', 'month_avg_price']].dropna(),
        df2[['Year', 'Month', 'month_avg_price']].dropna(),
        on=['Year', 'Month'], suffixes=('_1', '_2'))
    
    corr_text = html.Div([
        html.Span("Correlation Coeff: ", style={"color": COLORS["text_sub"]}),
        html.Span("N/A", style={"fontWeight":"bold"})
    ])
    
    corr_fig = go.Figure()
    if len(merged_df) > 1:
        corr_val = merged_df['month_avg_price_1'].corr(merged_df['month_avg_price_2'])
        corr_text = html.Div([
             html.H6("Statistical Correlation", style={"color": COLORS["text_sub"], "fontSize": "0.85rem"}),
             html.H3(f"{corr_val:.4f}", style={"color": COLORS["success"] if corr_val > 0.7 else COLORS["text_main"], "margin": 0})
        ])
        
        corr_fig.add_trace(go.Scatter(
            x=merged_df['month_avg_price_1'], 
            y=merged_df['month_avg_price_2'],
            mode='markers', 
            marker=dict(color=COLORS["accent_1"], size=8, opacity=0.7, line=dict(width=1, color="white"))
        ))
        corr_fig.update_layout(**common_layout)
        corr_fig.update_xaxes(title_text=f"{ticker1} Price")
        corr_fig.update_yaxes(title_text=f"{ticker2} Price")

    # --- 4. Sharpe Line ---
    sharpes_fig = go.Figure()
    sharpes_fig.add_trace(go.Scatter(x=df1['Year'], y=df1['sharpe'], mode='lines', name=ticker1.split('_')[0], line=dict(width=2.5, color=COLORS["accent_1"])))
    sharpes_fig.add_trace(go.Scatter(x=df2['Year'], y=df2['sharpe'], mode='lines', name=ticker2.split('_')[0], line=dict(width=2.5, color=COLORS["accent_2"])))
    sharpes_fig.update_layout(**common_layout)
    sharpes_fig.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    # --- 5. Max Drawdown Line ---
    maxdraw_fig = go.Figure()
    maxdraw_fig.add_trace(go.Scatter(x=df1['Year'], y=df1['max_drawdown']*100, mode='lines', fill='tozeroy', name=ticker1.split('_')[0], line=dict(width=2, color=COLORS["accent_1"])))
    maxdraw_fig.add_trace(go.Scatter(x=df2['Year'], y=df2['max_drawdown']*100, mode='lines', fill='tozeroy', name=ticker2.split('_')[0], line=dict(width=2, color=COLORS["accent_2"])))
    maxdraw_fig.update_layout(**common_layout)
    maxdraw_fig.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    return corr_text, metrics_html, corr_fig, bar_fig, sharpes_fig, maxdraw_fig

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
