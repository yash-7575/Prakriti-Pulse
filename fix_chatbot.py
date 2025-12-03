
service_path = r'c:\Users\hp\OneDrive\Documents\Prakriti-Pulse\chatbot_service.py'
tail_path = r'c:\Users\hp\OneDrive\Documents\Prakriti-Pulse\chatbot_tail.py'

with open(service_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Keep lines 1 to 535 (indices 0 to 534)
# Line 535 is "            top_indices = np.argsort(similarities)[::-1][:top_k]"
head_lines = lines[:535]

with open(tail_path, 'r', encoding='utf-8') as f:
    tail_content = f.read()

new_content = "".join(head_lines) + "\n" + tail_content

with open(service_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Successfully fixed {service_path}")
