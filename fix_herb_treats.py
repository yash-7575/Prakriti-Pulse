import os

input_path = 'edges/herb_treats_condition.csv'
output_path = 'edges/herb_treats_condition_fixed.csv'

def fix_herb_treats():
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r') as fin, open(output_path, 'w', newline='') as fout:
        lines = fin.readlines()
        
        fixed_count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Fix merged line 345 (index 344)
            if '""203,6' in line:
                # Split at ""203
                parts = line.split('""203')
                if len(parts) == 2:
                    part1 = parts[0] + '"'
                    part2 = '203' + parts[1]
                    
                    fout.write(part1 + '\n')
                    
                    # Clean up part2
                    # Replace \" with "
                    part2 = part2.replace('\\"', '"')
                    
                    # If it ends with "", replace with "
                    if part2.endswith('""'):
                        part2 = part2[:-1]
                        
                    fout.write(part2 + '\n')
                    fixed_count += 1
                    continue
            
            # Fix fully quoted lines (approx lines 346-353)
            if line.startswith('"') and line.endswith('"') and ',' in line:
                content = line[1:-1]
                if content and content[0].isdigit():
                     content = content.replace('\\"', '"').replace('""', '"')
                     fout.write(content + '\n')
                     fixed_count += 1
                     continue

            # Also check for lines with \" that are not fully quoted (like the one we just fixed might have been if we didn't catch it)
            if '\\"' in line:
                 line = line.replace('\\"', '"')
                 if line.endswith('""'):
                     line = line[:-1]
            
            fout.write(line + '\n')

    print(f"Fixed rows and written to {output_path}")

if __name__ == "__main__":
    fix_herb_treats()
