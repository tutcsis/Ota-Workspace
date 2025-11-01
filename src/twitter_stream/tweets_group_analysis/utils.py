import os

# load file from path
def get_file_names(path: str):
  return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def get_file_pathes(path: str):
  return [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
