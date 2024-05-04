import sys
sys.path.append("..")
from main import get_random_repositories, get_pull_requests, find_merging_url, find_merge_conflict

repo_num = 0
while repo_num <= 10:
    repo_url = get_random_repositories()

    if repo_url:
        repo_num += 1
        pull_urls = get_pull_requests(repo_url)
        if pull_urls:
            for pull_url in pull_urls:
                result = find_merge_conflict(find_merging_url(pull_url))
                if result:
                    print(f"{pull_url}: have merge conflict!")
                else:
                    print(f"{pull_url}: dont have merge conflict.")

# driver.quit()
