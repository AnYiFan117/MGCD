import pandas as pd
import torch
import torch.nn as nn
from unixcoder import UniXcoder
import javalang

from pygments.lexers import get_lexer_by_name
from pygments.token import Token
from calculateQ import jisuanshang 
from config.config import MODEL_PATH, FT_MODEL_PATH
import chardet

"""
将文件中的函数转化为向量，并存入milvus中
"""

model, device = None, None

def read_csv():
    """
    读取Vr得到的文件对结果
    :return: dataframe
    """
    df = pd.read_csv("Vr_result.csv")
    return df


def flatten_list(nested_list):
    flattened_list = []
    for i in nested_list:
        if isinstance(i, list):
            flattened_list.extend(flatten_list(i))
        else:
            flattened_list.append(i)
    return flattened_list

def get_startlines(tree):
    startlines, temp = [], []
    for i in range(len(tree.types)):
        for item in tree.types[i].body:
            try:
                if jisuanshang(item):
                    continue
            except Exception as e:
                # 有错误说明不应该被过滤
                pass
            res = find(item)
            if res is not None:
                temp.append(res)
    startlines = flatten_list(temp)
    return startlines

def find(item):
    data = []
    if isinstance(item, javalang.tree.ClassDeclaration):
        for body in item.body:
            res = find(body)
            if res is not None:
                data.append(res)
        return data
    elif isinstance(item, javalang.tree.FieldDeclaration):
        if item.declarators is not None:
            for declarator in item.declarators:
                if declarator.initializer is not None and isinstance(declarator.initializer, javalang.tree.ClassCreator):
                    if declarator.initializer.body is not None:
                        for body in declarator.initializer.body:
                            res = find(body)
                            if res is not None:
                                data.append(res)
        return data
    elif isinstance(item, javalang.tree.ReturnStatement):
        if item.expression is not None and isinstance(item.expression, javalang.tree.ClassCreator):
            if item.expression.body is not None:
                for body in item.expression.body:
                    res = find(body)
                    if res is not None:
                        data.append(res)
        return data
    elif isinstance(item, javalang.tree.MethodDeclaration) or isinstance(item, javalang.tree.ConstructorDeclaration):
        # 遍历body，寻找classcreater项
        if item.body is not None:
            data.append(item.position.line)
            for exp in item.body:
                if hasattr(exp, "expression") and isinstance(exp.expression, javalang.tree.MethodInvocation):
                    for arg in exp.expression.arguments:
                        if isinstance(arg, javalang.tree.ClassCreator) and arg.body is not None:
                            for body in arg.body:
                                res = find(body)
                                if res is not None:
                                    data.append(res)
        # 先不filter
            # if ffilter(item):
            #     return None
            # else:
        return data
    else:
        return None

def find_function_end(java_code, start_line):
    lexer = get_lexer_by_name("java")
    tokens = lexer.get_tokens(java_code)

    brace_count = 0
    function_start_line = None
    current_line = start_line  # 从第一行开始
    lines = java_code.split('\n')
    code_lines = lines[start_line - 1:]

    for line in code_lines:
        line_tokens = list(lexer.get_tokens(line))
        for token_type, token_value in line_tokens:
            if token_type == Token.Punctuation and token_value == "{":
                # 处理花括号，增加计数器
                brace_count += 1
            elif token_type == Token.Punctuation and token_value == "}":
                # 处理花括号，减少计数器
                brace_count -= 1
                if brace_count == 0:
                    # 函数结束
                    return current_line
        current_line += 1
    return None


def extract_functions(java_file, startlines, endlines):
    func_list = []
    length_list = []

    for start, end in zip(startlines, endlines):
        function_text = extract_function_text(java_file, start, end)
        func_list.append(function_text)
        length_list.append(end-start+1)

    return func_list, length_list

def extract_function_text(java_file, start, end):

    with open(java_file, 'rb') as fb:
        encode = chardet.detect(fb.read())['encoding']
        if encode not in ['Shift-JIS', 'SHIFT_JIS']:
            encode = 'utf-8'

    with open(java_file, 'r', encoding=encode) as file:
        lines = file.readlines()

    function_lines = lines[start - 1:end]  # Assuming line numbers start from 1
    function_text = ''.join(function_lines)
    function_text = function_text.replace("    ","")
    
    return function_text


def init():
    """
    初始化模型
    :return:
    """
    global model, device
    device = torch.device("cuda")
    model = UniXcoder(MODEL_PATH, FT_MODEL_PATH)
    model.to(device)

def func2vector(content):   
    """
    将函数内容转化为vector返回
    :param content: 函数内容
    :return: 一个向量
    """
    tokens_ids = model.tokenize([content], max_length=512, mode="<encoder-only>")
    source_ids = torch.tensor(tokens_ids).to(device)
    _, embeddings = model(source_ids)
    x = nn.functional.normalize(embeddings, p=2, dim=1)
    # x = embeddings
    return x


