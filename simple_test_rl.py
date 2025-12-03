from rl_service import RLService
import os

try:
    rl = RLService(data_file='test_rl_simple.json')
    print("Init OK")
    
    action, ctx = rl.get_action("headache")
    print(f"Action: {action}, Context: {ctx}")
    
    new_q = rl.update_feedback("headache", action, 1)
    print(f"New Q: {new_q}")
    
    if os.path.exists('test_rl_simple.json'):
        os.remove('test_rl_simple.json')
        print("Cleanup OK")
        
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
