import logging
import coloredlogs
import sys
import os
import json
import requests
import getpass
import webbrowser
from fake_useragent import UserAgent
from api import GetWithoutTokenAPI
import jieba
from bigdata import TagTracker
import random
import math
import subprocess

def is_prime(n):
    """
    判断一个数是否为质数
    质数定义：大于1的自然数，且除了1和它本身外，不能被其他自然数整除
    """
    # 小于2的数不是质数
    if n < 2:
        return False
    
    # 2是质数
    if n == 2:
        return True
    
    # 偶数（除了2）不是质数
    if n % 2 == 0:
        return False
    
    # 检查从3到sqrt(n)的奇数是否能整除n
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    
    return True

def check_random_prime():
    """
    生成0到100之间的随机数并判断是否为质数
    返回布尔值：True(质数) 或 False(非质数)
    """
    # 生成0到100之间的随机整数
    random_number = random.randint(0, 100)
    
    # 判断是否为质数
    prime_check = is_prime(random_number)
    
    return prime_check


tracker = TagTracker("simple_tags.json")

Debug = True

LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "latest.log")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
)
if Debug:
    coloredlogs.install(level="DEBUG", fmt="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")
else:
    coloredlogs.install(level="INFO", fmt="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")

if os.path.exists("login.json"):
    try:
        with open("login.json", "r", encoding="utf-8") as f:
            login_data = json.load(f)
            login_user_name = login_data['user_info']['nickname']
            login_token = login_data['auth']['token']
    except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
        logging.warning(f"login.json 文件损坏或格式错误: {e}")
        # 删除损坏的文件，重新登录
        os.remove("login.json")
        login_user_name = None
else:
    logging.info("登录到Codemao Network以使用BetterCodemaoWorkPages")
    logging.info("请输入您的用户名/手机号")
    identity = input()
    logging.info("请输入您的密码")
    password = getpass.getpass()
    try:
        login_response = requests.post(
            url="https://api.codemao.cn/tiger/v3/web/accounts/login",
            headers={
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "User-Agent": UserAgent().random,
            },
            json={
            "pid": "65edCTyg",
            "identity": identity,
            "password": password
            }
        )
    except requests.RequestException as e:
        logging.error(f"登录请求失败: {e}")
        exit(1)

    logging.info(f"登录响应状态码: {login_response.status_code}")
    logging.info(f"登录响应内容: {login_response.text}")
    try:
        login_user_id = login_response.json()['user_info']['id']
        login_user_name = login_response.json()['user_info']['nickname']
    except KeyError:
        logging.error("登录响应中没有找到用户信息")
        exit(1)

    logging.info(f"登录成功，用户ID: {login_user_id}")
    # 将用户登录信息写入login.json
    with open("login.json", "w", encoding="utf-8") as f:
        f.write(login_response.text)
logging.info(f"欢迎回家，{login_user_name}")

amazing = GetWithoutTokenAPI("/creation-tools/v1/pc/home/recommend-work?type=1")
amazing = amazing.json()
logging.info("点猫精选:")
for item in amazing:
    logging.info(f"作品ID: {item['id']}，编辑器：{item['type']}，标题: {item['name']}，作者: {item['user']['nickname']}")
new = GetWithoutTokenAPI("/creation-tools/v1/pc/home/recommend-work?type=2")
new = new.json()
logging.info("新作喵喵看:")
for item in new:
    logging.info(f"作品ID: {item['id']}，编辑器：{item['type']}，标题: {item['name']}，作者: {item['user']['nickname']}")
logging.info("每日推荐:")
today = GetWithoutTokenAPI("/creation-tools/v1/pc/discover/subject-work?limit=200")
today = today.json()

# 直接获取items列表
if isinstance(today, dict) and 'items' in today:
    today = today['items']
# 如果已经是列表就直接使用

for item in today:
    # 直接获取work_name，根据不同的结构
    work_name = item.get('work_name') or (item.get('item') or {}).get('work_name', '')
    
    if work_name:
        tokens = jieba.lcut(work_name)
        if any(token in tracker.views for token in tokens):
            result = check_random_prime()
            if result:
                logging.info(f"作品ID: {item['work_id']}，标题: {item['work_name']}，作者: {item['nickname']}")

logging.info("请输入您要查看的作品ID，输入0退出，输入1刷新:")
input_workid = input()
if input_workid == "0":
    exit(0)
elif input_workid == "1":
    subprocess.call([sys.executable] + sys.argv)
    sys.exit(0)  # 结束当前进程
else:
    webbrowser.open(f"https://shequ.codemao.cn/work/{input_workid}")
    # 获取这个ID作品的名字
    work_info = GetWithoutTokenAPI(f"/creation-tools/v1/works/{input_workid}")
    work_name = work_info.json()['work_name']
    work_type = work_info.json()['type']
    work_worker = work_info.json()['user_info']['nickname']
    tracker.add(work_type)
    tokens = jieba.lcut(work_name)
    logging.info(tokens)
    for token in tokens:
        tracker.add(token)
    tracker.save()
    
