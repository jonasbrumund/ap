import pandas as pd
import os

csv_path = os.path.join(os.getcwd(), 'ap', 'samples_data.csv')

# add a idx column at the beginning of dataframe
def add_idx_column(csv_path):
    # Load the existing CSV file
    df = pd.read_csv(csv_path)

    # Check if 'idx' column already exists
    if 'idx' in df.columns:
        print("Column 'idx' already exists. No changes made.")
        return

    # Create a new 'idx' column with sequential numbers starting from 0
    df.insert(0, 'idx', range(len(df)))

    print(df.head())  # Display the first few rows of the modified DataFrame

    # Save the modified DataFrame back to the CSV file
    df.to_csv(csv_path, index=False)
    print(f"'idx' column added to {csv_path}.")

add_idx_column(csv_path)