import random
import re
import threading
import time

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import progressbar
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse


# 令牌读取
with open("token.txt", "r") as token_file:
    for line in token_file:
        if line.strip() and not line.strip().startswith("#"):
            access_token = line.strip()
headers = {
    "Authorization": f"token {access_token}"
}
print(headers)


def find_merge_conflict(pull_url):
    # 判断是否发生了合并冲突
    if pull_url:
        response = retry_session().get(pull_url, headers=headers)
        pull = response.json()
        # print("Pull information:", pull)  # 添加调试语句，打印拉取请求的信息
        # print("Mergeable status:", pull.get("mergeable_state"))  # 添加调试语句，打印合并状态
        mergeable = pull.get("mergeable_state", None)  # 从 pull 字典中获取 mergeable 字段的值
        if pull["mergeable_state"] == "dirty":
            return True
        else:
            return False
    else:
        return False


def get_random_repositories(num_repositories):
    # 随机寻找github仓库
    url = "https://api.github.com/repositories"
    response = retry_session().get(url, headers=headers)

    if response.status_code == 200:
        repositories = response.json()

        random_repos = [repo["url"] for repo in random.sample(repositories, num_repositories)]
        return random_repos
    else:
        print("Error occurred while fetching repositories:", response.status_code)
        return None


def get_pull_requests(repo_url):
    # 获得合并请求的网页
    url = f"{repo_url}/pulls"
    response = retry_session().get(url, headers=headers)

    if response.status_code == 200:
        pull_requests = response.json()
        if pull_requests:
            pull_urls = [pull["url"] for pull in pull_requests]
            return pull_urls
        else:
            # print(f"No pull requests found for {repo_url}.")
            return None
    else:
        print(f"Error occurred while fetching pull requests for {repo_url}:", response.status_code)
        return None


def retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    # retries: 重试次数, backoff_factor: 重试的退避因子, status_forcelist: 元组包含触发重试的HTTP状态码
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session


def process_pull_url(pull_url):
    global conflict_num
    global merge_conflict_dict
    if conflict_num >= max_conflict_num:
        return
    result = find_merge_conflict(pull_url)
    if result:
        parsed_url = urlparse(pull_url)
        repo_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/', 2)[0]}"
        with lock:
            # print(f"{pull_url}: have merge conflict!")
            if merge_conflict_dict.get(repo_url) == None:
                merge_conflict_dict[repo_url] = [pull_url]
            else:
                merge_conflict_dict[repo_url].append(pull_url)
            conflict_num += 1
            progress_bar.update(conflict_num)


if __name__ == "__main__":
    repo_num = 0
    conflict_num = 0
    merge_conflict_dict = {}

    max_conflict_num = 500
    max_repo_num = 10

    # 线程初始化
    lock = threading.Lock()
    thread_pool = ThreadPoolExecutor(max_workers=12)

    # 进度条初始化
    progress_bar = progressbar.ProgressBar(max_value=max_conflict_num)
    progress_bar.update(conflict_num)

    while repo_num <= max_repo_num or conflict_num <= max_conflict_num:
        repo_urls = get_random_repositories(100)
        repo_num += len(repo_urls)
        for repo_url in repo_urls:
            if conflict_num >= max_conflict_num:
                break
            pull_urls = get_pull_requests(repo_url)
            if pull_urls:
                # print(pull_urls)
                # 创建线程
                for pull_url in pull_urls:
                    if conflict_num >= max_conflict_num:
                        break
                    thread_pool.submit(process_pull_url, pull_url)
            # print("Repo num:", repo_num, "Conflict num:", conflict_num)  # 添加调试语句，打印 repo_num 和 conflict_num 的值

    thread_pool.shutdown(wait=True)
    progress_bar.finish()

    for key, value in merge_conflict_dict.items():
        print(f"{key}: {value}")


