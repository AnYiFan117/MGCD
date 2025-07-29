"""
将待测目录下的文件进行向量化
"""

import os,json,shutil,multiprocessing as mp
from tqdm import tqdm,trange
from prepare_model import init,get_startlines,find_function_end, extract_functions, func2vector
from config.config import USE_FILTER, JSON_PATH, DATABASE_PATH
import javalang

import chardet

import regex as re
import gc

# FILEID全局自增
FILE_ID = 1



def generate_json_for_all_files(path:str):
    """
    数据处理，将待测目录下的文件进行向量化，以便后续保存到数据库
    """

    # 遍历PATH里的所有文件
    for root,dirs,files in os.walk(path): # bcb_reduced/2
        # 遍历path下每一个子文件夹
        for subdir in dirs: # selected
            for root, dirs2, files in os.walk(path+"/"+subdir):
                # 针对每一个文件生成json文件
                # for file in tqdm(files, desc=f"{subdir}:"):
                for file in files:
                    # 获得路径
                    filename = root+"/"+file
                    # 生成文件的json
                    generate_json_for_file(filename, subdir)
                    gc.collect()
                    

            
def generate_json_for_file(filename:str, subdir:str):
    # 打开文件
    data = process_file_with_unixcoder(filename, subdir)
    # 保存文件路径
    savepath = JSON_PATH+"/" +subdir+"/"+ filename.split("/")[-1].split(".")[0] + ".json"
    if data is not None:
        save_to_json(data,savepath)
    else:
        print(f"{filename} has error, data is None")


def process_file_with_unixcoder(filename:str, subdir:str):
    """
    用unixcoder编码单个文件，将文件的函数提取出来

    @param filename: 文件名
    """
    # 打开文件
    try:
        with open(filename, mode='rb') as fb:
            encode = chardet.detect(fb.read())['encoding']
            if encode not in ['Shift-JIS', 'SHIFT_JIS', 'Windows-1252']:
                encode = 'utf-8'
            
            fb.close()

        with open(filename, mode='r', encoding=encode) as f:
                content = f.read()
                # print(f"generating {filename}")
                func_list, file_id, length_list, startline_list, endline_list = file2func(filename, content)
                if func_list is None:
                    return None
                result = [func2vector(func_content).tolist() for func_content in func_list]
                # result = [code2vec(func_content).tolist() for func_content in func_list]
                new_data = {"rows": 
                            [{"id": file_id[i], 
                            "vector": result[i][0], 
                            "filename": filename, 
                            "length": length_list[i],
                            "startline": startline_list[i],
                            "endline": endline_list[i],
                            "subdir": subdir} for i in range(len(file_id))]}
    except Exception as e:
        print(f"Error: {filename} {e}")
        return None
            
        # print(file_id)
    return new_data

def find_function_starts(java_content):
    function_starts = []
    lines = java_content.split('\n')
    in_multiline_comment = False
    for i, line in enumerate(lines):
        # Check for multiline comment
        if '/*' in line:
            in_multiline_comment = True
        if '*/' in line:
            in_multiline_comment = False
            continue
        # Skip commented lines
        if line.strip().startswith('//') or in_multiline_comment:
            continue
        # Search for method/function declaration
        match = re.match(r'\s*(public|private|protected)*\s*(static|final)?\s*(static|final)?\s*[\w<>,\[\]]+\s+(?<!new\s|else\s|do\s)\w+\s*\([^)]*\)[\s\w,]*({)+', line)
        if match:
            function_starts.append(i + 1)  # Line numbers are 1-indexed
    return function_starts


def file2func(filename:str, content:str):
    global FILE_ID
    # 初始化
    func_list = []
    file_id = []
    length_list = []
    
    if USE_FILTER:
        try:
            tree = javalang.parse.parse(content)
        except Exception as e:
            print(f"Error: {filename} {e}")
            return None, [], [], [], []
        temp_startlines = get_startlines(tree)
    else:
        # 获取起始行,no filter
        temp_startlines = find_function_starts(content)

    startlines = []
    endlines = []
    for startline in temp_startlines:
        endline = find_function_end(content, startline)
        if endline is not None: 
            startlines.append(startline)
            endlines.append(endline)
        else:
            print(f"Error: {filename} function endline not found in line {startline}")
    # 读取文件
    func_list, length_list = extract_functions(filename, startlines, endlines)
    # 生成file_id，同时id自增
    for i in range(len(func_list)):
        file_id.append(FILE_ID)
        FILE_ID += 1
    return func_list, file_id, length_list, startlines, endlines

def save_to_json(data:dict, savepath:str):
    """
    将数据保存为json文件，并采取4缩进
    
    @param data: 数据
    @param savepath: 保存路径

    """
    with open(savepath, 'w') as f:
        json.dump(data, f, indent=4)


def save_to_csv(data:list, savepath:str):
    """
    将数据保存为csv文件
    
    @param data: 数据
    @param savepath: 保存路径

    """
    # 保存data为csv文件
    with open(savepath, 'w') as f:
        for key in data:
            f.write(str(key) + "\n")

            
def get_file_length():
    """
    获取文件长度
    """
    fileLength = {}
    for root, dirs, files in os.walk(JSON_PATH):
        for file in files:
            filename = os.path.join(root, file)
            with open(filename, 'r') as f:
                length = 0
                data = json.load(f)
                for item in data["rows"]:
                    length += item["length"]
                fileLength[filename.split("/")[-1].split(".")[0]+".java"] = length
    return fileLength

def clear_json():
    """
    清空json文件夹
    """
    for root, dirs, files in os.walk(JSON_PATH):
        for file in files:
            os.remove(os.path.join(root, file))


if __name__ == "__main__":
    init()
    generate_json_for_all_files(DATABASE_PATH)


