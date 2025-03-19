import unittest
import json
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hyperscan import HyperscanAPI

class TestHyperscanAPI(unittest.TestCase):
    """测试HyperscanAPI类的功能"""
    
    def setUp(self):
        """每个测试之前运行"""
        self.api = HyperscanAPI()
    
    @patch('hyperscan.requests.Session')
    def test_get_perps_positions(self, mock_session):
        """测试获取永续合约持仓功能"""
        # 模拟response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response
        
        # 测试已知地址
        address = "0xf3f496c9486be5924a93d67e98298733bb47057c"
        positions = self.api.get_perps_positions(address)
        
        # 验证返回数据
        self.assertIsInstance(positions, list)
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]['token'], 'MELANIA')
        self.assertEqual(positions[0]['direction'], 'LONG')
        
        # 测试未知地址
        positions = self.api.get_perps_positions("0x0000000000000000000000000000000000000000")
        self.assertEqual(positions, [])
    
    def test_compare_positions(self):
        """测试持仓比较功能"""
        # 测试数据
        old_data = {
            'positions': [
                {
                    'token': 'MELANIA',
                    'direction': 'LONG',
                    'value': 2000000.0
                }
            ]
        }
        
        # 测试无变化情况
        new_data = {
            'positions': [
                {
                    'token': 'MELANIA',
                    'direction': 'LONG',
                    'value': 2000000.0
                }
            ]
        }
        result = self.api.compare_positions(old_data, new_data)
        self.assertEqual(len(result['new_positions']), 0)
        self.assertEqual(len(result['changed_positions']), 0)
        
        # 测试新增持仓
        new_data = {
            'positions': [
                {
                    'token': 'MELANIA',
                    'direction': 'LONG',
                    'value': 2000000.0
                },
                {
                    'token': 'HYPE',
                    'direction': 'SHORT',
                    'value': 100000.0
                }
            ]
        }
        result = self.api.compare_positions(old_data, new_data)
        self.assertEqual(len(result['new_positions']), 1)
        self.assertEqual(result['new_positions'][0]['token'], 'HYPE')
        
        # 测试持仓变化（>10%）
        new_data = {
            'positions': [
                {
                    'token': 'MELANIA',
                    'direction': 'LONG',
                    'value': 2500000.0  # 增加25%
                }
            ]
        }
        result = self.api.compare_positions(old_data, new_data)
        self.assertEqual(len(result['new_positions']), 0)
        self.assertEqual(len(result['changed_positions']), 1)
        self.assertEqual(result['changed_positions'][0]['change_type'], 'increase')
        self.assertAlmostEqual(result['changed_positions'][0]['change_percent'], 25.0)
        
        # 测试持仓减少
        new_data = {
            'positions': [
                {
                    'token': 'MELANIA',
                    'direction': 'LONG',
                    'value': 1500000.0  # 减少25%
                }
            ]
        }
        result = self.api.compare_positions(old_data, new_data)
        self.assertEqual(result['changed_positions'][0]['change_type'], 'decrease')
        self.assertAlmostEqual(result['changed_positions'][0]['change_percent'], 25.0)

if __name__ == '__main__':
    unittest.main() 