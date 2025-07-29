import csv
from collections import defaultdict
import time
from config.config import RESULT_PATH, FILE_SIMILARITY_PATH

def process_clone_data(input_lines):
    # 存储所有唯一的函数和它们的信息
    all_funcs = set()
    func_info = {}  # func: {file, lines}
    
    # 克隆行数统计 A到B和B到A
    a_to_b = defaultdict(lambda: defaultdict(int))
    b_to_a = defaultdict(lambda: defaultdict(int))
    
    for line in input_lines:
        parts = line.strip().split(',')
        if len(parts) < 8:
            continue
        
        # 解析两个函数的信息
        try:
            file1 = parts[1]
            start1 = int(parts[2])
            end1 = int(parts[3])
            func1 = (file1, start1, end1)
            
            file2 = parts[5]
            start2 = int(parts[6])
            end2 = int(parts[7])
            func2 = (file2, start2, end2)
        except:
            continue
        
        # 跳过自我克隆
        if func1 == func2:
            continue
        
        # 记录函数信息
        for func in [func1, func2]:
            if func not in all_funcs:
                all_funcs.add(func)
                lines = func[2] - func[1] + 1
                func_info[func] = {
                    'file': func[0],
                    'lines': lines
                }
        
        # 更新克隆行数统计
        lines1 = func_info[func1]['lines']
        a_to_b[file1][file2] += lines1
        
        lines2 = func_info[func2]['lines']
        b_to_a[file2][file1] += lines2
    
    # 计算每个文件的总行数
    file_lines = defaultdict(int)
    for func in all_funcs:
        file = func_info[func]['file']
        file_lines[file] += func_info[func]['lines']
    
    return a_to_b, b_to_a, file_lines

def calculate_similarity(a_to_b, b_to_a, file_lines):
    # 收集所有文件
    all_files = set(file_lines.keys())
    
    # 存储结果：result[A][B] = (A到B相似度, B到A相似度)
    result = defaultdict(dict)
    
    for A in all_files:
        # 获取所有相关文件B
        related_B = set(a_to_b.get(A, {}).keys())
        # 添加B到A有克隆关系的文件
        for B in all_files:
            if A in b_to_a.get(B, {}):
                related_B.add(B)
        
        for B in related_B:
            if A == B:
                continue  # 跳过自身
            
            # 计算A到B的相似度
            a_to_b_clone = a_to_b.get(A, {}).get(B, 0)
            total_A = file_lines.get(A, 1)  # 避免除零
            similarity_A_to_B = a_to_b_clone / total_A if total_A != 0 else 0.0
            
            # 计算B到A的相似度
            b_to_a_clone = b_to_a.get(B, {}).get(A, 0)
            total_B = file_lines.get(B, 1)
            similarity_B_to_A = b_to_a_clone / total_B if total_B != 0 else 0.0
            
            result[A][B] = (similarity_A_to_B, similarity_B_to_A)
    
    return result


def main():    
    # 实际使用时从文件读取
    with open(RESULT_PATH, 'r') as f:
        input_data = f.readlines()
    
    start = time.time()
    print("processing data")
    a_to_b, b_to_a, file_lines = process_clone_data(input_data)
    print("calculating similarity")
    similarity_result = calculate_similarity(a_to_b, b_to_a, file_lines)
    end = time.time()
    print(f"Time taken: {end - start} seconds")
    # 输出结果到CSV
    with open(FILE_SIMILARITY_PATH, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['FileA', 'FileB', 'SimilarityAtoB', 'SimilarityBtoA']) 
        
        for fileA in similarity_result:
            for fileB in similarity_result[fileA]:
                sim_ab, sim_ba = similarity_result[fileA][fileB]
                # 完全文件相似的情况
                if sim_ab == 1 and sim_ba == 1:
                    writer.writerow([fileA, fileB, f"{sim_ab:.4f}", f"{sim_ba:.4f}"])

if __name__ == "__main__":
    main()