#!/usr/bin/env python3
"""
测试平台切换功能的脚本
"""

import os
import sys
import yaml
import tempfile
from pathlib import Path

def test_platform_switch():
    """测试平台切换功能"""
    
    print("🧪 开始测试MT5/MT4双平台切换功能...")
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
        
        # 写入测试配置
        test_config = {
            'trading_platform': 'mt5',
            'mt5': {
                'terminal_path': '',
                'timeout': {'connect': 30, 'trade': 10}
            },
            'mt4': {
                'terminal_path': '',
                'bridge_port': 7788,
                'ea_name': 'MT4Bridge',
                'timeout': {'connect': 30, 'trade': 10}
            },
            'server': {
                'host': '127.0.0.1',
                'port': 5000,
                'debug': False,
                'security': {'api_key': '', 'allowed_ips': []}
            },
            'trading': {
                'default_volume': 0.1,
                'max_volume': 10.0,
                'min_volume': 0.01,
                'max_slippage': 3,
                'magic_number': 12345,
                'allowed_symbols': []
            },
            'logging': {
                'level': 'INFO',
                'file': 'test.log',
                'max_size': 10485760,
                'backup_count': 5,
                'console': True,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'webhook': {
                'validate_source': False,
                'timeout': 30,
                'required_fields': ['action', 'symbol'],
                'optional_fields': {'volume': 0.1, 'comment': 'Webhook Trade'}
            }
        }
        
        yaml.dump(test_config, f, default_flow_style=False)
    
    try:
        # 测试MT5配置
        print("\n📋 测试1: MT5平台配置")
        test_config['trading_platform'] = 'mt5'
        
        with open(temp_config, 'w') as f:
            yaml.dump(test_config, f)
        
        # 设置环境变量
        os.environ['TRADING_PLATFORM'] = 'mt5'
        
        # 导入并测试配置管理器
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from config_manager import ConfigManager
        
        try:
            config_manager = ConfigManager(temp_config)
            platform = config_manager.get_trading_platform()
            print(f"✅ 当前平台: {platform.upper()}")
            
            # 测试连接器工厂
            from connectors.connector_factory import ConnectorFactory
            supported_platforms = ConnectorFactory.get_supported_platforms()
            print(f"✅ 支持的平台: {supported_platforms}")
            
            # 测试配置验证
            config = config_manager.get_config()
            print(f"✅ 配置验证通过")
            
        except Exception as e:
            print(f"❌ MT5配置测试失败: {e}")
            return False
        
        # 测试MT4配置
        print("\n📋 测试2: MT4平台配置")
        test_config['trading_platform'] = 'mt4'
        
        with open(temp_config, 'w') as f:
            yaml.dump(test_config, f)
        
        # 更新环境变量
        os.environ['TRADING_PLATFORM'] = 'mt4'
        
        try:
            config_manager = ConfigManager(temp_config)
            platform = config_manager.get_trading_platform()
            print(f"✅ 当前平台: {platform.upper()}")
            
            # 测试配置验证
            config = config_manager.get_config()
            print(f"✅ 配置验证通过")
            
        except Exception as e:
            print(f"❌ MT4配置测试失败: {e}")
            return False
        
        # 测试环境变量优先级
        print("\n📋 测试3: 环境变量优先级")
        test_config['trading_platform'] = 'mt5'  # 配置文件中设为MT5
        
        with open(temp_config, 'w') as f:
            yaml.dump(test_config, f)
        
        os.environ['TRADING_PLATFORM'] = 'mt4'  # 环境变量设为MT4
        
        try:
            config_manager = ConfigManager(temp_config)
            platform = config_manager.get_trading_platform()
            print(f"✅ 环境变量优先级测试通过: {platform.upper()} (应为MT4)")
            
            if platform != 'mt4':
                print(f"❌ 环境变量优先级测试失败: 期望MT4，实际{platform}")
                return False
                
        except Exception as e:
            print(f"❌ 环境变量优先级测试失败: {e}")
            return False
        
        # 测试连接器创建
        print("\n📋 测试4: 连接器工厂创建")
        
        try:
            # 测试MT5连接器创建
            mt5_config = {'mt5': test_config['mt5']}
            mt5_connector = ConnectorFactory.create_connector('mt5', mt5_config)
            print(f"✅ MT5连接器创建成功: {type(mt5_connector).__name__}")
            
            # 测试MT4连接器创建
            mt4_config = {'mt4': test_config['mt4']}
            mt4_connector = ConnectorFactory.create_connector('mt4', mt4_config)
            print(f"✅ MT4连接器创建成功: {type(mt4_connector).__name__}")
            
        except Exception as e:
            print(f"❌ 连接器创建测试失败: {e}")
            return False
        
        print("\n🎉 所有测试通过！双平台切换功能正常工作。")
        return True
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_config):
            os.unlink(temp_config)
        
        # 清理环境变量
        if 'TRADING_PLATFORM' in os.environ:
            del os.environ['TRADING_PLATFORM']

def test_config_examples():
    """测试配置示例文件"""
    print("\n📋 测试5: 配置示例文件验证")
    
    try:
        # 检查配置示例文件
        config_example = 'config.yaml.example'
        env_example = '.env.example'
        
        if not os.path.exists(config_example):
            print(f"❌ 配置示例文件不存在: {config_example}")
            return False
        
        if not os.path.exists(env_example):
            print(f"❌ 环境变量示例文件不存在: {env_example}")
            return False
        
        # 验证配置示例文件
        with open(config_example, 'r', encoding='utf-8') as f:
            config_content = yaml.safe_load(f)
        
        required_sections = ['trading_platform', 'mt5', 'mt4', 'server', 'trading', 'logging', 'webhook']
        for section in required_sections:
            if section not in config_content:
                print(f"❌ 配置示例文件缺少必需部分: {section}")
                return False
        
        print("✅ 配置示例文件验证通过")
        
        # 验证环境变量示例文件
        with open(env_example, 'r', encoding='utf-8') as f:
            env_content = f.read()
        
        if 'TRADING_PLATFORM' not in env_content:
            print("❌ 环境变量示例文件缺少TRADING_PLATFORM")
            return False
        
        print("✅ 环境变量示例文件验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置示例文件测试失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("MT5/MT4 双平台切换功能测试")
    print("=" * 60)
    
    success = True
    
    # 运行平台切换测试
    if not test_platform_switch():
        success = False
    
    # 运行配置示例测试
    if not test_config_examples():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有测试通过！系统已成功支持MT5/MT4双平台。")
        print("\n📖 使用说明:")
        print("1. 在.env文件中设置 TRADING_PLATFORM=mt5 或 TRADING_PLATFORM=mt4")
        print("2. 或在config.yaml中设置 trading_platform")
        print("3. 环境变量优先级高于配置文件")
        print("4. 重启服务器即可切换平台")
    else:
        print("❌ 部分测试失败，请检查配置和代码。")
        sys.exit(1)
