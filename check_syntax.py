import tokenize

output_lines = []
with open(r'c:\Users\hp\OneDrive\Documents\Prakriti-Pulse\chatbot_service.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if '"""' in line:
            output_lines.append(f"{i+1}: {line.strip()}")

output_lines.append("-" * 20)

with open(r'c:\Users\hp\OneDrive\Documents\Prakriti-Pulse\chatbot_service.py', 'rb') as f:
    try:
        for token in tokenize.tokenize(f.readline):
            pass
        output_lines.append("No syntax errors found by tokenize.")
    except tokenize.TokenError as e:
        output_lines.append(f"TokenError: {e}")
        output_lines.append(f"Location: {e.args[1]}")
    except Exception as e:
        output_lines.append(f"Error: {e}")

with open(r'c:\Users\hp\OneDrive\Documents\Prakriti-Pulse\syntax_report.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))


