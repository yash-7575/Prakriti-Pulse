import csv
import os

input_path = 'nodes/symptoms.csv'
output_path = 'nodes/symptoms_fixed.csv'

doshas = {'Vata', 'Pitta', 'Kapha'}
severities = {'Low', 'Medium', 'High'}

def fix_symptoms():
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r') as fin, open(output_path, 'w', newline='') as fout:
        reader = csv.reader(fin)
        writer = csv.writer(fout)
        
        try:
            header = next(reader)
            writer.writerow(header)
        except StopIteration:
            print("Empty file")
            return

        fixed_count = 0
        for row in reader:
            # Check for split dosha (row[3] and row[4] are doshas)
            if len(row) >= 5 and row[3].strip() in doshas and row[4].strip() in doshas:
                combined_dosha = f"{row[3].strip()},{row[4].strip()}"
                
                if len(row) == 15:
                    # Case 1: Extra column due to split dosha. 
                    # row[5] is likely Body Location.
                    # Merge 3 and 4, keep the rest.
                    new_row = row[:3] + [combined_dosha] + row[5:]
                    writer.writerow(new_row)
                    fixed_count += 1
                elif len(row) == 14:
                    # Case 2: Split dosha BUT total columns is 14.
                    # This implies a column is MISSING (likely Body Location).
                    # row[5] is likely Severity.
                    # Merge 3 and 4, insert "Whole body" (or infer from description?) as Location.
                    # For now, use "Whole body" or "Unspecified".
                    new_row = row[:3] + [combined_dosha, "Unspecified"] + row[5:]
                    writer.writerow(new_row)
                    fixed_count += 1
                else:
                    # Unexpected length with split dosha
                    print(f"Warning: Row {row[0]} has split dosha but unexpected length {len(row)}. Writing as is.")
                    writer.writerow(row)
            else:
                writer.writerow(row)
                
    print(f"Fixed {fixed_count} rows.")
    print(f"Fixed file written to {output_path}")

if __name__ == "__main__":
    fix_symptoms()
