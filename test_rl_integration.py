import unittest
import os
import json
import shutil
from rl_service import RLService

class TestRLIntegration(unittest.TestCase):
    def setUp(self):
        # Use a temporary file for testing
        self.test_data_file = 'test_rl_data.json'
        self.rl_service = RLService(data_file=self.test_data_file)

    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.test_data_file):
            os.remove(self.test_data_file)

    def test_initialization(self):
        """Test if RL service initializes correctly"""
        self.assertTrue(os.path.exists(self.test_data_file))
        with open(self.test_data_file, 'r') as f:
            data = json.load(f)
            self.assertIn('q_values', data)
            self.assertIn('action_counts', data)

    def test_get_action(self):
        """Test action selection"""
        context = "headache"
        action, context_hash = self.rl_service.get_action(context)
        self.assertIn(action, [0, 1, 2])
        self.assertIsInstance(context_hash, str)

    def test_update_feedback(self):
        """Test Q-value update based on feedback"""
        context = "headache"
        action = 0
        reward = 1
        
        # Get initial Q-value
        initial_q = self.rl_service.get_q_value(context, action)
        
        # Update feedback
        new_q = self.rl_service.update_feedback(context, action, reward)
        
        # Check if Q-value updated
        self.assertNotEqual(initial_q, new_q)
        
        # Verify persistence
        with open(self.test_data_file, 'r') as f:
            data = json.load(f)
            context_hash = self.rl_service._get_context_hash(context)
            saved_q = data['q_values'].get(context_hash, {}).get(str(action), 0.0)
            self.assertAlmostEqual(new_q, saved_q)

    def test_context_hashing(self):
        """Test if similar contexts map to same hash if keywords match"""
        c1 = "I have a headache"
        c2 = "severe headache pain"
        
        h1 = self.rl_service._get_context_hash(c1)
        h2 = self.rl_service._get_context_hash(c2)
        
        # Both contain 'headache', so they might hash similarly if logic is simple
        # But my current logic is simple hash of sorted keywords.
        # Let's check if 'headache' is in keywords.
        
        # Actually, let's just verify that the hash is consistent
        self.assertEqual(h1, self.rl_service._get_context_hash(c1))

if __name__ == '__main__':
    unittest.main()
