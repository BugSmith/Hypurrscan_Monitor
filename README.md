# Hyper Monitor（超级监控）

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

一个用于监控HyperScan加密钱包地址持仓情况的Telegram机器人，支持查询持仓和新开仓报警功能。实时监测地址的永续合约持仓变化，及时通知用户。

## 🚀 功能

- 📊 **实时查询**：随时查询指定地址的永续合约持仓情况
- 🔄 **数据更新**：每2分钟自动更新数据，确保信息实时性
- 🔔 **持仓监控**：监控地址的持仓变化，包括新开仓和现有持仓的重大变化
- 🚨 **智能提醒**：新开仓位和价值变化超过10%时自动发送通知
- 📋 **多地址管理**：支持监控多个钱包地址
- 🔒 **用户授权**：只有授权用户才能使用机器人，保证数据安全

## 📸 效果展示

![机器人效果展示](https://your-image-host.com/demo.png)

## 🛠️ 安装与配置

### 前提条件

- Python 3.8+
- 已创建的Telegram机器人令牌 (通过 [BotFather](https://t.me/botfather) 获取)
- 用于访问Telegram API的代理服务

### 安装步骤

1. 克隆此仓库：

```bash
git clone https://github.com/your-username/hyper-monitor.git
cd hyper-monitor
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置环境变量：

创建`.env`文件并添加以下内容：

```
# Telegram机器人令牌（从BotFather获取）
TELEGRAM_BOT_TOKEN=your_bot_token_here

# 授权用户ID（多个ID用逗号分隔）
AUTHORIZED_USERS=12345678,87654321
```

4. 调整代理设置：

如果在中国或其他需要使用代理访问Telegram的地区，请在`bot.py`中配置正确的代理地址：

```python
proxy_url = 'http://127.0.0.1:7890'  # 改为您的代理地址
```

## 📝 使用方法

1. 启动机器人：

```bash
python main.py
```

2. 在Telegram中与机器人互动，使用以下命令：

- `/start` - 初始化机器人
- `/help` - 显示帮助信息
- `/query [地址]` - 查询指定地址的持仓情况 (不指定地址则查询默认地址)
- `/monitor [地址]` - 开始监控指定地址 (不指定地址则监控默认地址)
- `/stop_monitor [地址]` - 停止监控指定地址
- `/add_address` - 添加新的监控地址
- `/status` - 查看当前监控状态

## ⚙️ 自定义配置

在`config.py`文件中可以修改以下配置：

- `DEFAULT_ADDRESS` - 默认监控的钱包地址
- `MONITOR_INTERVAL` - 监控间隔 (秒)
- `MIN_POSITION_VALUE` - 开仓警报最小价值阈值 (美元)

## 🔧 技术实现

- **接口数据获取**：使用HyperScan API获取持仓数据
- **异步处理**：采用异步IO处理监控任务，提高性能
- **持仓变化检测**：智能算法检测新开仓和持仓价值变化
- **数据模拟**：根据时间戳模拟数据更新，实现动态价格变化

## 🤝 贡献指南

欢迎提交问题和拉取请求！如果您想为项目做出贡献，请遵循以下步骤：

1. Fork 这个仓库
2. 创建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 📜 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

## 📬 联系方式

如有任何问题或建议，请通过以下方式联系我：

- GitHub Issues: [https://github.com/your-username/hyper-monitor/issues](https://github.com/your-username/hyper-monitor/issues)
- 电子邮件: your-email@example.com

## 🙏 致谢

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram机器人框架
- [HyperScan](https://hypurrscan.io) - 提供加密货币数据的API 