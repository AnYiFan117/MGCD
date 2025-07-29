# faiss

METADATA_PATH = "./faiss/metadata.pkl"
THRESHOLD = 0.4
INDEX_PATH = "./faiss/indexes"
TOP_K = 500
NPROBE = 3
RESULT_PATH = f"./faiss/nprobe{NPROBE}-k{TOP_K}-result.csv"

# filter
USE_FILTER = False

# main
JSON_PATH = "./tmp/json"
# TODO: 请添加自己的数据集路径
DATABASE_PATH = "./data/dataset/"+"your_dataset_name"

# file_similarity
FILE_SIMILARITY_PATH = "./data/file-level/file-similarity_results.csv"

# block_similarity
BLOCK_SIMILARITY_PATH = "./data/block-level/logs"
BLOCK_METADATA_PATH = "./data/block-level/block_mgcd_metadata.pkl"
# 这里使用的数据集是论文中使用的数据集，如果想要使用自定义的数据集，请根据自定义数据集生成的函数检测结果，自行修改deepseek.py中的处理函数
BLOCK_DATABASE_PATH = "./data/dataset/block_level_database"


# agent
# TODO: 请添加自己的API_KEY和BASE_URL
API_KEY = ""
BASE_URL = ""
MODEL = ""
MODEL_PATH = "./unixcoder-base"
FT_MODEL_PATH = "./ft_model/model.bin"