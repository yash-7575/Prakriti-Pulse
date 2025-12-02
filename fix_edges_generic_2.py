import os
import glob
import re
import csv

edges_dir = 'edges'

def get_relationship_type(filepath):
    # Read first few lines to guess relationship type
    with open(filepath, 'r') as f:
        lines = f.readlines()
        for line in lines[1:10]: # Skip header
            parts = line.split(',')
            if len(parts) >= 3:
                return parts[2]
    return None

def fix_file(filepath):
    rel_type = get_relationship_type(filepath)
    if not rel_type:
        print(f"Could not determine relationship type for {filepath}")
        return

    print(f"Checking {filepath} for duplicate {rel_type}...")
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    fixed = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Count occurrences of relationship type
        if line.count(rel_type) > 1:
            print(f"Found merged line in {filepath} at line {i+1}")
            
            first_idx = line.find(rel_type)
            second_idx = line.find(rel_type, first_idx + len(rel_type))
            
            pre_part = line[:second_idx]
            post_part = line[second_idx:]
            
            c1 = pre_part.rfind(',') # Comma before rel_type
            if c1 == -1: 
                new_lines.append(line)
                continue
            
            c2 = pre_part.rfind(',', 0, c1) # Comma before next_target
            if c2 == -1: 
                new_lines.append(line)
                continue
            
            c3 = pre_part.rfind(',', 0, c2) # Comma before merged field
            
            merged_field = pre_part[c3+1 : c2]
            
            # Try splitting merged_field
            # Pattern: Anything followed by digits at the end
            # We use non-greedy matching for the first part
            match = re.match(r'(.*?)(\d+)$', merged_field)
            
            if match:
                val1 = match.group(1)
                val2 = match.group(2)
                
                # If val1 ends with a quote, it might be a closed quoted field
                # "Action"203 -> "Action", 203
                
                part1 = line[:c3+1] + val1
                part2 = val2 + line[c2:]
                
                new_lines.append(part1)
                new_lines.append(part2)
                fixed = True
            else:
                print(f"Could not split merged field: {merged_field}")
                new_lines.append(line)
        else:
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
