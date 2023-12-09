import unittest
from flask import json
from pebble import app, blockchain

class TestBlockchainApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_mine_block(self):
        response = self.app.get('/mine_block')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Congratulations, you just mined a block!', data['message'])

    def test_get_chain(self):
        response = self.app.get('/get_chain')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('chain', data)
        self.assertIn('length', data)

    def test_is_valid(self):
        response = self.app.get('/is_valid')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'All good. The Blockchain is valid.')

    def test_add_transaction(self):
        data = {'sender': 'Alice', 'receiver': 'Bob', 'amount': 5}
        response = self.app.post('/add_transaction', json=data)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', data)

    def test_connect_node(self):
        data = {'nodes': ['http://localhost:5000']}
        response = self.app.post('/connect_node', json=data)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', data)
        self.assertIn('total_nodes', data)

    def test_replace_chain(self):
        response = self.app.get('/replace_chain')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertIn('actual_chain', data)
    
    def test_hash_function(self):
        block = {
            'index': 1,
            'timestamp': '2023-12-01 12:00:00',
            'proof': 123,
            'previous_hash': 'abc123',
            'transactions': [{'sender': 'Alice', 'receiver': 'Bob', 'amount': 5}]
        }
        actual_hash = blockchain.hash(block)
        self.assertEqual(len(actual_hash), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in actual_hash))

if __name__ == '__main__':
    unittest.main()
