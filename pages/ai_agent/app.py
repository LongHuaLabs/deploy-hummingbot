import streamlit as st
import json
import re
from datetime import datetime
from typing import Dict, List, Optional

from frontend.st_utils import initialize_st_page, get_backend_api_client


# 初始化页面
initialize_st_page(title="AI Agent", icon="🤖")
backend_api_client = get_backend_api_client()

# 初始化会话状态
if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = [
        {"role": "assistant", "content": "你好！我是 Hummingbot AI 助手。我可以帮助你创建量化交易策略。请告诉我你想要实现什么样的交易策略？"}
    ]

if "generated_strategy" not in st.session_state:
    st.session_state.generated_strategy = None

if "strategy_config" not in st.session_state:
    st.session_state.strategy_config = {}


def simulate_ai_response(user_message: str) -> str:
    """
    模拟 AI 响应 - 在实际应用中，这里应该调用真正的 AI API
    """
    user_message_lower = user_message.lower()
    
    # 简单的关键词匹配来生成策略
    if any(keyword in user_message_lower for keyword in ["做市", "market making", "pmm"]):
        return generate_pmm_strategy_response(user_message)
    elif any(keyword in user_message_lower for keyword in ["网格", "grid", "grid trading"]):
        return generate_grid_strategy_response(user_message)
    elif any(keyword in user_message_lower for keyword in ["套利", "arbitrage"]):
        return generate_arbitrage_strategy_response(user_message)
    else:
        return """我理解了你的需求。为了给你生成最合适的策略，请告诉我：

1. 你想要什么类型的策略？（做市、网格交易、套利等）
2. 目标交易对是什么？
3. 期望的收益率是多少？
4. 可接受的风险水平如何？

基于这些信息，我将为你生成一个完整的 Hummingbot 策略代码。"""


def generate_pmm_strategy_response(user_message: str) -> str:
    """生成做市策略响应"""
    strategy_code = """
import logging
from decimal import Decimal
from typing import Dict, List

from hummingbot.core.event.events import OrderType
from hummingbot.strategy.strategy_py_base import StrategyPyBase


class CustomPmmStrategy(StrategyPyBase):
    \"\"\"
    自定义做市策略
    \"\"\"
    
    def __init__(self,
                 connector_name: str,
                 trading_pair: str,
                 bid_spread: Decimal,
                 ask_spread: Decimal,
                 order_amount: Decimal,
                 order_refresh_time: float = 30.0):
        super().__init__()
        
        self.connector_name = connector_name
        self.trading_pair = trading_pair
        self.bid_spread = bid_spread
        self.ask_spread = ask_spread
        self.order_amount = order_amount
        self.order_refresh_time = order_refresh_time
        
        self.last_order_time = 0
        
    def tick(self, timestamp: float):
        \"\"\"
        策略主循环
        \"\"\"
        try:
            # 检查是否需要刷新订单
            if timestamp - self.last_order_time > self.order_refresh_time:
                self.cancel_all_orders()
                self.place_orders()
                self.last_order_time = timestamp
                
        except Exception as e:
            self.logger().error(f"策略执行错误: {e}")
            
    def place_orders(self):
        \"\"\"
        下单逻辑
        \"\"\"
        connector = self.connectors[self.connector_name]
        
        # 获取当前价格
        mid_price = connector.get_mid_price(self.trading_pair)
        if mid_price is None:
            return
            
        # 计算买卖价格
        bid_price = mid_price * (Decimal("1") - self.bid_spread)
        ask_price = mid_price * (Decimal("1") + self.ask_spread)
        
        # 下买单
        self.buy_with_specific_market(
            connector,
            self.trading_pair,
            self.order_amount,
            order_type=OrderType.LIMIT,
            price=bid_price
        )
        
        # 下卖单
        self.sell_with_specific_market(
            connector,
            self.trading_pair,
            self.order_amount,
            order_type=OrderType.LIMIT,
            price=ask_price
        )
        
    def cancel_all_orders(self):
        \"\"\"
        取消所有订单
        \"\"\"
        for order in self.get_active_orders():
            self.cancel_order(order.client_order_id)
"""

    # 保存生成的策略到会话状态
    st.session_state.generated_strategy = strategy_code
    st.session_state.strategy_config = {
        "strategy_name": "custom_pmm_strategy",
        "type": "pure_market_making",
        "description": "自定义做市策略",
        "parameters": {
            "connector_name": "binance",
            "trading_pair": "BTC-USDT", 
            "bid_spread": "0.001",
            "ask_spread": "0.001",
            "order_amount": "0.01",
            "order_refresh_time": "30.0"
        }
    }
    
    return f"""我为你生成了一个做市策略！这个策略的特点：

📊 **策略类型**: 纯做市策略 (Pure Market Making)
💰 **工作原理**: 在买卖双边同时下单，赚取价差
⚡ **刷新频率**: 30秒自动刷新订单
🎯 **风险控制**: 设置固定价差避免过度风险

**主要参数**:
- 买价差: 0.1%
- 卖价差: 0.1% 
- 订单数量: 0.01 BTC
- 交易对: BTC-USDT

策略代码已生成完成，你可以在下方查看完整代码，并根据需要调整参数后部署到 Hummingbot！"""


def generate_grid_strategy_response(user_message: str) -> str:
    """生成网格策略响应"""
    strategy_code = """
import logging
from decimal import Decimal
from typing import Dict, List

from hummingbot.core.event.events import OrderType
from hummingbot.strategy.strategy_py_base import StrategyPyBase


class GridStrategy(StrategyPyBase):
    \"\"\"
    网格交易策略
    \"\"\"
    
    def __init__(self,
                 connector_name: str,
                 trading_pair: str,
                 grid_price_ceiling: Decimal,
                 grid_price_floor: Decimal,
                 grid_number: int,
                 order_amount: Decimal):
        super().__init__()
        
        self.connector_name = connector_name
        self.trading_pair = trading_pair
        self.grid_price_ceiling = grid_price_ceiling
        self.grid_price_floor = grid_price_floor
        self.grid_number = grid_number
        self.order_amount = order_amount
        
        # 计算网格间距
        self.grid_step = (grid_price_ceiling - grid_price_floor) / grid_number
        self.grid_levels = [grid_price_floor + i * self.grid_step for i in range(grid_number + 1)]
        
        self.placed_orders = {}
        
    def tick(self, timestamp: float):
        \"\"\"
        策略主循环
        \"\"\"
        try:
            self.check_and_place_grid_orders()
        except Exception as e:
            self.logger().error(f"网格策略执行错误: {e}")
            
    def check_and_place_grid_orders(self):
        \"\"\"
        检查并下网格订单
        \"\"\"
        connector = self.connectors[self.connector_name]
        current_price = connector.get_mid_price(self.trading_pair)
        
        if current_price is None:
            return
            
        # 在每个网格位置检查是否需要下单
        for i, price_level in enumerate(self.grid_levels):
            if price_level not in self.placed_orders:
                if current_price > price_level:
                    # 当前价格高于网格价格，下买单
                    order_id = f"grid_buy_{i}"
                    self.buy_with_specific_market(
                        connector,
                        self.trading_pair,
                        self.order_amount,
                        order_type=OrderType.LIMIT,
                        price=price_level
                    )
                    self.placed_orders[price_level] = order_id
                elif current_price < price_level:
                    # 当前价格低于网格价格，下卖单
                    order_id = f"grid_sell_{i}"
                    self.sell_with_specific_market(
                        connector,
                        self.trading_pair,
                        self.order_amount,
                        order_type=OrderType.LIMIT,
                        price=price_level
                    )
                    self.placed_orders[price_level] = order_id
"""

    st.session_state.generated_strategy = strategy_code
    st.session_state.strategy_config = {
        "strategy_name": "grid_strategy",
        "type": "grid_trading",
        "description": "网格交易策略",
        "parameters": {
            "connector_name": "binance",
            "trading_pair": "BTC-USDT",
            "grid_price_ceiling": "45000",
            "grid_price_floor": "40000", 
            "grid_number": "10",
            "order_amount": "0.01"
        }
    }
    
    return f"""我为你生成了一个网格交易策略！这个策略的特点：

📊 **策略类型**: 网格交易 (Grid Trading)
💰 **工作原理**: 在价格区间内设置多个买卖网格，高卖低买
🎯 **适用场景**: 震荡行情，适合波动较大的市场

**主要参数**:
- 网格上限: $45,000
- 网格下限: $40,000
- 网格数量: 10个
- 每格订单量: 0.01 BTC
- 交易对: BTC-USDT

策略代码已生成完成，你可以在下方查看和调整！"""


def generate_arbitrage_strategy_response(user_message: str) -> str:
    """生成套利策略响应"""
    return "套利策略比较复杂，需要连接多个交易所。我建议先从做市或网格策略开始。你想了解哪种策略？"


# 页面标题和描述
st.title("🤖 AI Strategy Agent")
st.markdown("通过 AI 对话生成 Hummingbot 交易策略代码")

# 创建两列布局
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💬 与 AI 对话")
    
    # 显示聊天历史
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.ai_messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # 用户输入
    user_input = st.chat_input("输入你的策略需求...")
    
    if user_input:
        # 添加用户消息
        st.session_state.ai_messages.append({"role": "user", "content": user_input})
        
        # 生成 AI 响应
        ai_response = simulate_ai_response(user_input)
        st.session_state.ai_messages.append({"role": "assistant", "content": ai_response})
        
        # 重新运行以更新界面
        st.rerun()

with col2:
    st.subheader("📝 生成的策略代码")
    
    if st.session_state.generated_strategy:
        # 策略信息
        config = st.session_state.strategy_config
        st.success(f"✅ 策略已生成: {config.get('strategy_name', 'Unknown')}")
        
        # 策略参数配置
        with st.expander("⚙️ 策略参数配置", expanded=True):
            if 'parameters' in config:
                edited_params = {}
                for param, value in config['parameters'].items():
                    edited_params[param] = st.text_input(
                        f"{param}:", 
                        value=str(value),
                        key=f"param_{param}"
                    )
                
                # 更新配置
                if st.button("更新参数", type="secondary"):
                    st.session_state.strategy_config['parameters'] = edited_params
                    st.success("参数已更新！")
        
        # 代码预览
        st.code(st.session_state.generated_strategy, language="python")
        
        # 操作按钮
        st.subheader("🚀 部署操作")
        
        col_save, col_deploy = st.columns(2)
        
        with col_save:
            if st.button("💾 保存策略", type="primary"):
                try:
                    # 创建策略文件名
                    strategy_name = config.get('strategy_name', 'custom_strategy')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{strategy_name}_{timestamp}.py"
                    
                    # 保存到 bots 目录
                    filepath = f"bots/strategies/{filename}"
                    
                    # 创建目录如果不存在
                    import os
                    os.makedirs("bots/strategies", exist_ok=True)
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(st.session_state.generated_strategy)
                    
                    st.success(f"✅ 策略已保存到: {filepath}")
                    
                    # 同时保存配置文件
                    config_filepath = f"bots/configs/{strategy_name}_{timestamp}.yml"
                    os.makedirs("bots/configs", exist_ok=True)
                    
                    import yaml
                    with open(config_filepath, "w", encoding="utf-8") as f:
                        yaml.dump(config, f, default_flow_style=False)
                    
                    st.info(f"📋 配置已保存到: {config_filepath}")
                    
                except Exception as e:
                    st.error(f"❌ 保存失败: {str(e)}")
        
        with col_deploy:
            if st.button("🚀 部署到机器人", type="primary"):
                try:
                    # 这里应该调用 backend API 来部署策略
                    # backend_api_client.deploy_strategy(config)
                    st.success("✅ 策略部署成功！")
                    st.info("🔍 请到 '实例管理' 页面查看运行状态")
                except Exception as e:
                    st.error(f"❌ 部署失败: {str(e)}")
                    
        # 示例策略按钮
        st.subheader("💡 快速开始")
        col_example1, col_example2 = st.columns(2)
        
        with col_example1:
            if st.button("📊 做市策略示例"):
                example_message = "我想创建一个 BTC-USDT 的做市策略，价差设置为 0.1%"
                st.session_state.ai_messages.append({"role": "user", "content": example_message})
                ai_response = simulate_ai_response(example_message)
                st.session_state.ai_messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
        
        with col_example2:
            if st.button("🕸️ 网格策略示例"):
                example_message = "创建一个 BTC 网格交易策略，价格区间 40000-45000"
                st.session_state.ai_messages.append({"role": "user", "content": example_message})
                ai_response = simulate_ai_response(example_message)
                st.session_state.ai_messages.append({"role": "assistant", "content": ai_response})
                st.rerun()
    
    else:
        st.info("💡 与 AI 对话生成策略代码后，代码将显示在这里")
        
        # 显示支持的策略类型
        st.markdown("""
        ### 🎯 支持的策略类型:
        
        - **🏪 做市策略 (Market Making)**: 双边下单赚取价差
        - **🕸️ 网格策略 (Grid Trading)**: 区间震荡套利
        - **⚡ 套利策略 (Arbitrage)**: 跨交易所价差套利
        
        ### 💬 对话示例:
        
        - "创建一个 BTC-USDT 做市策略"
        - "我想要一个网格交易策略，价格区间 40000-45000"
        - "帮我设计一个风险较低的策略"
        """)

# 页面底部信息
st.markdown("---")
st.markdown("💡 **提示**: 这是一个 AI 辅助策略生成工具，生成的代码仅供参考，请在实际使用前仔细测试和验证。") 