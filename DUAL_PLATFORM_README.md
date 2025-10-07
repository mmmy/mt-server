# MT5/MT4 双平台支持说明

## 概述

本系统现已支持 MT5 和 MT4 双平台，可以通过配置文件或环境变量轻松切换交易平台。

## 🚀 快速开始

### 1. 切换到 MT5 平台

#### 方法 1：使用环境变量（推荐）

```bash
# 在.env文件中设置
TRADING_PLATFORM=mt5

# 或直接设置环境变量
export TRADING_PLATFORM=mt5
```

#### 方法 2：使用配置文件

```yaml
# 在config.yaml中设置
trading_platform: "mt5"
```

### 2. 切换到 MT4 平台

#### 方法 1：使用环境变量（推荐）

```bash
# 在.env文件中设置
TRADING_PLATFORM=mt4

# 或直接设置环境变量
export TRADING_PLATFORM=mt4
```

#### 方法 2：使用配置文件

```yaml
# 在config.yaml中设置
trading_platform: "mt4"
```

### 3. 重启服务器

```bash
python app.py
# 或
python start_server.py
```

## 📋 配置说明

### 环境变量配置

创建或编辑 `.env` 文件：

```bash
# 交易平台选择 (mt5 或 mt4)
TRADING_PLATFORM=mt5

# MT5 配置
MT5_TERMINAL_PATH=""
MT5_TIMEOUT_CONNECT=30
MT5_TIMEOUT_TRADE=10

# MT4 配置
MT4_TERMINAL_PATH=""
MT4_BRIDGE_PORT=7788
MT4_EA_NAME="MT4Bridge"
MT4_TIMEOUT_CONNECT=30
MT4_TIMEOUT_TRADE=10

# 服务器配置
SERVER_HOST=127.0.0.1
SERVER_PORT=5000
DEBUG_MODE=false

# API安全
API_KEY=""

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/mt5_server.log
```

### 配置文件配置

编辑 `config.yaml` 文件：

```yaml
# 交易平台配置
trading_platform: "mt5" # Options: mt5, mt4

# MT5 设置
mt5:
  terminal_path: "" # MT5终端路径（可选）
  timeout:
    connect: 30 # 连接超时（秒）
    trade: 10 # 交易超时（秒）

# MT4 设置
mt4:
  terminal_path: "" # MT4终端路径（可选）
  bridge_port: 7788 # MT4桥接服务器端口
  ea_name: "MT4Bridge" # MT4专家顾问名称
  timeout:
    connect: 30 # 连接超时（秒）
    trade: 10 # 交易超时（秒）

# 交易设置
trading:
  default_volume: 0.1
  max_volume: 10.0
  min_volume: 0.01
  max_slippage: 3
  magic_number: 12345
  allowed_symbols: []

# 服务器设置
server:
  host: "127.0.0.1"
  port: 5000
  debug: false
  security:
    api_key: ""
    allowed_ips: []

# 日志设置
logging:
  level: "INFO"
  file: "mt5_server.log"
  max_size: 10485760
  backup_count: 5
  console: true
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Webhook设置
webhook:
  validate_source: false
  timeout: 30
  required_fields:
    - "action"
    - "symbol"
  optional_fields:
    volume: 0.1
    comment: "Webhook Trade"
```

## 🔧 平台特定要求

### MT5 平台要求

1. **系统要求**：

   - Windows 操作系统
   - MetaTrader 5 终端已安装
   - Python 3.7+

2. **依赖安装**：

   ```bash
   pip install MetaTrader5
   ```

3. **MT5 终端设置**：
   - 启用"允许算法交易"
   - 确保终端已登录交易账户

### MT4 平台要求

1. **系统要求**：

   - Windows 操作系统
   - MetaTrader 4 终端已安装
   - Python 3.7+

2. **依赖安装**：

   ```bash
   pip install MetaTrader4
   ```

   **注意**：MT4 Python 库可能需要额外的桥接程序或 EA。

3. **MT4 终端设置**：
   - 启用"允许算法交易"
   - 启用"允许 DLL 导入"
   - 安装桥接 EA（如需要）
   - 确保终端已登录交易账户

## 📊 API 响应差异

双平台支持的 API 响应会包含平台信息：

### 健康检查响应

```json
{
  "status": "healthy",
  "platform": "MT5", // 或 "MT4"
  "connected": true,
  "account_info": {
    "login": 123456,
    "server": "Broker-Demo",
    "balance": 10000.0,
    "equity": 10000.0
  },
  "timestamp": "2025-01-15T10:30:00"
}
```

### 状态响应

```json
{
  "server_status": "running",
  "platform": "MT4", // 或 "MT5"
  "connected": true,
  "account_info": {
    "login": 123456,
    "server": "Broker-Demo",
    "balance": 10000.0,
    "equity": 10000.0
  },
  "timestamp": "2025-01-15T10:30:00"
}
```

## 🔄 切换流程

### 从 MT5 切换到 MT4

1. **停止服务器**：

   ```bash
   # 如果服务器正在运行，按 Ctrl+C 停止
   ```

2. **修改配置**：

   ```bash
   # 方法1：修改环境变量
   export TRADING_PLATFORM=mt4

   # 方法2：修改.env文件
   echo "TRADING_PLATFORM=mt4" >> .env

   # 方法3：修改config.yaml
   sed -i 's/trading_platform: "mt5"/trading_platform: "mt4"/' config.yaml
   ```

3. **启动服务器**：

   ```bash
   python app.py
   ```

4. **验证切换**：
   ```bash
   curl http://127.0.0.1:5000/health
   ```

### 从 MT4 切换到 MT5

同样的流程，只需将平台设置为"mt5"。

## 🛠️ 故障排除

### 常见问题

1. **连接失败**：

   - 确保对应的 MT5/MT4 终端正在运行
   - 检查终端是否已登录交易账户
   - 验证是否启用了算法交易

2. **配置错误**：

   - 检查环境变量是否正确设置
   - 验证配置文件格式是否正确
   - 确认平台名称拼写正确（mt5 或 mt4）

3. **依赖问题**：
   - 确保安装了正确的 Python 库
   - 检查 Python 版本兼容性

### 调试步骤

1. **检查当前平台**：

   ```bash
   python -c "
   from config_manager import ConfigManager
   cm = ConfigManager()
   print(f'当前平台: {cm.get_trading_platform().upper()}')
   "
   ```

2. **测试连接器创建**：

   ```bash
   python -c "
   from connectors.connector_factory import ConnectorFactory
   config = {'mt5': {'terminal_path': ''}}
   connector = ConnectorFactory.create_connector('mt5', config)
   print(f'连接器类型: {type(connector).__name__}')
   "
   ```

3. **查看日志**：
   ```bash
   tail -f logs/mt5_server.log
   ```

## 📝 开发说明

### 架构设计

系统采用工厂模式和抽象基类设计：

```
HTTP API Layer
    ↓
Trading Manager (业务逻辑层)
    ↓
BaseConnector (抽象接口层)
    ↓
MT5Connector / MT4Connector (具体实现层)
    ↓
MT5 Terminal / MT4 Terminal (交易平台)
```

### 添加新平台

如需添加新的交易平台：

1. 创建新的连接器类继承`BaseConnector`
2. 实现所有抽象方法
3. 在`ConnectorFactory`中注册新平台
4. 更新配置验证逻辑
5. 添加相应的测试

### 测试

运行双平台测试：

```bash
python test_platform_switch.py
```

## 🔒 安全注意事项

1. **账户安全**：

   - 使用演示账户进行测试
   - 不要在生产环境中使用默认配置
   - 定期更改 API 密钥

2. **网络安全**：

   - 配置 IP 白名单
   - 使用强 API 密钥
   - 启用 HTTPS（生产环境）

3. **交易安全**：
   - 设置合理的交易量限制
   - 配置止损和风险控制
   - 监控交易日志

## 📞 支持

如有问题或建议，请：

1. 查看日志文件获取详细错误信息
2. 运行测试脚本诊断问题
3. 检查配置文件格式
4. 确认平台依赖已正确安装

---

**注意**：MT4 支持需要额外的桥接程序或 EA，具体取决于使用的 MT4 Python 库实现。
