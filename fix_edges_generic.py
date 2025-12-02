import os
import glob
import re

edges_dir = 'edges'

def fix_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    fixed = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Check for merge pattern: "" followed by digit
        match = re.search(r'""("?\d+)', line)
        if match:
            print(f"Found merged line in {filepath} at line {i+1}")
            split_idx = match.start()
            
            part1 = line[:split_idx] + '"'
            part2 = line[split_idx+2:] # Skip the ""
            
            # Check if part2 needs a starting quote
            # If it starts with digits and is followed by a quote, it likely lost its starting quote
            if part2 and part2[0].isdigit():
                first_non_digit_idx = next((k for k, c in enumerate(part2) if not c.isdigit()), None)
                if first_non_digit_idx is not None and part2[first_non_digit_idx] == '"':
                    part2 = '"' + part2
            
            # Clean up part2 end
            if part2.endswith('""'):
                part2 = part2[:-1]
            
            # Also handle escaped quotes \" if present (artifact from previous bad fixes or original corruption)
            if '\\"' in part2:
                part2 = part2.replace('\\"', '"')
                if part2.endswith('""'): # Re-check end after replacement
                    part2 = part2[:-1]

            new_lines.append(part1)
            new_lines.append(part2)
            fixed = True
        else:
            # Also check for fully quoted lines that might be artifacts (like in herb_treats)
            # "203,16,..."
            if line.startswith('"') and line.endswith('"') and ',' in line:
                 content = line[1:-1]
                 if content and content[0].isdigit():
                      # It's likely a quoted row
                      content = content.replace('\\"', '"').replace('""', '"')
                      new_lines.append(content)
                      fixed = True
                      continue
            
            new_lines.append(line)
            
    if fixed:
        print(f"Writing fixed content to {filepath}")
        with open(filepath, 'w', newline='') as f:
            for line in new_lines:
                f.write(line + '\n')

if __name__ == "__main__":
    if not os.path.exists(edges_dir):
        print(f"Directory {edges_dir} not found.")
    else:
        for filename in glob.glob(os.path.join(edges_dir, '*.csv')):
            fix_file(filename)
