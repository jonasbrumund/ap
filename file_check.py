import os

cwd = os.getcwd()
sample_folder = os.path.join(cwd, 'Samples')

subfolder_names = ['audiocommons', 'chroma_analysis', 'pt_analysis']
subfolder_suffixes = ['_analysis', '_chroma', '_pytimbre']

missing_entries = []  # Store all missing info


def check_subdirectories():
    for root, dirs, files in os.walk(sample_folder):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if '__MACOSX' in dir_path:
                continue

            wav_files = [f for f in os.listdir(dir_path) if f.endswith('.wav')]
            wav_stems = [os.path.splitext(f)[0] for f in wav_files]

            if wav_files:
                for subfolder, suffix in zip(subfolder_names, subfolder_suffixes):
                    subfolder_path = os.path.join(dir_path, subfolder)

                    if not os.path.exists(subfolder_path):
                        entry = f"Subfolder '{subfolder}' does not exist in '{dir_path}'"
                        print(entry)
                        missing_entries.append(entry)
                        continue

                    existing_jsons = [os.path.splitext(f)[0] for f in os.listdir(subfolder_path) if f.endswith('.json')]

                    for stem in wav_stems:
                        expected_json = f"{stem}{suffix}"
                        if expected_json not in existing_jsons:
                            entry = f"Missing '{expected_json}.json' in '{subfolder_path}' for '{stem}.wav'"
                            print(entry)
                            missing_entries.append(entry)


check_subdirectories()

# Write missing entries to log file
log_file = os.path.join(cwd, 'missing_files.log')
with open(log_file, 'w') as f:
    for entry in missing_entries:
        f.write(entry + '\n')

print(f"\nMissing files log saved to: {log_file}")
