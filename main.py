#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import asyncio
from bot import HyperMonitorBot
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hyper_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

async def main():
    """主函数"""
    try:
        # 检查Telegram机器人令牌是否设置
        if not os.getenv("TELEGRAM_BOT_TOKEN"):
            logger.error("缺少TELEGRAM_BOT_TOKEN环境变量！请在.env文件中设置。")
            return
        
        # 启动机器人
        bot = HyperMonitorBot()
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("收到退出信号，正在停止机器人...")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")

if __name__ == "__main__":
    # 检查是否存在.env文件
    if not os.path.exists(".env"):
        logger.warning("未找到.env文件，创建示例配置...")
        with open(".env", "w") as f:
            f.write("# Telegram机器人令牌（从BotFather获取）\n")
            f.write("TELEGRAM_BOT_TOKEN=your_bot_token_here\n\n")
            f.write("# 授权用户ID（多个ID用逗号分隔）\n")
            f.write("AUTHORIZED_USERS=12345678,87654321\n")
        logger.info("已创建.env文件模板，请编辑并填写相关配置后重新运行程序。")
        exit(0)
    
    # 运行主函数
    asyncio.run(main()) 