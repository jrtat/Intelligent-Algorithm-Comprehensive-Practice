# 如何部署本地大模型


```bash
#--------- 在Windows本地环境（管理员模式） ---------#

pip install modelscope # 下载modelscope

modelscope download --model Qwen/Qwen2.5-3B-Instruct --local_dir ./models/Qwen2.5-3B-Instruct # 把Qwen2.5-3B下载到当前目录的/models/子文件夹里
# 1. 显存大的可以用更大的模型
# 2. 模型保存的地址可以自行更改，默认路径值：C:\Windows\System32\models\Qwen2.5-7B 
# 3. 不用时，模型可以直接在资源管理器删除

```

```bash

#---------在Windows的cmd中--------#

wsl # 进入wsl

wsl --update # 更新 WSL 系统本身

wsl --install -d Ubuntu --web-download # 一次性安装并启用 WSL + 默认下载并安装 Ubuntu 发行版，配置账号和密码，之后进入Ubentu

# 这是因为在Windows环境下没法使用vllm，wsl可以在Windows环境中虚拟一个Linux环境

wsl --status # 如果Window没有开启虚拟化，则上述指令会失败，可通过该指令进行检查是否开启
# 开启方式：
# 1. 控制面板 → 程序和功能 → 启用或关闭 Windows 功能
# 2. 打开：适用于 Linux 的 Windows 子系统

```

```bash

#-----------在Ubuntu环境中-----------#

sudo apt update 
sudo apt install python3-venv python3-pip -y # 确保 venv 模块存在（一般默认就有）

python3 -m venv ~/myQwenEnv/vllm-env # 创建虚拟环境（建议放在你项目目录里） 

source ~/myQwenEnv/vllm-env/bin/activate # 激活它，看到 (vllm-env) 前缀就成功激活了
# 这一步每次使用时都要执行

pip install --upgrade pip 
pip install vllm # 下载vllm

python -m vllm.entrypoints.openai.api_server \
  --model "/mnt/c/Windows/System32/models/Qwen2.5-3B-Instruct/" \
  --gpu-memory-utilization 0.83 \
  --max-model-len 4096 \
  --port 8000 \
  --served-model-name Qwen2.5-3B # 启动模型
# 这一步每次使用时都要执行

```

参数含义
- `--model` **必填**。指定本地模型文件夹路径，注意要用绝对路径。
- `--tensor-parallel-size`使用的 GPU 数量。单卡填 `1`，多卡填对应数字。
- `--gpu-memory-utilization` GPU 显存利用率，默认 0.9（即最多用 90% 显存）。
- `--max-model-len` 模型最大上下文长度（token 数）。处理短文本（如薪资条目）可以设小一点如 4096，留更多显存。
- `--port` 服务端口，默认 8000。
- `--served-model-name` 给模型起一个调用时用的名字。

```python

#------------- 在Windows上的python环境（调用示例） ---------------#

from openai import OpenAI  
  
client = OpenAI(  
    base_url="http://localhost:8000/v1",  # 关键点：指向你的 vLLM 服务器地址 
    api_key="EMPTY"  
    # vLLM 默认不验证 API key，但 OpenAI 客户端需要这个参数
    # 可以设为空字符串或任意值 [citation:3]
)  
# 初始化客户端  
# base_url 需要指向你 WSL 中 vLLM 服务的地址  
# 默认端口是 8000，WSL 的 IP 通常可以通过主机名 localhost 访问    
 
chat_completion = client.chat.completions.create(  
    model="Qwen2.5-3B",  
    # 必须与启动服务时设置的 --served-model-name 一致 
    messages=[  
        {"role": "user", "content": "介绍一下自己"}  
    ],  
    temperature=0.7,  
    max_tokens=2048,  
)  

print(chat_completion.choices[0].message.content)  
# 打印模型的回复 

```
