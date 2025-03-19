# hypurrscan.io Monitor
[![en](https://img.shields.io/badge/lang-English-blue.svg)](README.md) [![cn](https://img.shields.io/badge/语言-中文-red.svg)](README_CN.md)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A Telegram bot for monitoring cryptocurrency wallet positions on HyperScan.io. It supports position querying and new position alerts, tracking real-time changes in perpetual contract positions and notifying users promptly.

## 🚀 Features

- 📊 **Real-time Queries**: Check perpetual contract positions of specified addresses at any time
- 🔄 **Data Updates**: Automatic data refresh every 2 minutes for up-to-date information
- 🔔 **Position Monitoring**: Track changes in address positions, including new positions and significant changes to existing ones
- 🚨 **Smart Alerts**: Automatic notifications for new positions and value changes exceeding 10%
- 📋 **Multi-address Management**: Support for monitoring multiple wallet addresses
- 🔒 **User Authorization**: Only authorized users can use the bot, ensuring data security

## 📸 Demo

![Bot Demo](https://your-image-host.com/demo.png)

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8+
- A Telegram bot token (obtain from [BotFather](https://t.me/botfather))
- Proxy service for accessing Telegram API (if required in your region)

### Installation Steps

1. Clone this repository:

```bash
git clone https://github.com/BugSmith/Hypurrscan_Monitor.git
cd Hypurrscan_Monitor
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

Create a `.env` file with the following content:

```
# Telegram bot token (from BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Authorized user IDs (comma-separated)
AUTHORIZED_USERS=12345678,87654321
```

4. Adjust proxy settings:

If you're in a region that requires a proxy to access Telegram, configure the correct proxy address in `bot.py`:

```python
proxy_url = 'http://127.0.0.1:7890'  # Change to your proxy address
```

## 📝 Usage

1. Start the bot:

```bash
python main.py
```

2. Interact with the bot in Telegram using these commands:

- `/start` - Initialize the bot
- `/help` - Display help information
- `/query [address]` - Query positions for a specific address (uses default address if none specified)
- `/monitor [address]` - Start monitoring a specific address (uses default address if none specified)
- `/stop_monitor [address]` - Stop monitoring a specific address
- `/add_address` - Add a new address to monitor
- `/status` - Check current monitoring status

## ⚙️ Custom Configuration

You can modify the following settings in the `config.py` file:

- `DEFAULT_ADDRESS` - Default wallet address to monitor
- `MONITOR_INTERVAL` - Monitoring interval in seconds
- `MIN_POSITION_VALUE` - Minimum position value threshold for alerts (in USD)

## 🔧 Technical Implementation

- **API Data Retrieval**: Uses HyperScan API to obtain position data
- **Asynchronous Processing**: Employs async I/O for monitoring tasks to improve performance
- **Position Change Detection**: Smart algorithms to detect new positions and significant changes in position value
- **Data Simulation**: Simulates data updates based on timestamps for dynamic price changes

## 🤝 Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact

If you have any questions or suggestions, please contact us through:

- GitHub Issues: [https://github.com/BugSmith/Hypurrscan_Monitor/issues](https://github.com/BugSmith/Hypurrscan_Monitor/issues)
- Email: your-email@example.com

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram bot framework
- [HyperScan](https://hypurrscan.io) - API providing cryptocurrency data

---

For Chinese documentation, please see [README_CN.md](README_CN.md) 