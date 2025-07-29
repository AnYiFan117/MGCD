import faiss
import json
import os
import pickle
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import time
import gc
import csv
from config.config import METADATA_PATH, INDEX_PATH, JSON_PATH, THRESHOLD, TOP_K, NPROBE, RESULT_PATH


def get_all_metadata(basepath):
    metadata = []
    for subdir in tqdm(os.listdir(basepath)):
        subdir_path = os.path.join(basepath, subdir)
        if os.path.isdir(subdir_path):
            for file in os.listdir(subdir_path):
                file_path = os.path.join(subdir_path, file)
                if os.path.isfile(file_path):
                    with open(file_path, "r") as f:
                        data = json.load(f)["rows"]
                        metadata.extend([{
                            "vector": item["vector"],
                            "filename": item["filename"].split("/")[-1], 
                            "subdir": item["subdir"],
                            "startline": item["startline"],
                            "endline": item["endline"],
                            } for item in data])
                        
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

def main():

    # # 读取索引
    index = faiss.read_index(INDEX_PATH+"/ivf.faiss")  
    threshold_ivf = THRESHOLD
    batch_size = 10000
    
    vectors = []

    print("reading data")
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    
    print("loading")
    for data in metadata:
        vectors.append(data["vector"])
    
    # 对所有vectors进行批量搜索
    # 添加数据
    vectors_np = np.array(vectors).astype("float32")
    top_ks = [TOP_K]
    for i in top_ks:
        result = []
        top_k = i
        nprobe = NPROBE
        index.nprobe = nprobe
        print("total entries:", index.ntotal)

        start_time = time.time()

        # 批量搜索
        for base in tqdm(range(0, len(vectors), batch_size)):
            batch_vectors = vectors_np[base:base+batch_size]
            D, I = index.search(batch_vectors, top_k)
            for q_idx, (distances, indices) in enumerate(zip(D, I)):
                for i, d in enumerate(distances):
                    if d<=threshold_ivf:
                        hit_idx = indices[i]
                        result.append([metadata[q_idx+base]["subdir"], 
                                    metadata[q_idx+base]["filename"].split("/")[-1], 
                                    metadata[q_idx+base]["startline"], 
                                    metadata[q_idx+base]["endline"], 
                                    metadata[hit_idx]["subdir"], 
                                    metadata[hit_idx]["filename"].split("/")[-1], 
                                    metadata[hit_idx]["startline"], 
                                    metadata[hit_idx]["endline"]])
                    else:
                        break

        end_time = time.time()
        print("nprobe:", index.nprobe, "top_k:", top_k)
        print(f"Time taken: {end_time - start_time} seconds")   
        # 保存结果
        with open(RESULT_PATH, "w") as f:
            writer = csv.writer(f)
            writer.writerows(result)
        gc.collect()


def generate_ifx_index():
    vectors = []
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    for data in metadata:
        vectors.append(data["vector"])
    
    vectors_np = np.array(vectors).astype("float32")
    start = time.time()
    index = faiss.IndexIVFFlat(faiss.IndexFlatL2(768), 768, 894)
    index.train(vectors_np)
    index.add(vectors_np)
    end = time.time()
    print("time: ",end-start)
    faiss.write_index(index, INDEX_PATH+"/ivf.faiss")

def generate_lsh_index():
    vectors = []
    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)
    for data in metadata:
        vectors.append(data["vector"])
    
    vectors_np = np.array(vectors).astype("float32")
    index = faiss.IndexLSH(768, 2 * 768)
    index.train(vectors_np)
    index.add(vectors_np)
    faiss.write_index(index, INDEX_PATH+"/lsh.faiss")


if __name__ == "__main__":
    get_all_metadata(JSON_PATH)
    generate_ifx_index()
    # generate_lsh_index()

    main()
    