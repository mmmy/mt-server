"""
MT4 Connector implementation using third-party library.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from functools import wraps
import logging

from .base_connector import BaseConnector
from utils.exceptions import MT4Error, ConnectionError
from utils.logger import log_error_with_context


def auto_reconnect_mt4(func):
    """
    Decorator to automatically reconnect to MT4 if connection is lost.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            # Check connection before attempting operation
            if not self.is_connected():
                self.logger.warning(f"MT4 not connected before {func.__name__}, attempting to reconnect...")
                if not self.connect():
                    raise ConnectionError(f"MT4 connection failed before {func.__name__}")

            # First attempt
            return func(self, *args, **kwargs)
        except Exception as e:
            # Check if it's a connection-related error
            error_str = str(e).lower()
            if (not self.is_connected() or
                "not connected" in error_str or
                "connection" in error_str or
                isinstance(e, ConnectionError)):

                self.logger.warning(f"MT4 connection lost during {func.__name__}, attempting to reconnect...")

                # Attempt to reconnect
                if self.connect():
                    self.logger.info(f"MT4 reconnection successful, retrying {func.__name__}")
                    # Retry the operation after successful reconnection
                    return func(self, *args, **kwargs)
                else:
                    self.logger.error(f"MT4 reconnection failed for {func.__name__}")
                    raise ConnectionError(f"MT4 reconnection failed during {func.__name__}: {e}")
            else:
                # Not a connection error, re-raise original exception
                raise
    return wrapper


class MT4Connector(BaseConnector):
    """MT4连接器实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化MT4连接器
        
        Args:
            config: MT4配置字典
        """
        super().__init__(config)
        self.mt4_lib = None
        self._initialize_mt4_library()
    
    def _initialize_mt4_library(self):
        """初始化MT4库"""
        try:
            # 尝试导入MT4库
            import MetaTrader4 as mt4
            self.mt4_lib = mt4
            self.logger.info("MT4 library loaded successfully")
        except ImportError:
            self.logger.error("MetaTrader4 library not found. Please install it with: pip install MetaTrader4")
            raise MT4Error("MetaTrader4 library not available")
        except Exception as e:
            self.logger.error(f"Failed to initialize MT4 library: {e}")
            raise MT4Error(f"MT4 library initialization failed: {e}")
    
    def connect(self) -> bool:
        """
        Connect to MT4 terminal.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.mt4_lib:
                raise MT4Error("MT4 library not initialized")
            
            # Initialize MT4 connection
            terminal_path = self.config.get('terminal_path', '')
            bridge_port = self.config.get('bridge_port', 7788)
            
            self.logger.info(f"Connecting to MT4 with bridge port: {bridge_port}")
            
            # 使用MT4库连接（这里需要根据实际的MT4库API调整）
            if terminal_path:
                if not self.mt4_lib.initialize(path=terminal_path, port=bridge_port):
                    raise MT4Error(f"Failed to initialize MT4 with path: {terminal_path}")
            else:
                if not self.mt4_lib.initialize(port=bridge_port):
                    raise MT4Error("Failed to initialize MT4")

            # 获取账户信息
            self.account_info = self.mt4_lib.account_info()
            if self.account_info is None:
                raise MT4Error("Failed to get account information. Please ensure MT4 is running and logged in.")

            self.connected = True

            # 记录连接成功
            login = self.account_info.login
            server = self.account_info.server
            self.logger.info(f"MT4 connected successfully - Account: {login}, Server: {server}")

            # Log account details
            self.logger.info(f"MT4 Account: {self.account_info.name} - "
                           f"Balance: {self.account_info.balance} {self.account_info.currency}")

            return True
            
        except Exception as e:
            self.connected = False
            log_error_with_context(self.logger, e, "MT4 connection failed")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MT4 terminal."""
        try:
            if self.connected and self.mt4_lib:
                self.mt4_lib.shutdown()
                self.connected = False
                self.logger.info("MT4 disconnected successfully")
        except Exception as e:
            log_error_with_context(self.logger, e, "MT4 disconnection error")
    
    def is_connected(self) -> bool:
        """
        Check if connected to MT4.
        
        Returns:
            True if connected, False otherwise
        """
        if not self.connected or not self.mt4_lib:
            return False
        
        try:
            # Test connection by getting account info
            account_info = self.mt4_lib.account_info()
            return account_info is not None
        except:
            self.connected = False
            return False
    
    @auto_reconnect_mt4
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Get account information.
        
        Returns:
            Account information dictionary or None if failed
        """
        try:
            if not self.is_connected():
                raise ConnectionError("Not connected to MT4")
            
            account_info = self.mt4_lib.account_info()
            if account_info is None:
                return None
            
            return {
                'login': account_info.login,
                'name': account_info.name,
                'server': account_info.server,
                'currency': account_info.currency,
                'balance': account_info.balance,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'free_margin': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'profit': account_info.profit,
                'company': account_info.company,
                'trade_allowed': account_info.trade_allowed,
                'trade_expert': account_info.trade_expert,
                'leverage': account_info.leverage
            }
            
        except Exception as e:
            log_error_with_context(self.logger, e, "Failed to get MT4 account info")
            return None
    
    @auto_reconnect_mt4
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get symbol information.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Symbol information dictionary or None if failed
        """
        try:
            if not self.is_connected():
                raise ConnectionError("Not connected to MT4")
            
            symbol_info = self.mt4_lib.symbol_info(symbol)
            if symbol_info is None:
                return None
            
            return {
                'name': symbol_info.name,
                'description': symbol_info.description,
                'currency_base': symbol_info.currency_base,
                'currency_profit': symbol_info.currency_profit,
                'currency_margin': symbol_info.currency_margin,
                'digits': symbol_info.digits,
                'point': symbol_info.point,
                'spread': symbol_info.spread,
                'volume_min': symbol_info.volume_min,
                'volume_max': symbol_info.volume_max,
                'volume_step': symbol_info.volume_step,
                'trade_mode': symbol_info.trade_mode,
                'bid': symbol_info.bid,
                'ask': symbol_info.ask,
                'time': symbol_info.time
            }
            
        except Exception as e:
            log_error_with_context(self.logger, e, f"Failed to get MT4 symbol info for {symbol}")
            return None
    
    @auto_reconnect_mt4
    def get_positions(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        Get open positions.
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of position dictionaries
        """
        try:
            if not self.is_connected():
                raise ConnectionError("Not connected to MT4")
            
            if symbol:
                positions = self.mt4_lib.positions_get(symbol=symbol)
            else:
                positions = self.mt4_lib.positions_get()
            
            if positions is None:
                return []
            
            result = []
            for pos in positions:
                result.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': pos.type,
                    'type_name': 'BUY' if pos.type == 0 else 'SELL',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'profit': pos.profit,
                    'swap': pos.swap,
                    'comment': pos.comment,
                    'magic': pos.magic,
                    'time': pos.time,
                    'time_update': pos.time_update
                })
            
            return result
            
        except Exception as e:
            log_error_with_context(self.logger, e, "Failed to get MT4 positions")
            return []
    
    @auto_reconnect_mt4
    def get_orders(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        Get pending orders.
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of order dictionaries
        """
        try:
            if not self.is_connected():
                raise ConnectionError("Not connected to MT4")
            
            if symbol:
                orders = self.mt4_lib.orders_get(symbol=symbol)
            else:
                orders = self.mt4_lib.orders_get()
            
            if orders is None:
                return []
            
            result = []
            for order in orders:
                result.append({
                    'ticket': order.ticket,
                    'symbol': order.symbol,
                    'type': order.type,
                    'volume_initial': order.volume_initial,
                    'volume_current': order.volume_current,
                    'price_open': order.price_open,
                    'sl': order.sl,
                    'tp': order.tp,
                    'comment': order.comment,
                    'magic': order.magic,
                    'time_setup': order.time_setup,
                    'time_expiration': order.time_expiration
                })
            
            return result
            
        except Exception as e:
            log_error_with_context(self.logger, e, "Failed to get MT4 orders")
            return []
    
    @auto_reconnect_mt4
    def get_server_time(self) -> Optional[datetime]:
        """
        Get MT4 server time.
        
        Returns:
            Server time as datetime object or None if failed
        """
        try:
            if not self.is_connected():
                return None
            
            # Get latest tick to get server time
            symbols = self.mt4_lib.symbols_get()
            if symbols and len(symbols) > 0:
                tick = self.mt4_lib.symbol_info_tick(symbols[0].name)
                if tick:
                    return datetime.fromtimestamp(tick.time)
            
            return None
            
        except Exception as e:
            log_error_with_context(self.logger, e, "Failed to get MT4 server time")
            return None
    
    @auto_reconnect_mt4
    def check_symbol_availability(self, symbol: str) -> bool:
        """
        Check if symbol is available for trading.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if symbol is available, False otherwise
        """
        try:
            if not self.is_connected():
                return False
            
            symbol_info = self.mt4_lib.symbol_info(symbol)
            if symbol_info is None:
                return False
            
            # Check if symbol is visible and tradeable
            return symbol_info.visible and symbol_info.trade_mode != 0
            
        except Exception as e:
            log_error_with_context(self.logger, e, f"Failed to check MT4 symbol availability for {symbol}")
            return False
