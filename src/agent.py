import re
from openai import OpenAI
from config.config import API_KEY, BASE_URL, MODEL, BLOCK_SIMILARITY_PATH
class DeepseekAgent:
    """first, call the prepare_prompt() function to prepare the prompt.
    then call the call_deepseek() function to call the deepseek API.
    """
    
    def __init__(self, path:str, filename:str):
        self.path = path
        self.filename = filename
        self.sys_prompt = """# 背景：
在代码中，每一个段代码都有固定的语义信息。如何将代码根据语义信息进行分段，是一个重要的任务。
# 任务：
你现在的任务是，对于输入的一段代码，你需要将他按照语义切分为一系列的代码段，将他们输出。
注意事项：
- 切分的代码段应该具备独立且完整的语义信息，你不需要将他们切分地过于细小。
- 如果你切分出的代码段有多个，请使用---将他们分割开
# 你接受的输入有：
- 一段代码
# 你需要给出的输出有：
<切分的代码段>
"""
        self.user_prompt = """
```java
<code>
```
"""
        self.client = OpenAI(
            api_key = API_KEY,
            base_url = BASE_URL,
        )
        self.result = ""

    def prepare_prompt(self) -> bool:
        print("----- prepare prompt -----")
        # 修改user_prompt
        # 首先获取filename中的所有内容
        try:
            with open(f"{self.path}") as file:
                code = file.read()
            # 将prompt中的<filename>替换为filename
            self.user_prompt = self.user_prompt.replace("<code>", code)
            # print(self.user_prompt)
            return True
        except Exception as e:
            print("----- prepare prompt error -----")
            print(e)
            return False
        
    
    
    def call_deepseek(self) -> bool:
        print("----- standard request -----")
        try:
            completion = self.client.chat.completions.create(
                model = MODEL,  # your model endpoint ID
                messages = [
                    {"role": "system", "content": f"{self.sys_prompt}"},
                    {"role": "user", "content": f"{self.user_prompt}"},
                ],
                temperature=0.0,
            )
            self.result = completion.choices[0].message.content
            return True
        except Exception as e:
            print("----- standard request error -----")
            print(e)
            return False
        
    def parse_result(self) -> bool:
        print("----- parse result -----")
        try:
            result_filename = f"DeepseekR1-{self.filename}.log"
            result = f"========================\n{self.result}\n"
            with open(f"{BLOCK_SIMILARITY_PATH}/{result_filename}", "a") as file:   
                file.write(result)
            print("----- parse result success -----")
            print(f"check result in {result_filename}")
            return True
        except Exception as e:
            print("----- parse result error -----")
            print(e)
            return False