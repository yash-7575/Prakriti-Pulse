import csv
import os

input_path = 'nodes/guna.csv'
output_path = 'nodes/guna_fixed.csv'

def fix_guna():
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r') as fin, open(output_path, 'w', newline='') as fout:
        lines = fin.readlines()
        
        # Header
        if lines:
            fout.write(lines[0])
        
        fixed_count = 0
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split(',')
            if len(parts) > 3:
                # id, name, desc_part1, desc_part2...
                node_id = parts[0]
                name = parts[1]
                # Reconstruct description with commas
                desc = ",".join(parts[2:])
                # Quote description
                # Escape existing quotes if any (though unlikely here)
                desc = desc.replace('"', '""')
                new_line = f'{node_id},{name},"{desc}"\n'
                fout.write(new_line)
                fixed_count += 1
            else:
                fout.write(line + '\n')
                
    print(f"Fixed {fixed_count} rows.")
    print(f"Fixed file written to {output_path}")

if __name__ == "__main__":
    fix_guna()
