import pandas as pd
import os
import ast

# # Replace these with your actual file paths
# file1 = os.path.join(os.getcwd(), 'ap', 'audiocommons_data.csv')
# file2 = os.path.join(os.getcwd(), 'ap', 'chroma_data.csv')
# file3 = os.path.join(os.getcwd(), 'ap', 'pytimbre_data.csv')


# # Read the CSV files
# df1 = pd.read_csv(file1)
# df2 = pd.read_csv(file2)
# df3 = pd.read_csv(file3)

# # Columns to keep only once
# common_cols = ['stem', 'mr_copy', 'dir_name']

# # Drop common columns from second and third DataFrame
# unique_df2 = df2.drop(columns=common_cols, errors='ignore')
# unique_df3 = df3.drop(columns=common_cols, errors='ignore')

# # Concatenate columns side by side
# combined_df = pd.concat([df1, unique_df2, unique_df3], axis=1)

# # Save to new CSV
# combined_df.to_csv(os.path.join(os.getcwd(), 'ap', 'samples_data.csv'), index=False)

# print('Combined CSV saved as combined.csv')


csv_path = os.path.join(os.getcwd(), 'ap', 'samples_data.csv')

df = pd.read_csv(csv_path, low_memory=False)

# change 'dir' column to list
print(df['dir'].head())
df['dir'] = df['dir'].apply(ast.literal_eval)
print(df['dir'].head())

# save the DataFrame to a new CSV file
new_csv_path = os.path.join(os.getcwd(), 'ap', 'samples_data_new.csv')
df.to_csv(new_csv_path, index=False)
print(f"DataFrame saved to {new_csv_path}")
# Check the first few rows of the DataFrame
print(df.head())