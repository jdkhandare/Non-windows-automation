import os

current_script_path = os.path.abspath(__file__)

# Get the directory path of the current script
current_directory = os.path.dirname(current_script_path)
filename = 'atirwraplinux.sh'  # Replace 'example.txt' with your desired file name
file_path = os.path.join(current_directory, filename)

# Use the file_path as needed
print("Path of the file in the same directory:", file_path)
