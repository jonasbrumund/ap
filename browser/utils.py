import os
import pandas as pd


def json_extract(path, stem, suffix, dir_path):
    with open(path, 'r') as f:

        if suffix == '_analysis':
            data = f.read()
            data = data.replace('\t', ' ')  # Replace tabs with spaces
            data = data.replace(' ', '')  # Remove all spaces
            data = data.replace('\n', '')  # Remove newlines
            data = data.replace('}{', '},{')  # Ensure proper JSON format
            data = f'[{data}]'  # Wrap in square brackets to form a valid JSON array
            json_data = pd.read_json(data)
            # add stem name at the beggining of the DataFrame
            json_data.insert(0, 'stem', stem)
            # add directory to the DataFrame
            dir = dir_path.split('/')
            # remove first 5 elements from dir
            dir = dir[5:]
            json_data.insert(1, 'dir', [dir])

        else:
            data = f.read()
            data = f'[{data}]'  # Wrap in square brackets to form a valid JSON array
            json_data = pd.read_json(data)
            # add stem name at the beggining of the DataFrame
            json_data.insert(0, 'stem', stem)

    return json_data


def check_subdirectories():

    cwd = os.getcwd()
    sample_folder = os.path.join(cwd, 'Samples')

    subfolder_names = ['audiocommons', 'chroma_analysis', 'pt_analysis']
    subfolder_suffixes = ['_analysis', '_chroma', '_pytimbre']

    # create musicradar_copy list (musicradar_copy1 - musicradar_copy22)
    musicradar_copy = ['musicradar_copy' + str(i + 1) for i in range(22)]

    for mrcopy in musicradar_copy:
        copy_path = os.path.join(sample_folder, mrcopy)
        if not os.path.exists(copy_path):
            continue

        for root, dirs, files in os.walk(copy_path):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if '__MACOSX' in dir_path:
                    continue

                wav_files = [f for f in os.listdir(dir_path) if f.endswith('.wav')]
                wav_stems = [os.path.splitext(f)[0] for f in wav_files]

                if wav_files:

                    audiocommons_files = []
                    chroma_files = []
                    pt_analysis_files = []
                    missing_entries = []

                    for subfolder, suffix in zip(subfolder_names, subfolder_suffixes):
                        subfolder_path = os.path.join(dir_path, subfolder)

                        if not os.path.exists(subfolder_path):
                            entry = f"Subfolder '{subfolder}' does not exist in '{dir_path}'"
                            print(entry)
                            continue

                        existing_jsons = [os.path.splitext(f)[0] for f in os.listdir(subfolder_path) if f.endswith('.json')]

                        for stem in wav_stems:
                            expected_json = f"{stem}{suffix}"
                            if expected_json not in existing_jsons:
                                missing_entries.append(stem)
                            elif suffix == '_analysis':
                                audiocommons_files.append(stem)
                            elif suffix == '_chroma':
                                chroma_files.append(stem)
                            elif suffix == '_pytimbre':
                                pt_analysis_files.append(stem)

                    # delete all stems from the lists that are in missing_entries
                    audiocommons_files = [stem for stem in audiocommons_files if stem not in missing_entries]
                    chroma_files = [stem for stem in chroma_files if stem not in missing_entries]
                    pt_analysis_files = [stem for stem in pt_analysis_files if stem not in missing_entries]

                    # check if all three lists contain the same stems
                    res = set(audiocommons_files) == set(chroma_files) == set(pt_analysis_files)
                    if res:
                        stems = audiocommons_files

                    # save turn the existing json files into a DataFrame
                    audiocommons_data = []
                    chroma_data = []
                    pt_analysis_data = []
                    for suffix in subfolder_suffixes:
                        if suffix == '_analysis':
                            folder_path = os.path.join(dir_path, 'audiocommons')
                            for stem in stems:
                                json_file = f"{stem}{suffix}.json"
                                json_path = os.path.join(folder_path, json_file)
                                audiocommons_data.append(json_extract(json_path, stem, suffix, dir_path))
                        elif suffix == '_chroma':
                            folder_path = os.path.join(dir_path, 'chroma_analysis')
                            for stem in stems:
                                json_file = f"{stem}{suffix}.json"
                                json_path = os.path.join(folder_path, json_file)
                                chroma_data.append(json_extract(json_path, stem, suffix, dir_path))
                        elif suffix == '_pytimbre':
                            folder_path = os.path.join(dir_path, 'pt_analysis')
                            for stem in stems:
                                json_file = f"{stem}{suffix}.json"
                                json_path = os.path.join(folder_path, json_file)
                                pt_analysis_data.append(json_extract(json_path, stem, suffix, dir_path))

                    # check if any of the lists are empty
                    if not audiocommons_data or not chroma_data or not pt_analysis_data:
                        print(f"No data found for {dir_name} in {mrcopy}. Skipping...")
                        continue

                    # concatenate all DataFrames into one
                    audiocommons_df = pd.concat(audiocommons_data, ignore_index=True)
                    chroma_df = pd.concat(chroma_data, ignore_index=True)
                    pt_analysis_df = pd.concat(pt_analysis_data, ignore_index=True)

                    # save the DataFrame to a CSV file
                    csv_path = os.path.join(cwd, 'ap')
                    # csv_path = os.path.join(csv_path, 'audiocommons_data.csv')


                    # chek if dataframe exists to add header at the top
                    if not os.path.exists(os.path.join(csv_path, 'audiocommons_data.csv')):
                        audiocommons_df.to_csv(os.path.join(csv_path, 'audiocommons_data.csv'), mode='w', header=True, index=False)
                        chroma_df.to_csv(os.path.join(csv_path, 'chroma_data.csv'), mode='w', header=True, index=False)
                        pt_analysis_df.to_csv(os.path.join(csv_path, 'pytimbre_data.csv'), mode='w', header=True, index=False)
                    else:
                        # append to dataframe
                        audiocommons_df.to_csv(os.path.join(csv_path, 'audiocommons_data.csv'), mode='a', header=False, index=False)
                        chroma_df.to_csv(os.path.join(csv_path, 'chroma_data.csv'), mode='a', header=False, index=False)
                        pt_analysis_df.to_csv(os.path.join(csv_path, 'pytimbre_data.csv'), mode='a', header=False, index=False)



