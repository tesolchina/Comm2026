import pandas as pd
import os

# Define paths
input_file = '/Users/simonwang/Documents/Usage/ZhouWorkshop/Comm2026/demo/lab1/input/AI_mental_health.csv'
output_dir = '/Users/simonwang/Documents/Usage/ZhouWorkshop/Comm2026/demo/lab1/output'
output_file = os.path.join(output_dir, 'AI_mental_health_with_wordcount.csv')

# Read the CSV file
df = pd.read_csv(input_file)

# Function to count words in a text
def count_words(text):
    if pd.isna(text) or text == '':
        return 0
    return len(str(text).split())

# Add word count column
df['Word Count'] = df['Abstract'].apply(count_words)

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Save to output folder
df.to_csv(output_file, index=False)

print(f"Successfully added word count column. Output saved to: {output_file}")
print(f"Total rows processed: {len(df)}")


