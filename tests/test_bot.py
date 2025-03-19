import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import HyperMonitorBot

class TestHyperMonitorBot(unittest.TestCase):
    """测试HyperMonitorBot类的功能"""
    
    def setUp(self):
        """每个测试之前运行，设置测试环境"""
        # 禁用日志输出
        logging.disable(logging.CRITICAL)
        
        # 创建机器人实例的Patch
        self.bot_patcher = patch('telegram.Bot')
        self.mock_bot = self.bot_patcher.start()
        
        # 创建updater的Patch
        self.updater_patcher = patch('telegram.ext.Updater')
        self.mock_updater = self.updater_patcher.start()
        
        # 创建HyperscanAPI的Patch
        self.api_patcher = patch('hyperscan.HyperscanAPI')
        self.mock_api = self.api_patcher.start()
        
        # 创建机器人实例
        self.hyper_bot = HyperMonitorBot()
        
    def tearDown(self):
        """每个测试之后运行，清理测试环境"""
        # 停止所有Patch
        self.bot_patcher.stop()
        self.updater_patcher.stop()
        self.api_patcher.stop()
        
        # 恢复日志
        logging.disable(logging.NOTSET)
    
    async def test_notify_new_position(self):
        """测试新开仓通知功能"""
        # 模拟新开仓数据
        position = {
            'token': 'MELANIA',
            'direction': 'LONG',
            'leverage': 5,
            'value': 2792478.40,
            'quantity': 3863043.7,
            'token_quantity': '3863043.7 MELANIA',
            'entry_price': 0.71745,
            'funding': 315.71,
            'liquidation_price': 0.65333
        }
        
        # 设置mock的updater实例
        self.hyper_bot.updater = MagicMock()
        self.hyper_bot.updater.bot = MagicMock()
        
        # 调用通知方法
        await self.hyper_bot.notify_new_position(123456789, '0xf3f496c9486be5924a93d67e98298733bb47057c', position)
        
        # 验证bot.send_message被调用
        self.hyper_bot.updater.bot.send_message.assert_called_once()
        
        # 获取调用send_message的参数
        args, kwargs = self.hyper_bot.updater.bot.send_message.call_args
        
        # 验证消息内容包含重要信息
        self.assertIn('新开仓', kwargs['text'])
        self.assertIn('MELANIA', kwargs['text'])
        self.assertIn('LONG', kwargs['text'])
        self.assertIn('$2,792,478.40', kwargs['text'])
    
    async def test_notify_position_change(self):
        """测试持仓变化通知功能"""
        # 模拟持仓变化数据
        change_info = {
            'position': {
                'token': 'MELANIA',
                'direction': 'LONG',
                'value': 3000000.00,
                'quantity': 4000000.0
            },
            'change_type': 'increase',
            'change_percent': 15.0
        }
        
        # 设置mock的updater实例
        self.hyper_bot.updater = MagicMock()
        self.hyper_bot.updater.bot = MagicMock()
        
        # 调用通知方法
        await self.hyper_bot.notify_position_change(123456789, '0xf3f496c9486be5924a93d67e98298733bb47057c', change_info)
        
        # 验证bot.send_message被调用
        self.hyper_bot.updater.bot.send_message.assert_called_once()
        
        # 获取调用send_message的参数
        args, kwargs = self.hyper_bot.updater.bot.send_message.call_args
        
        # 验证消息内容包含重要信息
        self.assertIn('持仓变化', kwargs['text'])
        self.assertIn('MELANIA', kwargs['text'])
        self.assertIn('15.0%', kwargs['text'])
        self.assertIn('增加', kwargs['text'])
    
    async def test_monitor_loop(self):
        """测试监控循环功能"""
        # 设置mock对象
        self.hyper_bot.api = MagicMock()
        self.hyper_bot.updater = MagicMock()
        self.hyper_bot.updater.bot = MagicMock()
        
        # 模拟监控地址
        address = '0xf3f496c9486be5924a93d67e98298733bb47057c'
        self.hyper_bot.monitored_addresses = {123456789: [address]}
        
        # 模拟持仓数据
        mock_data = {'positions': [{'token': 'MELANIA', 'direction': 'LONG', 'value': 2000000.0}]}
        self.hyper_bot.api.get_address_data.return_value = mock_data
        
        # 模拟比较结果 - 无变化
        self.hyper_bot.api.compare_positions.return_value = {'new_positions': [], 'changed_positions': []}
        
        # 运行一次循环
        self.hyper_bot.is_running = False  # 确保循环只运行一次
        await self.hyper_bot.monitor_loop()
        
        # 验证方法调用
        self.hyper_bot.api.get_address_data.assert_called_once_with(address)
        
        # 测试有新持仓时
        position_cache[address] = {'positions': []}
        mock_data = {'positions': [{'token': 'MELANIA', 'direction': 'LONG', 'value': 2000000.0}]}
        self.hyper_bot.api.get_address_data.return_value = mock_data
        self.hyper_bot.api.compare_positions.return_value = {
            'new_positions': [{'token': 'MELANIA', 'direction': 'LONG', 'value': 2000000.0}],
            'changed_positions': []
        }

if __name__ == '__main__':
    unittest.main() 