import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# Telegram机器人令牌
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 默认监控的钱包地址
DEFAULT_ADDRESS = "0xf3F496C9486BE5924a93D67e98298733Bb47057c"

# Hyperscan 基础URL
HYPERSCAN_BASE_URL = "https://hypurrscan.io"

# Hyperscan API 基础URL
HYPERSCAN_API_BASE_URL = "https://api.hypurrscan.io"

# 监控间隔(秒)
MONITOR_INTERVAL = 120  # 2分钟

# 授权的用户ID列表(只有这些用户可以使用机器人)
AUTHORIZED_USERS = [int(id) for id in os.getenv("AUTHORIZED_USERS", "").split(",") if id]

# 开仓警报阈值
MIN_POSITION_VALUE = 5000  # 美元 