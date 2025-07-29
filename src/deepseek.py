import os, time
from agent import DeepseekAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from config.config import RESULT_PATH, BLOCK_DATABASE_PATH


# TODO: 如果使用自定义的数据集，请根据自定义数据集生成的函数检测结果，自行修改get_files_list函数
def get_files_list() -> set:
    files = set()
    with open(RESULT_PATH, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 8:
                files.add(row[1])
                files.add(row[5])
            else:
                files.add(row[0])
                files.add(row[1])
        print("number of files", len(files))
        return files 


def process_file(path, filename):
    agent = DeepseekAgent(path=path, filename=filename)
    if agent.prepare_prompt():
        # 成功调整prompt
        if agent.call_deepseek():
            # 成功调用deepseek
            agent.parse_result()

def main():
    
    files = get_files_list()
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor: 
        futures = []
        for file in files:
            if file.endswith(".java"):
                # TODO: 如果使用自定义的数据集，请自行修改这里的文件路径
                path = os.path.join(BLOCK_DATABASE_PATH, file)
                futures.append(executor.submit(process_file, path, file))
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(e)
            
                    
    end = time.time()
    print("Time: ", end - start)

if __name__ == "__main__":
    main()