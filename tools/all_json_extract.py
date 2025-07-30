# This script extracts JSON data from the all_jsonfiles file into
# subfolders in the Samples folder, creating JSON files for each
# subfolder (audiocommons, chroma_analysis, pt_analysis) based on the
# structure of the all_jsonfiles file. It handles special cases for
# atmospheric samples and ensures that the JSON files are created
# correctly with the necessary content.

import os

cwd = os.getcwd()
all_json = open(os.path.join(cwd, 'Samples/all_jsonfiles'))
all_jsonfiles = all_json.readlines()

sample_folder = os.path.join(cwd, 'Samples')


def atmos_check(folders):
    atmos_folders = ['ReAtmos', 'Sweepa', 'SynAtmos', 'Textures']
    if folders[0] in atmos_folders:
        # add missing folder at the beginning of folders list
        folders.insert(0, 'musicradar-atmospheric-samples-2')
        return folders


def extract_jsons(line, idx, period=True):
    line = line.strip()
    folders = line.split('/')
    if '/' not in line:
        print(f'Skipping {line} as it does not contain any subfolders.')
        return

    # pop last element in folder until it contains '.json'
    while folders and '.json' not in folders[-1]:
        folders.pop()
    # get filename
    filename = folders[-1]
    filename = filename.split('.json')[0]
    # remove first and last element of folders list
    if period:
        folders = folders[1:-1]
    if not period:
        folders = folders[:-1]

    atmos_check(folders)

    # create folder path
    folder_path = os.path.join(*folders[:-1])
    # create musicradar_copy list (musicradar_copy1 - musicradar_copy22)
    musicradar_copy = ['musicradar_copy' + str(i + 1) for i in range(22)]

    print(f'Processing {filename} in {folder_path}')

    # check if json file already exists in sample_folder
    for mrcopy in musicradar_copy:
        if os.path.exists(os.path.join(sample_folder, mrcopy, folders[0], '__MACOSX')):
            filepath = os.path.join(sample_folder, mrcopy, folders[0], folder_path)
        else:
            filepath = os.path.join(sample_folder, mrcopy, folder_path)

        if os.path.exists(filepath):
            # check if the file already exists
            if os.path.exists(os.path.join(filepath, folders[-1], filename + '.json')):
                print(f'File {filename}.json already exists in {mrcopy}, skipping...')
                continue

            else:
                if folders[-1] == 'audiocommons':
                    # check if in range idx +1 to idx + 31 there is a line that contains ./
                    if any('./' in all_jsonfiles[j] for j in range(idx + 1, idx + 31)):
                        # extract json file into directory
                        json_content = []
                        for j in range(idx + 1, idx + 31):
                            line = all_jsonfiles[j].strip()
                            if line:
                                json_content.append(line)
                    else:
                        # if no line contains ./, skip this file
                        print(f'Skipping {filename} as no valid JSON content found.')
                        return

                    # tab in the beginning of each line
                    json_content = [f'\t{line}' for line in json_content]

                    # create one line at the beginning and end for { and }
                    json_content.insert(0, '{')
                    json_content.append('}')

                    # write json_content to file and create directories if they don't exist
                    save_path = os.path.join(filepath, folders[-1], filename + '.json')
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    # save_path = os.path.join(sample_folder, json_path, filename + '.json')
                    with open(save_path, 'w') as f:
                        f.write('\n'.join(json_content))

                elif folders[-1] == 'chroma_analysis' or folders[-1] == 'pt_analysis':
                    # check for { and } in the line
                    if '{' in line and '}' in line:
                        # extract the data from { to }
                        start = line.index('{')
                        end = line.index('}')
                        json_content = line[start:end + 1]
                        json_content = [json_content]

                        # write json_content to file and create directories if they don't exist
                        save_path = os.path.join(filepath, folders[-1], filename + '.json')
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        # save_path = os.path.join(sample_folder, json_path, filename + '.json')
                        with open(save_path, 'w') as f:
                            f.write('\n'.join(json_content))


# go though all_jsonfiles and stop when there is ./ in the line
for idx, line in enumerate(all_jsonfiles):

    if 2087996 < idx < 2124225:

        line = line.strip()
        if './' not in line:
            continue

        # check if there are multipple ./ in the line
        if line.count('./') > 1:
            # split the line by ./ and remove the first element
            parts = line.split('./')[1:]
            # remove empty strings from parts
            parts = [part.strip() for part in parts if part.strip()]
            # check if each part contains '.json'. If it does, check if it
            # also contains '{'. If it does not, check if following part
            # does not contain '.json' but does contain '{' and merge them.
            for i, part in enumerate(parts):
                if '.json' in part and '{' in part:
                    extract_jsons(part, idx=idx, period=False)
                elif '.json' in part and '{' not in part:
                    # check if the next part contains '{' and combine them
                    if i + 1 < len(parts) and '{' in parts[i + 1]:
                        combined_part = part + ' ' + parts[i + 1]
                        extract_jsons(combined_part, idx=idx, period=False)
                elif '.json' not in part and '{' not in part:
                    # if the part does not contain '.json' or '{', skip it
                    continue
        else:
            extract_jsons(line, idx=idx)
