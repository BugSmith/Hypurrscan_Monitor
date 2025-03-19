import logging
import asyncio
from telegram import Update, ParseMode
from telegram.ext import (
    Updater, CommandHandler, CallbackContext, 
    MessageHandler, Filters, ConversationHandler
)
from config import TELEGRAM_BOT_TOKEN, DEFAULT_ADDRESS, AUTHORIZED_USERS, MIN_POSITION_VALUE, MONITOR_INTERVAL
from hyperscan import HyperscanAPI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 会话状态
WAITING_ADDRESS = 1

# 全局变量
monitored_addresses = {}  # 用户ID -> 监控的地址列表
position_cache = {}  # 地址 -> 上次的持仓数据

class HyperMonitorBot:
    def __init__(self):
        self.api = HyperscanAPI()
        self.updater = None
        self.monitor_task = None
        self.is_running = False
    
    def start(self):
        """启动机器人"""
        # Clash代理配置
        # 使用HTTP代理
        proxy_url = 'http://127.0.0.1:7890'
        # 如果HTTP代理不工作，可以尝试SOCKS5代理
        # proxy_url = 'socks5://127.0.0.1:7890'
        
        self.updater = Updater(
            TELEGRAM_BOT_TOKEN,
            request_kwargs={
                'proxy_url': proxy_url,  # Clash代理
                'connect_timeout': 30.0,
                'read_timeout': 30.0
            }
        )
        dispatcher = self.updater.dispatcher
        
        # 注册命令处理函数
        dispatcher.add_handler(CommandHandler("start", self.cmd_start))
        dispatcher.add_handler(CommandHandler("help", self.cmd_help))
        dispatcher.add_handler(CommandHandler("query", self.cmd_query))
        dispatcher.add_handler(CommandHandler("monitor", self.cmd_monitor))
        dispatcher.add_handler(CommandHandler("stop_monitor", self.cmd_stop_monitor))
        dispatcher.add_handler(CommandHandler("status", self.cmd_status))
        
        # 注册地址输入处理
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('add_address', self.cmd_add_address)],
            states={
                WAITING_ADDRESS: [MessageHandler(Filters.text & ~Filters.command, self.process_address)]
            },
            fallbacks=[CommandHandler('cancel', self.cmd_cancel)]
        )
        dispatcher.add_handler(conv_handler)
        
        # 注册错误处理
        dispatcher.add_error_handler(self.error_handler)
        
        # 启动机器人
        self.updater.start_polling()
        logger.info("机器人已启动")
        
        # 初始化监控任务
        self.is_running = True
        
        # 使用线程运行异步监控任务
        import threading
        def run_monitor():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.monitor_loop())
            
        monitor_thread = threading.Thread(target=run_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # 监听Ctrl+C
        self.updater.idle()
    
    async def monitor_loop(self):
        """监控持仓变化的循环"""
        while self.is_running:
            try:
                # 遍历所有用户监控的地址
                for user_id, addresses in monitored_addresses.items():
                    for address in addresses:
                        # 获取最新数据
                        new_data = self.api.get_address_data(address)
                        if not new_data:
                            continue
                            
                        # 检查是否有缓存数据
                        old_data = position_cache.get(address)
                        
                        # 检测持仓变化
                        if old_data:
                            positions_changes = self.api.compare_positions(old_data, new_data)
                            
                            # 发送新开仓通知
                            new_positions = positions_changes.get('new_positions', [])
                            for position in new_positions:
                                # 检查价值是否超过阈值
                                if position.get('value', 0) >= MIN_POSITION_VALUE:
                                    await self.notify_new_position(user_id, address, position)
                            
                            # 发送持仓变化通知
                            changed_positions = positions_changes.get('changed_positions', [])
                            for change_info in changed_positions:
                                # 只通知重大变化
                                await self.notify_position_change(user_id, address, change_info)
                        
                        # 更新缓存
                        position_cache[address] = new_data
                        logger.info(f"已更新地址 {address} 的缓存数据")
                
                # 等待下一个检查周期
                await asyncio.sleep(MONITOR_INTERVAL)  
                
            except Exception as e:
                logger.error(f"监控循环出错: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                await asyncio.sleep(60)  # 出错后等待1分钟再继续
    
    async def notify_new_position(self, user_id, address, position):
        """发送新开仓通知"""
        token = position.get('token', 'Unknown')
        direction = position.get('direction', 'Unknown')
        value = position.get('value', 0)
        leverage = position.get('leverage', 0)
        entry_price = position.get('entry_price', 0)
        liquidation_price = position.get('liquidation_price', 0)
        
        message = f"🚨 <b>新开仓警报</b> 🚨\n\n"
        message += f"📊 <b>地址</b>: <code>{address}</code>\n"
        message += f"🪙 <b>代币</b>: {token}\n"
        message += f"📈 <b>方向</b>: {'做多' if direction == 'LONG' else '做空'}\n"
        message += f"💰 <b>价值</b>: ${value:,.2f}\n"
        message += f"⚡ <b>杠杆</b>: {leverage}x\n"
        message += f"🏁 <b>入场价</b>: ${entry_price:,.4f}\n"
        if liquidation_price:
            message += f"⚠️ <b>清算价</b>: ${liquidation_price:,.4f}\n"
        
        try:
            self.updater.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            logger.info(f"已向用户 {user_id} 发送新开仓通知: {token} {direction}")
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
    
    async def notify_position_change(self, user_id, address, change_info):
        """发送持仓变化通知"""
        position = change_info.get('position', {})
        change_type = change_info.get('change_type', '')
        change_percent = change_info.get('change_percent', 0)
        
        token = position.get('token', 'Unknown')
        direction = position.get('direction', 'Unknown')
        value = position.get('value', 0)
        
        emoji = "📈" if change_type == 'increase' else "📉"
        change_text = "增加" if change_type == 'increase' else "减少"
        
        message = f"{emoji} <b>持仓变化提醒</b> {emoji}\n\n"
        message += f"📊 <b>地址</b>: <code>{address}</code>\n"
        message += f"🪙 <b>代币</b>: {token}\n"
        message += f"📈 <b>方向</b>: {'做多' if direction == 'LONG' else '做空'}\n"
        message += f"💰 <b>当前价值</b>: ${value:,.2f}\n"
        message += f"🔄 <b>变化</b>: {change_text} {change_percent:.2f}%\n"
        
        try:
            self.updater.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            logger.info(f"已向用户 {user_id} 发送持仓变化通知: {token} {direction} {change_text} {change_percent:.2f}%")
        except Exception as e:
            logger.error(f"发送通知失败: {str(e)}")
    
    def stop(self):
        """停止机器人"""
        # 设置停止标志，异步循环会自行结束
        self.is_running = False
        
        if self.updater:
            self.updater.stop()
        
        logger.info("机器人已停止")
    
    def is_authorized(self, user_id):
        """检查用户是否授权使用机器人"""
        if not AUTHORIZED_USERS:  # 如果未设置授权用户，则允许所有用户
            return True
        return user_id in AUTHORIZED_USERS
    
    # 命令处理函数
    def cmd_start(self, update: Update, context: CallbackContext):
        """处理/start命令"""
        user = update.effective_user
        user_id = user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("抱歉，您没有使用此机器人的权限。")
            return
        
        # 初始化用户的监控地址列表
        if user_id not in monitored_addresses:
            monitored_addresses[user_id] = [DEFAULT_ADDRESS]
        
        message = (
            f"👋 你好 {user.first_name}!\n\n"
            f"欢迎使用Hyper监控机器人。此机器人可以帮助你监控特定地址的持仓情况，"
            f"并在发现新开仓时发送通知。\n\n"
            f"默认监控地址: <code>{DEFAULT_ADDRESS}</code>\n\n"
            f"使用 /help 获取可用命令列表。"
        )
        
        update.message.reply_text(message, parse_mode=ParseMode.HTML)
    
    def cmd_help(self, update: Update, context: CallbackContext):
        """处理/help命令"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("抱歉，您没有使用此机器人的权限。")
            return
        
        message = (
            "📋 <b>可用命令列表</b>\n\n"
            "/query [地址] - 查询指定地址的持仓情况 (不指定地址则查询默认地址)\n"
            "/monitor [地址] - 开始监控指定地址 (不指定地址则监控默认地址)\n"
            "/stop_monitor [地址] - 停止监控指定地址\n"
            "/add_address - 添加新的监控地址\n"
            "/status - 查看当前监控状态\n"
            "/help - 显示此帮助信息"
        )
        
        update.message.reply_text(message, parse_mode=ParseMode.HTML)
    
    def cmd_query(self, update: Update, context: CallbackContext):
        """处理/query命令"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("抱歉，您没有使用此机器人的权限。")
            return
        
        # 获取参数中的地址，如果没有提供则使用默认地址
        address = context.args[0] if context.args else DEFAULT_ADDRESS
        
        # 发送等待消息
        wait_message = update.message.reply_text("正在查询数据，请稍候...")
        
        # 获取数据
        data = self.api.get_address_data(address)
        
        if not data:
            wait_message.edit_text(f"无法获取地址 {address} 的数据，请确保地址正确。")
            return
        
        # 构建响应消息
        message = f"📊 <b>{address}</b> 持仓情况\n\n"
        
        # 添加概览信息
        overview = data.get('overview', {})
        perps = overview.get('perps', {})
        spot = overview.get('spot', {})
        vault = overview.get('vault', {})
        staked = overview.get('staked', {})
        
        message += f"🔄 <b>Perps ({perps.get('count', 0)})</b>: ${perps.get('value', 0):,.2f}\n"
        message += f"💱 <b>Spot ({spot.get('count', 0)})</b>: ${spot.get('value', 0):,.2f}\n"
        message += f"🏦 <b>Vault</b>: ${vault.get('value', 0):,.2f}\n"
        message += f"⚓ <b>Staked</b>: ${staked.get('value', 0):,.2f}\n\n"
        
        # 添加持仓信息
        positions = data.get('positions', [])
        if positions:
            message += f"📋 <b>当前持仓 ({len(positions)})</b>:\n\n"
            
            for i, position in enumerate(positions, 1):
                token = position.get('token', 'Unknown')
                direction = position.get('direction', 'Unknown')
                value = position.get('value', 0)
                leverage = position.get('leverage', 0)
                entry_price = position.get('entry_price', 0)
                funding = position.get('funding', 0)
                liquidation_price = position.get('liquidation_price', 0)
                
                message += f"{i}. <b>{token}</b> ({'做多' if direction == 'LONG' else '做空'}):\n"
                message += f"   💰 价值: ${value:,.2f}\n"
                message += f"   ⚡ 杠杆: {leverage}x\n"
                message += f"   🏁 入场价: ${entry_price:,.6f}\n"
                message += f"   💵 资金费: ${funding:,.2f}\n"
                message += f"   ⚠️ 清算价: ${liquidation_price:,.6f}\n\n"
        else:
            message += "当前没有活跃持仓。\n\n"
            
        # 添加代币持有信息
        holdings = data.get('holdings', {})
        if holdings:
            message += f"💼 <b>代币持有</b>:\n\n"
            for token, amount in holdings.items():
                if amount > 0:
                    message += f"   {token}: {amount:,.2f}\n"
        
        # 添加更新时间
        if 'updated_at' in data:
            from datetime import datetime
            update_time = datetime.fromtimestamp(data['updated_at']).strftime('%Y-%m-%d %H:%M:%S')
            message += f"\n🕒 <b>更新时间</b>: {update_time}"
        
        # 发送消息
        wait_message.edit_text(message, parse_mode=ParseMode.HTML)
    
    def cmd_monitor(self, update: Update, context: CallbackContext):
        """处理/monitor命令"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("抱歉，您没有使用此机器人的权限。")
            return
        
        # 获取参数中的地址，如果没有提供则使用默认地址
        address = context.args[0] if context.args else DEFAULT_ADDRESS
        
        # 初始化用户的监控地址列表
        if user_id not in monitored_addresses:
            monitored_addresses[user_id] = []
        
        # 检查地址是否已经在监控列表中
        if address in monitored_addresses[user_id]:
            update.message.reply_text(f"已经在监控地址 {address}")
            return
        
        # 添加到监控列表
        monitored_addresses[user_id].append(address)
        
        # 初始化持仓缓存
        if address not in position_cache:
            data = self.api.get_address_data(address)
            if data:
                position_cache[address] = data
        
        update.message.reply_text(f"开始监控地址: {address}")
    
    def cmd_stop_monitor(self, update: Update, context: CallbackContext):
        """处理/stop_monitor命令"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("抱歉，您没有使用此机器人的权限。")
            return
        
        # 获取参数中的地址
        if not context.args:
            update.message.reply_text("请指定要停止监控的地址。")
            return
            
        address = context.args[0]
        
        # 检查用户是否有监控地址
        if user_id not in monitored_addresses or not monitored_addresses[user_id]:
            update.message.reply_text("您当前没有监控任何地址。")
            return
        
        # 从监控列表中移除
        if address in monitored_addresses[user_id]:
            monitored_addresses[user_id].remove(address)
            update.message.reply_text(f"已停止监控地址: {address}")
        else:
            update.message.reply_text(f"未找到监控地址: {address}")
    
    def cmd_add_address(self, update: Update, context: CallbackContext):
        """处理/add_address命令"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("抱歉，您没有使用此机器人的权限。")
            return
        
        update.message.reply_text("请输入要添加的钱包地址:")
        return WAITING_ADDRESS
    
    def process_address(self, update: Update, context: CallbackContext):
        """处理用户输入的地址"""
        user_id = update.effective_user.id
        address = update.message.text.strip()
        
        # 简单验证地址格式（以0x开头的以太坊地址）
        if not address.startswith("0x") or len(address) != 42:
            update.message.reply_text("地址格式不正确，请输入有效的以太坊地址。")
            return WAITING_ADDRESS
        
        # 初始化用户的监控地址列表
        if user_id not in monitored_addresses:
            monitored_addresses[user_id] = []
        
        # 检查地址是否已经在监控列表中
        if address in monitored_addresses[user_id]:
            update.message.reply_text(f"已经在监控地址 {address}")
        else:
            # 添加到监控列表
            monitored_addresses[user_id].append(address)
            
            # 初始化持仓缓存
            if address not in position_cache:
                data = self.api.get_address_data(address)
                if data:
                    position_cache[address] = data
            
            update.message.reply_text(f"已添加监控地址: {address}")
        
        return ConversationHandler.END
    
    def cmd_cancel(self, update: Update, context: CallbackContext):
        """取消当前操作"""
        update.message.reply_text("操作已取消。")
        return ConversationHandler.END
    
    def cmd_status(self, update: Update, context: CallbackContext):
        """处理/status命令"""
        user_id = update.effective_user.id
        
        if not self.is_authorized(user_id):
            update.message.reply_text("抱歉，您没有使用此机器人的权限。")
            return
        
        # 检查用户是否有监控地址
        if user_id not in monitored_addresses or not monitored_addresses[user_id]:
            update.message.reply_text("您当前没有监控任何地址。")
            return
        
        # 构建状态消息
        message = "📋 <b>当前监控状态</b>\n\n"
        message += f"监控地址数量: {len(monitored_addresses[user_id])}\n\n"
        
        for i, address in enumerate(monitored_addresses[user_id], 1):
            message += f"{i}. <code>{address}</code>\n"
        
        update.message.reply_text(message, parse_mode=ParseMode.HTML)
    
    def error_handler(self, update, context):
        """处理错误"""
        logger.error(f"更新 {update} 导致错误 {context.error}")
        
        # 发送错误通知给用户
        if update and update.effective_message:
            update.effective_message.reply_text("处理命令时发生错误，请稍后再试。")

# 如果直接运行此文件
if __name__ == "__main__":
    bot = HyperMonitorBot()
    bot.start() 