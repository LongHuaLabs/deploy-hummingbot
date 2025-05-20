from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
from hummingbot.core.data_type.common import PriceType, TradeType
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
from hummingbot.core.data_type.candles import CandlesFactory, CandlesConfig

class MultiAssetRSIStrategy(ScriptStrategyBase):
    # 策略参数配置
    trading_pairs = ["BTC-USDT", "ETH-USDT"]
    exchange = "binance"
    
    # RSI参数
    rsi_length = 14
    eth_btc_rsi_length = 14
    bullish_rsi_entry = 70
    bullish_rsi_exit = 65
    bearish_rsi_entry = 30
    bearish_rsi_exit = 35
    sma_length = 200
    
    # 头寸管理
    allocation = 0.98
    rebalance_threshold = 0.1  # 10%变化触发调仓
    max_position_ratio = 0.25  # 单资产最大仓位比例
    
    # 风险管理
    stop_loss_pct = 0.20
    trailing_stop_activation = 0.05  # 5%盈利后启动追踪止损
    trailing_delta = 0.03  # 3%追踪幅度
    
    # 初始化变量
    candles_config = {}
    last_execution_time = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化各交易对的K线配置
        for pair in self.trading_pairs:
            self.candles_config[pair] = CandlesConfig(
                connector=self.exchange,
                trading_pair=pair,
                interval="1d",
                max_records=300
            )
        # 注册K线数据源
        self.candles = {pair: CandlesFactory.get_candle(self.candles_config[pair])
                        for pair in self.trading_pairs}
        
    def on_tick(self):
        # 每5分钟执行一次逻辑
        if not self._should_execute():
            return
        
        # 更新K线数据
        for candle in self.candles.values():
            candle.update()
            
        # 获取当前投资组合价值
        total_value = self.get_total_portfolio_value()
        target_value = total_value * self.allocation
        
        # 计算市场状态
        market_regime = self.determine_market_regime()
        
        # 生成交易信号
        signals = {}
        for pair in self.trading_pairs:
            signals[pair] = self.generate_signal(pair, market_regime)
            
        # 头寸再平衡
        self.rebalance_positions(signals, target_value)
        
    def _should_execute(self):
        # 每日执行一次策略逻辑
        now = datetime.now()
        if not self.last_execution_time or (now - self.last_execution_time) >= timedelta(days=1):
            self.last_execution_time = now
            return True
        return False
    
    def get_total_portfolio_value(self):
        # 计算总组合价值（包括所有资产和现金）
        total = self.connectors[self.exchange].get_available_balance("USDT")
        for pair in self.trading_pairs:
            base = pair.split("-")[0]
            position = self.connectors[self.exchange].get_balance(base)
            price = self.connectors[self.exchange].get_price(pair, PriceType.MidPrice)
            total += position * price
        return total
    
    def determine_market_regime(self):
        # 使用BTC的200日SMA判断市场状态
        btc_candles = self.candles["BTC-USDT"].candles_df
        if len(btc_candles) < self.sma_length:
            return "neutral"
        
        sma = ta.sma(btc_candles["close"], length=self.sma_length).iloc[-1]
        current_price = self.connectors[self.exchange].get_price("BTC-USDT", PriceType.MidPrice)
        
        if current_price > sma * 1.05:
            return "bull"
        elif current_price < sma * 0.95:
            return "bear"
        else:
            return "neutral"
    
    def generate_signal(self, pair, regime):
        candles_df = self.candles[pair].candles_df
        if len(candles_df) < self.rsi_length:
            return "hold"
            
        # 计算RSI
        rsi = ta.rsi(candles_df["close"], length=self.rsi_length).iloc[-1]
        
        # 计算ETH/BTC相对强弱
        if "ETH" in pair:
            eth_price = candles_df["close"].iloc[-1]
            btc_price = self.candles["BTC-USDT"].candles_df["close"].iloc[-1]
            eth_btc_ratio = eth_price / btc_price
            eth_btc_rsi = ta.rsi(pd.Series([eth_btc_ratio]), length=self.eth_btc_rsi_length).iloc[-1]
        else:
            eth_btc_rsi = 50
            
        # 生成信号逻辑
        position = self.connectors[self.exchange].get_position(pair)
        
        if regime == "bull":
            entry_level = self.bullish_rsi_entry
            exit_level = self.bullish_rsi_exit
        elif regime == "bear":
            entry_level = self.bearish_rsi_entry
            exit_level = self.bearish_rsi_exit
        else:
            entry_level = (self.bullish_rsi_entry + self.bearish_rsi_entry) / 2
            exit_level = (self.bullish_rsi_exit + self.bearish_rsi_exit) / 2
            
        # 考虑ETH/BTC相对强弱
        if "ETH" in pair and eth_btc_rsi > 70:
            entry_level -= 5
        elif "ETH" in pair and eth_btc_rsi < 30:
            entry_level += 5
            
        if position == 0:
            if rsi <= entry_level:
                return "buy"
        else:
            if rsi >= exit_level:
                return "sell"
                
        return "hold"
    
    def rebalance_positions(self, signals, target_value):
        # 计算当前头寸权重
        current_weights = {}
        total = self.get_total_portfolio_value()
        for pair in self.trading_pairs:
            base = pair.split("-")[0]
            position = self.connectors[self.exchange].get_balance(base)
            price = self.connectors[self.exchange].get_price(pair, PriceType.MidPrice)
            current_weights[pair] = (position * price) / total
            
        # 计算目标权重
        target_weights = self.calculate_target_weights(signals)
        
        # 执行再平衡
        for pair in self.trading_pairs:
            current_weight = current_weights.get(pair, 0)
            target_weight = target_weights.get(pair, 0)
            
            if abs(current_weight - target_weight) > self.rebalance_threshold:
                self.adjust_position(pair, target_weight, target_value)
                
    def calculate_target_weights(self, signals):
        # 基于信号和动量计算目标权重
        weights = {}
        total_score = 0
        momentum_scores = {}
        
        for pair in self.trading_pairs:
            candles_df = self.candles[pair].candles_df
            if len(candles_df) < 3:
                momentum = 0
            else:
                returns = candles_df["close"].pct_change(3).iloc[-1]
                momentum = pow(abs(returns), 3.5)  # 原策略的动量指数
                
            if signals[pair] == "buy":
                momentum_scores[pair] = momentum
            else:
                momentum_scores[pair] = 0
            total_score += momentum_scores[pair]
            
        if total_score > 0:
            for pair in self.trading_pairs:
                weights[pair] = min(momentum_scores[pair] / total_score, self.max_position_ratio)
        else:
            for pair in self.trading_pairs:
                weights[pair] = 0
                
        return weights
    
    def adjust_position(self, pair, target_weight, target_value):
        # 计算目标头寸
        current_price = self.connectors[self.exchange].get_price(pair, PriceType.MidPrice)
        target_notional = target_value * target_weight
        current_position = self.connectors[self.exchange].get_balance(pair.split("-")[0])
        current_notional = current_position * current_price
        
        # 计算调整量
        delta = target_notional - current_notional
        if abs(delta) < 10:  # 最小交易量过滤
            return
            
        if delta > 0:
            trade_type = TradeType.BUY
        else:
            trade_type = TradeType.SELL
            
        amount = abs(delta) / current_price
        
        # 执行订单
        self.execute_order(pair, amount, trade_type)
        
    def execute_order(self, pair, amount, trade_type):
        # 使用市价单执行
        connector = self.connectors[self.exchange]
        if trade_type == TradeType.BUY:
            connector.buy(pair, amount, order_type=OrderType.MARKET)
        else:
            connector.sell(pair, amount, order_type=OrderType.MARKET)
            
    def apply_risk_management(self):
        # 实施止损逻辑
        for pair in self.trading_pairs:
            position = self.connectors[self.exchange].get_position(pair)
            if position != 0:
                entry_price = self.get_average_entry_price(pair)
                current_price = self.connectors[self.exchange].get_price(pair, PriceType.MidPrice)
                
                # 硬止损
                if current_price <= entry_price * (1 - self.stop_loss_pct):
                    self.close_position(pair)
                    
                # 追踪止损
                if current_price >= entry_price * (1 + self.trailing_stop_activation):
                    trailing_stop_price = current_price * (1 - self.trailing_delta)
                    if current_price <= trailing_stop_price:
                        self.close_position(pair)
    
    def close_position(self, pair):
        base = pair.split("-")[0]
        position = self.connectors[self.exchange].get_balance(base)
        if position > 0:
            self.execute_order(pair, position, TradeType.SELL)
        elif position < 0:
            self.execute_order(pair, abs(position), TradeType.BUY)
            
    def format_status(self) -> str:
        status = []
        status.append("Strategy Status:")
        status.append(f"Total Portfolio Value: {self.get_total_portfolio_value():.2f} USDT")
        
        for pair in self.trading_pairs:
            price = self.connectors[self.exchange].get_price(pair, PriceType.MidPrice)
            position = self.connectors[self.exchange].get_balance(pair.split("-")[0])
            status.append(f"{pair}:")
            status.append(f"  Price: {price:.2f}")
            status.append(f"  Position: {position:.4f}")
            status.append(f"  RSI: {self.get_current_rsi(pair):.2f}")
            
        return "\n".join(status)
    
    def get_current_rsi(self, pair):
        candles_df = self.candles[pair].candles_df
        if len(candles_df) >= self.rsi_length:
            return ta.rsi(candles_df["close"], length=self.rsi_length).iloc[-1]
        return 50
