import os
from typing import List
from config.settings import DART_EXTENSIONS

def get_flutter_project_files(project_path: str) -> List[str]:
    dart_files = []
    
    for root, _, files in os.walk(project_path):
        # Skip hidden directories and build folders
        if any(part.startswith('.') or part == 'build' for part in root.split(os.sep)):
            continue
            
        for file in files:
            if file.endswith(DART_EXTENSIONS):
                dart_files.append(os.path.join(root, file))
    
    return dart_files