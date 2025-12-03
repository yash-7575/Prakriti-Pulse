import json
import os
import random
import numpy as np
from datetime import datetime

class RLService:
    """
    Reinforcement Learning Service using Contextual Bandits (Epsilon-Greedy).
    Selects between different response strategies (Actions) based on context.
    
    Actions:
    0: RAG Response (Retrieval Augmented Generation)
    1: Rule-based Response (Pattern matching)
    2: Fallback/Default Response
    """
    
    def __init__(self, data_file='rl_data.json', epsilon=0.1):
        self.data_file = data_file
        self.epsilon = epsilon  # Exploration rate
        self.actions = [0, 1, 2]
        self.q_values = {}  # Map context_hash -> [q_val_0, q_val_1, q_val_2]
        self.action_counts = {} # Map context_hash -> [count_0, count_1, count_2]
        self.load_data()

    def load_data(self):
        """Load Q-values from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.q_values = data.get('q_values', {})
                    self.action_counts = data.get('action_counts', {})
                print(f"Loaded RL data with {len(self.q_values)} contexts")
            except Exception as e:
                print(f"Error loading RL data: {e}")
                self.q_values = {}
                self.action_counts = {}
        else:
            print("No existing RL data found, starting fresh")

    def save_data(self):
        """Save Q-values to file"""
        try:
            data = {
                'q_values': self.q_values,
                'action_counts': self.action_counts,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print("RL data saved")
        except Exception as e:
            print(f"Error saving RL data: {e}")

    def _get_context_hash(self, query):
        """
        Create a simple hash of the query to represent context.
        In a real system, this would be a vector clustering or feature hash.
        For simplicity, we'll use the first few words or keywords.
        """
        # Simple keyword extraction
        keywords = [w for w in query.lower().split() if len(w) > 3]
        if not keywords:
            return "general"
        
        # Sort to handle word order invariance
        keywords.sort()
        return "_".join(keywords[:3])

    def get_action(self, query):
        """
        Select an action using Epsilon-Greedy strategy.
        Returns: (action_index, context_hash)
        """
        context = self._get_context_hash(query)
        
        # Initialize if new context
        if context not in self.q_values:
            self.q_values[context] = [0.0, 0.0, 0.0] # Initial Q-values
            self.action_counts[context] = [0, 0, 0]
        
        # Exploration
        if random.random() < self.epsilon:
            return random.choice(self.actions), context
        
        # Exploitation (choose max Q-value)
        q_vals = self.q_values[context]
        # If all equal, choose random
        if all(q == q_vals[0] for q in q_vals):
            return random.choice(self.actions), context
            
        return int(np.argmax(q_vals)), context

    def update_feedback(self, query, action, reward):
        """
        Update Q-values based on user feedback.
        Reward: 1 (Positive), -1 (Negative), 0 (Neutral)
        """
        context = self._get_context_hash(query)
        
        if context not in self.q_values:
            self.q_values[context] = [0.0, 0.0, 0.0]
            self.action_counts[context] = [0, 0, 0]
            
        # Update counts
        self.action_counts[context][action] += 1
        n = self.action_counts[context][action]
        
        # Update Q-value (Incremental Mean)
        # Q_new = Q_old + (Reward - Q_old) / n
        old_q = self.q_values[context][action]
        new_q = old_q + (reward - old_q) / n
        self.q_values[context][action] = new_q
        
        self.save_data()
        return new_q

# Singleton instance
rl_service = RLService()
