# import sys
#
# import requests
#
# sys.path.append("..")
# from main import get_random_repositories, get_pull_requests, retry_session
#
# with open("../token.txt", "r") as token_file:
#     access_token = token_file.read().strip()
# headers = {
#     "Authorization": f"token {access_token}"
# }
#
# repo_url = get_random_repositories(headers)
# pulls = get_pull_requests(repo_url, headers)
# print(repo_url)
# print(pulls)
# # for pull in pulls:
# response = requests.get("https://api.github.com/repos/mingQianGu/test/pulls/1", headers=headers)
# result = response.json()
# print(result)

# from urllib.parse import urlparse
#
# pull_url = "https://api.github.com/repos/mingQianGu/test/pulls/1"
# parsed_url = urlparse(pull_url)
# repo_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path.rsplit('/', 2)[0]}"
# print(repo_url)

merge_conflict_dict = {"1": [1, 2, 3], "2": [2, 3, 4]}


for key, value in merge_conflict_dict.items():
    print(f"{key}: {value}")

