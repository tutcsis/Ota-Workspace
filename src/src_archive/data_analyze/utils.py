import os

# load file from path
def get_file_names(path: str):
  return sorted([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])

def get_file_pathes(path: str):
  return sorted([os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])

def get_folder_names(path: str):
  return sorted([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])
