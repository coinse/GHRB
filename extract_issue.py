import requests
from urllib.parse import urlparse
import os
import json

def extract_github_issue (url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip('/').split('/')
    headers = {"Authorization": "token " }

    owner, repo, issue_number = path_segments[0], path_segments[1], path_segments[3]
    #print(owner, repo, issue_number)
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        issue_info = response.json ()
        return issue_info
    else:
        return None

def iterate ():
    for file in os.listdir("verified_bug"):
        with open(f"verified_bug/{file}", "r") as f:
            content = json.load(f)

        for bug in content:
            output = dict()
            bug_id = content[bug]["bug_id"]
            issue_url = content[bug]["issue"]["url"]
        
            issue_info = extract_github_issue(issue_url)
            
            output["issue_id"] = issue_info["number"]
            output["issue_url"] = issue_info["html_url"]
            output["title"] = issue_info["title"]
            output["description_text"] = issue_info['body']

    
            with open(f"bug_reports/{bug_id}.json", "w") as f:
                json.dump(output, f, indent = 2)

if __name__ == '__main__':
    if not os.path.isdir("bug_reports"):
        os.makedirs("bug_reports")
iterate()
