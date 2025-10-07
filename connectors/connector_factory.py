"""
Connector Factory for creating platform-specific connectors.
"""

from typing import Dict, Any
from .base_connector import BaseConnector
from .mt5_connector import MT5Connector
from .mt4_connector import MT4Connector


class ConnectorFactory:
    """连接器工厂类"""
    
    _connectors = {
        'mt5': MT5Connector,
        'mt4': MT4Connector,
    }
    
    @classmethod
    def create_connector(cls, platform: str, config: Dict[str, Any]) -> BaseConnector:
        """
        根据平台类型创建连接器
        
        Args:
            platform: 平台类型 ('mt5' 或 'mt4')
            config: 平台配置字典
            
        Returns:
            对应平台的连接器实例
            
        Raises:
            ValueError: 当平台类型不支持时
        """
        platform = platform.lower()
        
        if platform not in cls._connectors:
            supported_platforms = ', '.join(cls._connectors.keys())
            raise ValueError(f"Unsupported trading platform: {platform}. "
                           f"Supported platforms: {supported_platforms}")
        
        connector_class = cls._connectors[platform]
        return connector_class(config)
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """
        获取支持的平台列表
        
        Returns:
            支持的平台名称列表
        """
        return list(cls._connectors.keys())
    
    @classmethod
    def is_platform_supported(cls, platform: str) -> bool:
        """
        检查平台是否支持
        
        Args:
            platform: 平台名称
            
        Returns:
            True if supported, False otherwise
        """
        return platform.lower() in cls._connectors
    
    @classmethod
    def register_connector(cls, platform: str, connector_class: type):
        """
        注册新的连接器类
        
        Args:
            platform: 平台名称
            connector_class: 连接器类
        """
        if not issubclass(connector_class, BaseConnector):
            raise ValueError("Connector class must inherit from BaseConnector")
        
        cls._connectors[platform.lower()] = connector_class
    
    @classmethod
    def get_platform_config_schema(cls, platform: str) -> Dict[str, Any]:
        """
        获取平台配置模式
        
        Args:
            platform: 平台名称
            
        Returns:
            配置模式字典
        """
        platform = platform.lower()
        
        schemas = {
            'mt5': {
                'terminal_path': {
                    'type': 'string',
                    'required': False,
                    'description': 'MT5 terminal executable path'
                },
                'timeout': {
                    'type': 'dict',
                    'required': False,
                    'properties': {
                        'connect': {'type': 'integer', 'default': 30},
                        'trade': {'type': 'integer', 'default': 10}
                    }
                }
            },
            'mt4': {
                'terminal_path': {
                    'type': 'string',
                    'required': False,
                    'description': 'MT4 terminal executable path'
                },
                'bridge_port': {
                    'type': 'integer',
                    'required': False,
                    'default': 7788,
                    'description': 'MT4 bridge server port'
                },
                'ea_name': {
                    'type': 'string',
                    'required': False,
                    'default': 'MT4Bridge',
                    'description': 'MT4 Expert Advisor name'
                },
                'timeout': {
                    'type': 'dict',
                    'required': False,
                    'properties': {
                        'connect': {'type': 'integer', 'default': 30},
                        'trade': {'type': 'integer', 'default': 10}
                    }
                }
            }
        }
        
        return schemas.get(platform, {})
