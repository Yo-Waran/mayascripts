######GO TO HOT KEYEDITOR AND PASTE THIS IN RUN TIME COMMAND EDITOR AND SET A HOTKEY#########

"""Auotmatically Run the Latest Saved VSCode file from its directory"""

import os
import glob

# Replace with the directory where your VSCode Maya files are located
vscode_workspace_dir = '/Users/ramyogeshwaran/Documents/Yogi/GitHub Repo/mayascripts'

# Get a list of all files in the workspace directory
files = glob.glob(os.path.join(vscode_workspace_dir, '*'))

if files:
    # Get the latest saved file in the workspace directory
    latest_file = max(files, key=os.path.getctime)
    
    
    print('Latest file path  : ' + latest_file)
else:
    print('No files found ')

#run the latest saved file

try:
    # Retrieve the stored file path from Houdini's session variable
    external_script_path = latest_file
    
    # Check if the path is not empty
    if external_script_path:
        # Open and execute the script
        with open(external_script_path, "r") as file:
            exec(file.read())
    else:
        print("No file path stored.")
except AttributeError:
    print("No file path stored. Please use the 'Store File Path' tool first.")