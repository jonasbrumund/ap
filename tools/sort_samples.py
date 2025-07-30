# This script copies all .wav files from a sample folder to
# a destination folder, preserving the directory structure.

import os

cwd = os.getcwd()

name = 'Insert Sample Folder Name Here'  # e.g. 'Dubstep kit 01 140bpm'
sample_folder = os.path.join('Insert Downloads Folder', name)

copy = 'musicradar_copy2'
destination_folder = os.path.join(cwd, 'Samples', copy, name)


# go through each folder in sample folder and copy to same subfolder
# in destination folder
def copy_samples(src, dest):
    if not os.path.exists(dest):
        os.makedirs(dest)
    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dest_item = os.path.join(dest, item)
        if os.path.isdir(src_item):
            copy_samples(src_item, dest_item)
        else:
            if item.endswith('.wav'):
                print(f'Copying {src_item} to {dest_item}')
                os.system(f'cp "{src_item}" "{dest_item}"')


copy_samples(sample_folder, destination_folder)
