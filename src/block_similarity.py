import os
import time
import pickle
from config.config import BLOCK_SIMILARITY_PATH, BLOCK_METADATA_PATH

def load_file(path: str) -> str:
    try:
        with open(path, "r") as f:
            lines = f.read()
        return lines
    except Exception as e:
        print(f"Error loading file {path}: {e}")
        return ""

def main():
    metadata = []
    files = os.listdir(BLOCK_SIMILARITY_PATH)
    for file in files:
        if file.endswith(".log"):
            path = os.path.join(BLOCK_SIMILARITY_PATH, file)
            code = load_file(path)
            # 对code进行切分
            results = code.split("---")
            for result in results:
                metadata.extend([{
                    "code": result,
                    "filename": file
                }])
    with open(BLOCK_METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"Time taken: {end - start} seconds")