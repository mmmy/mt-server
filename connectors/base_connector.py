"""
Base connector abstract class for trading platforms.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging


class BaseConnector(ABC):
    """交易连接器抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化连接器
        
        Args:
            config: 平台配置字典
        """
        self.config = config
        self.connected = False
        self.account_info = None
        self.logger = logging.getLogger('mt5_server.connector')
    
    @abstractmethod
    def connect(self) -> bool:
        """
        连接到交易平台
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        检查连接状态
        
        Returns:
            True if connected, False otherwise
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        获取账户信息
        
        Returns:
            Account information dictionary or None if failed
        """
        pass
    
    @abstractmethod
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取品种信息
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Symbol information dictionary or None if failed
        """
        pass
    
    @abstractmethod
    def get_positions(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        获取持仓
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of position dictionaries
        """
        pass
    
    @abstractmethod
    def get_orders(self, symbol: str = None) -> List[Dict[str, Any]]:
        """
        获取挂单
        
        Args:
            symbol: Filter by symbol (optional)
            
        Returns:
            List of order dictionaries
        """
        pass
    
    @abstractmethod
    def get_server_time(self) -> Optional[datetime]:
        """
        获取服务器时间
        
        Returns:
            Server time as datetime object or None if failed
        """
        pass
    
    @abstractmethod
    def check_symbol_availability(self, symbol: str) -> bool:
        """
        检查品种可用性
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if symbol is available, False otherwise
        """
        pass
    
    def get_platform_name(self) -> str:
        """
        获取平台名称
        
        Returns:
            Platform name string
        """
        return self.__class__.__name__.replace('Connector', '').upper()
    
    def validate_connection(self) -> bool:
        """
        验证连接状态
        
        Returns:
            True if connection is valid, False otherwise
        """
        if not self.connected:
            return False
        
        try:
            # 尝试获取账户信息来验证连接
            account_info = self.get_account_info()
            return account_info is not None
        except Exception:
            self.connected = False
            return False
