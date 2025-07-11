from st_pages import Page, Section


# def main_page():
#     return [Page("main.py", "Hummingbot Dashboard", "📊")]


# def public_pages():
#     return [
#         Section("Config Generator", "🎛️"),
#         Page("frontend/pages/config/grid_strike/app.py", "Grid Strike", "🎳"),
#         Page("frontend/pages/config/pmm_simple/app.py", "PMM Simple", "👨‍🏫"),
#         Page("frontend/pages/config/pmm_dynamic/app.py", "PMM Dynamic", "👩‍🏫"),
#         Page("frontend/pages/config/dman_maker_v2/app.py", "D-Man Maker V2", "🤖"),
#         Page("frontend/pages/config/bollinger_v1/app.py", "Bollinger V1", "📈"),
#         Page("frontend/pages/config/macd_bb_v1/app.py", "MACD_BB V1", "📊"),
#         Page("frontend/pages/config/supertrend_v1/app.py", "SuperTrend V1", "👨‍🔬"),
#         Page("frontend/pages/config/xemm_controller/app.py", "XEMM Controller", "⚡️"),
#         Section("Data", "💾"),
#         Page("frontend/pages/data/download_candles/app.py", "Download Candles", "💹"),
#         Section("Community Pages", "👨‍👩‍👧‍👦"),
#         Page("frontend/pages/data/token_spreads/app.py", "Token Spreads", "🧙"),
#         Page("frontend/pages/data/tvl_vs_mcap/app.py", "TVL vs Market Cap", "🦉"),
#         Page("frontend/pages/performance/bot_performance/app.py", "Strategy Performance", "📈"),
#     ]


# def private_pages():
#     return [
#         Section("Bot Orchestration", "🐙"),
#         Page("frontend/pages/orchestration/instances/app.py", "Instances", "🦅"),
#         Page("frontend/pages/orchestration/launch_bot_v2/app.py", "Deploy V2", "🚀"),
#         Page("frontend/pages/orchestration/credentials/app.py", "Credentials", "🔑"),
#         Page("frontend/pages/orchestration/portfolio/app.py", "Portfolio", "💰"),
#     ]

def main_page():
    return [Page("main.py", "CCSMEC Dashboard")]

def public_pages():
    return [
        Section("AI 投顾"),
        Page("frontend/pages/ai_agent/app.py", "AI Agent"),
        # Page("frontend/pages/ai_agent/app.py", "fundamentals analyst"),
        # Page("frontend/pages/ai_agent/app.py", "market analyst"),
        # Page("frontend/pages/ai_agent/app.py", "news analyst"),
        # Page("frontend/pages/ai_agent/app.py", "social media analyst"),
        # Page("frontend/pages/ai_agent/app.py", "technical analyst"),
        Section("策略配置"),
        Page("frontend/pages/config/grid_strike/app.py", "网格"),
        Page("frontend/pages/config/pmm_simple/app.py", "PMM 简易版"),
        Page("frontend/pages/config/pmm_dynamic/app.py", "PMM 动态版"),
        Page("frontend/pages/config/dman_maker_v2/app.py", "D-Man 做市商 V2"),
        Page("frontend/pages/config/bollinger_v1/app.py", "布林线 V1"),
        Page("frontend/pages/config/macd_bb_v1/app.py", "MACD_BB V1"),
        Page("frontend/pages/config/supertrend_v1/app.py", "SuperTrend V1"),
        Page("frontend/pages/config/xemm_controller/app.py", "XEMM 控制器"),
        Section("数据模块"),
        Page("frontend/pages/data/download_candles/app.py", "下载K线数据"),
        Section("社区页面"),
        Page("frontend/pages/data/token_spreads/app.py", "代币价差分析"),
        Page("frontend/pages/data/tvl_vs_mcap/app.py", "TVL 与市值对比"),
        Page("frontend/pages/performance/bot_performance/app.py", "策略表现"),
    ]


def private_pages():
    return [

        Section("机器人管理"),
        Page("frontend/pages/orchestration/instances/app.py", "实例管理"),
        Page("frontend/pages/orchestration/launch_bot_v2/app.py", "部署 V2"),
        Page("frontend/pages/orchestration/credentials/app.py", "凭证管理"),
        Page("frontend/pages/orchestration/portfolio/app.py", "投资组合"),
    ]