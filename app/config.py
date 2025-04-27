import os

version = '2.0.5'
contact = '701805520'
github = 'https://github.com/LC044/WeChatMsg'
website = 'https://memotrace.cn/'
copyright = '© 2022-2024 SiYuan'
license = 'GPLv3'
description = [
    '1. 支持获取个人信息<br>',
    '2. 支持显示聊天界面<br>',
    '3. 支持导出聊天记录<br>&nbsp;&nbsp;&nbsp;&nbsp;* csv<br>&nbsp;&nbsp;&nbsp;&nbsp;* html<br>&nbsp;&nbsp;&nbsp;&nbsp;* '
    'txt<br>&nbsp;&nbsp;&nbsp;&nbsp;* docx<br>',
    '4. 生成年度报告——圣诞特别版',
]
about = f'''
    版本：{version}<br>
    QQ交流群:请关注微信公众号回复：联系方式<br>
    地址：<a href='{github}'>{github}</a><br>
    官网：<a href='{website}'>{website}</a><br>
    新特性:<br>{''.join(['' + i for i in description])}<br>
    License <a href='https://github.com/LC044/WeChatMsg/blob/master/LICENSE' target='_blank'>{license}</a><br>
    Copyright {copyright}
'''

# 数据存放文件路径
INFO_FILE_PATH = './app/data/info.json'  # 个人信息文件
DB_DIR = './app/Database/Msg'
OUTPUT_DIR = './data/'  # 输出文件夹
os.makedirs('./app/data', exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
# 全局参数
SEND_LOG_FLAG = False  # 是否发送错误日志
SERVER_API_URL = None   #'http://api.lc044.love'  # api接口

# 硅基流动API配置
import json
import os

# 配置文件路径
API_CONFIG_FILE_PATH = './app/data/api_config.json'

# 默认API配置
DEFAULT_API_CONFIG = {
    "SIBEI_API_URL": "https://api.siliconflow.cn/v1/chat/completions",
    "SIBEI_API_KEY": "",  # 初始为空，需要用户配置
    "SIBEI_MODEL": "",  # 初始为空，需要用户配置
    "AI_TEMPERATURE": 0.7,
    "AI_MAX_TOKENS": 8000,

    # 聊天记录处理参数
    "CHAT_MAX_MESSAGES": 3000,  # 最多处理的消息数量
    "CHAT_MAX_TOKENS": 30000,   # 用于聊天记录的最大token数
    "CHAT_ESTIMATED_TOKENS_PER_MSG": 10  # 估计每条消息的平均token数
}

# 初始化全局变量
SIBEI_API_URL = DEFAULT_API_CONFIG["SIBEI_API_URL"]
SIBEI_API_KEY = DEFAULT_API_CONFIG["SIBEI_API_KEY"]
SIBEI_MODEL = DEFAULT_API_CONFIG["SIBEI_MODEL"]
AI_TEMPERATURE = DEFAULT_API_CONFIG["AI_TEMPERATURE"]
AI_MAX_TOKENS = DEFAULT_API_CONFIG["AI_MAX_TOKENS"]

# 聊天记录处理参数
CHAT_MAX_MESSAGES = DEFAULT_API_CONFIG["CHAT_MAX_MESSAGES"]
CHAT_MAX_TOKENS = DEFAULT_API_CONFIG["CHAT_MAX_TOKENS"]
CHAT_ESTIMATED_TOKENS_PER_MSG = DEFAULT_API_CONFIG["CHAT_ESTIMATED_TOKENS_PER_MSG"]

# 从配置文件加载设置
def load_api_config():
    """从配置文件加载API配置"""
    global SIBEI_API_URL, SIBEI_API_KEY, SIBEI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS
    global CHAT_MAX_MESSAGES, CHAT_MAX_TOKENS, CHAT_ESTIMATED_TOKENS_PER_MSG

    try:
        if os.path.exists(API_CONFIG_FILE_PATH):
            with open(API_CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                # 加载API配置
                SIBEI_API_URL = config_data.get("SIBEI_API_URL", DEFAULT_API_CONFIG["SIBEI_API_URL"])
                SIBEI_API_KEY = config_data.get("SIBEI_API_KEY", DEFAULT_API_CONFIG["SIBEI_API_KEY"])
                SIBEI_MODEL = config_data.get("SIBEI_MODEL", DEFAULT_API_CONFIG["SIBEI_MODEL"])
                AI_TEMPERATURE = config_data.get("AI_TEMPERATURE", DEFAULT_API_CONFIG["AI_TEMPERATURE"])
                AI_MAX_TOKENS = config_data.get("AI_MAX_TOKENS", DEFAULT_API_CONFIG["AI_MAX_TOKENS"])

                # 加载聊天记录处理参数
                CHAT_MAX_MESSAGES = config_data.get("CHAT_MAX_MESSAGES", DEFAULT_API_CONFIG["CHAT_MAX_MESSAGES"])
                CHAT_MAX_TOKENS = config_data.get("CHAT_MAX_TOKENS", DEFAULT_API_CONFIG["CHAT_MAX_TOKENS"])
                CHAT_ESTIMATED_TOKENS_PER_MSG = config_data.get("CHAT_ESTIMATED_TOKENS_PER_MSG", DEFAULT_API_CONFIG["CHAT_ESTIMATED_TOKENS_PER_MSG"])

                print(f"已加载API配置: URL={SIBEI_API_URL}, 模型={SIBEI_MODEL}, 温度={AI_TEMPERATURE}, 最大Token={AI_MAX_TOKENS}")
                print(f"已加载聊天记录处理参数: 最大消息数={CHAT_MAX_MESSAGES}, 最大Token数={CHAT_MAX_TOKENS}, 每条消息估计Token数={CHAT_ESTIMATED_TOKENS_PER_MSG}")
                return True
        else:
            # 如果配置文件不存在，创建一个默认的配置文件
            save_api_config()
            return False
    except Exception as e:
        print(f"读取API配置文件失败: {e}")
        return False

# 保存API配置到文件
def save_api_config(api_url=None, api_key=None, model=None, temperature=None, max_tokens=None,
                   chat_max_messages=None, chat_max_tokens=None, chat_estimated_tokens_per_msg=None):
    """
    保存API配置到文件

    Args:
        api_url: API URL
        api_key: API密钥
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大token数
        chat_max_messages: 最大处理消息数
        chat_max_tokens: 聊天记录最大token数
        chat_estimated_tokens_per_msg: 估计每条消息的token数
    """
    global SIBEI_API_URL, SIBEI_API_KEY, SIBEI_MODEL, AI_TEMPERATURE, AI_MAX_TOKENS
    global CHAT_MAX_MESSAGES, CHAT_MAX_TOKENS, CHAT_ESTIMATED_TOKENS_PER_MSG

    # 更新全局变量 - API配置
    if api_url is not None:
        SIBEI_API_URL = api_url
    if api_key is not None:
        SIBEI_API_KEY = api_key
    if model is not None:
        SIBEI_MODEL = model
    if temperature is not None:
        AI_TEMPERATURE = temperature
    if max_tokens is not None:
        AI_MAX_TOKENS = max_tokens

    # 更新全局变量 - 聊天记录处理参数
    if chat_max_messages is not None:
        CHAT_MAX_MESSAGES = chat_max_messages
    if chat_max_tokens is not None:
        CHAT_MAX_TOKENS = chat_max_tokens
    if chat_estimated_tokens_per_msg is not None:
        CHAT_ESTIMATED_TOKENS_PER_MSG = chat_estimated_tokens_per_msg

    # 更新配置文件
    try:
        config_data = {
            # API配置
            "SIBEI_API_URL": SIBEI_API_URL,
            "SIBEI_API_KEY": SIBEI_API_KEY,
            "SIBEI_MODEL": SIBEI_MODEL,
            "AI_TEMPERATURE": AI_TEMPERATURE,
            "AI_MAX_TOKENS": AI_MAX_TOKENS,

            # 聊天记录处理参数
            "CHAT_MAX_MESSAGES": CHAT_MAX_MESSAGES,
            "CHAT_MAX_TOKENS": CHAT_MAX_TOKENS,
            "CHAT_ESTIMATED_TOKENS_PER_MSG": CHAT_ESTIMATED_TOKENS_PER_MSG
        }
        os.makedirs(os.path.dirname(API_CONFIG_FILE_PATH), exist_ok=True)
        with open(API_CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"保存API配置文件失败: {e}")
        return False

# 加载配置
load_api_config()