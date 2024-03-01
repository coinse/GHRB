import glob
import os
import html
import json
import datetime
import pandas as pd
import subprocess 
import shlex
import shutil
import time
from bs4 import BeautifulSoup
from collections import defaultdict
from dateutil import parser
import langid
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
import argparse

debug = True

'''
Fetch 50 latest pull requests of repositories in new_repo
Write each pull requests sorted by repo into raw_data

fetchLatestPullRequest -> find the latest PR number
fetchPullRequest -> find PRs
'''

def gql_request(client, graphql_query, params):
    result = client.execute(graphql_query, variable_values=params)
    return result

def find_last_pr_number(client, find_last_pr_query, param):
    query_result = gql_request(client, find_last_pr_query, param)

    latest_pr = query_result["repository"]["pullRequests"]["edges"][0]["node"]["number"]
    # pr_num_list = [x for x in range(latest_pr)]
    # pr_num_list = pr_num_list[latest_pr-3000 : latest_pr]
    return latest_pr

def find_first_pr_number(client, find_first_pr_query, param):
    query_result = gql_request(client, find_first_pr_query, param)
    if len(query_result["search"]["edges"]) == 0:
        return None
    first_pr = query_result["search"]["edges"][0]["node"]["number"]
    return first_pr

def iterate_each(client, fetch_pr_query, param, pr_num_list):
    pr_list = []

    for pr_num in pr_num_list:
        param["number"] = pr_num

        try:
            pr_result = gql_request(client, fetch_pr_query, param)
            if len(pr_result["repository"]["pullRequest"]["closingIssuesReferences"]['edges']) > 0:
              pr_list.append(pr_result)
            else:
              continue
        except TransportQueryError as err:
            continue

    return pr_list

def iterate_repo(repos, client, fetch_pr_query, date, existing):
    with open("scripts/graphql/fetchFirstPullRequests.graphql") as f:
        find_first_pr_query_raw = f.read()

    with open("scripts/graphql/fetchLatestPullRequests.graphql") as f:
        find_last_pr_query_raw = f.read()
    
    find_first_pr_query = gql(find_first_pr_query_raw)
    find_last_pr_query = gql(find_last_pr_query_raw)

    i = 0
    error_count = 0

    while i <= len(repos)-1:
        repo = repos[i]
        try:
            param = defaultdict()
            param["name"] = repo["name"]
            name = param["name"]
            param["owner"] = repo["owner"]["login"]
            owner = param["owner"]
            param["startDate"] = date
            param["query"] = f"repo:{owner}/{name} is:pr created:<{date}"
            pr_list = []

            last_pr = find_last_pr_number(client, find_last_pr_query, param)
            if existing:
                first_pr = find_first_pr_number(client, find_first_pr_query, param)
                #print(first_pr)
                if first_pr == None:
                    #print("No new PR")
                    i += 1
                    continue
                pr_num_list = list(range(first_pr, last_pr + 1))
            else:
                pr_num_list = [x for x in range(last_pr)]
                pr_num_list = pr_num_list[last_pr - 3000 : last_pr]
            
            #print(last_pr)
            pr_list = iterate_each(client, fetch_pr_query, param, pr_num_list)
        
            file_path = "collected/raw_data/" + param["owner"] + "_" + param["name"] + '.json'

            with open(file_path, 'w') as o:
                json.dump(pr_list, o, indent=2)
            
            #print(f"#{i} Done")
            i += 1
            error_count = 0
        except Exception as e:
            #print(e)
            time.sleep(60 * 5)
            error_count += 1
            # if the number of error count exceeds 20, continue to next repo
            if error_count > 20:
                i += 1
                
'''
Filter out PRs that were created before cutoff point, which is
June 2021
'''
def filter_old_PR (datapath, date):

    collected_pr = {}

    filter_date = parser.parse(date)

    for repo_data in glob.glob(os.path.join(datapath, '*.json')):
        repo_name = os.path.basename(repo_data).replace('.json', '')
        with open(repo_data) as f:
            collected_pr[repo_name] = json.load(f)

    # if debug:
    #     print(f'# of Original PR: {sum([len(collected_pr[repo]) for repo in collected_pr])}')

    filtered_pr = defaultdict(list)
    for repo_name in collected_pr:
        for pr_data in collected_pr[repo_name]:

            '''
            No closing issue reference
            Too many non-issue referencing pull requests, which is a problem
            '''
            issues = pr_data['repository']['pullRequest']['closingIssuesReferences']['edges']
            assert len(issues) > 0

            '''
            Filter out by date
            '''

            created_at = parser.parse(pr_data['repository']['pullRequest']['createdAt'], ignoretz=True)
            
            if created_at >= filter_date:
                filtered_pr[repo_name].append(pr_data)
    
    if debug:
        print(f'|PRs within relevant period|{sum([len(filtered_pr[repo]) for repo in filtered_pr])}|  ')
    return filtered_pr
    

'''
Filter out PRs that does not add any test to the project
'''
def filter_no_test_PR (filtered_pr):
    
    filtered_test_pr = defaultdict(list)

    def contains_test_in_paths(paths):
        for path in paths:
            if 'test' in path.lower() and path.endswith('.java'):
                return True

            if 'assert' in path.lower() and path.endswith('.java'):
                return True 

            if 'should' in path.lower() and path.endswith('.java'):
                return True
            
        return False
    
    for repo_name in filtered_pr:
        for pr_data in filtered_pr[repo_name]:
            changed_files = [node['node']['path'] for node in pr_data['repository']['pullRequest']['files']['edges']]

            if contains_test_in_paths(changed_files):
                filtered_test_pr[repo_name].append(pr_data)
    
    if debug:
        print(f'|... that also have test files|{sum([len(filtered_test_pr[repo]) for repo in filtered_test_pr])}|  ')

    return filtered_test_pr

'''
PRs should not be associated with multiple issues
'''
def filter_multiple_PR (filtered_pr):
    filtered_issue_pr = defaultdict(list)

    for repo_name in filtered_pr:
        for pr_data in filtered_pr[repo_name]:
            issues = [node['node'] for node in pr_data['repository']['pullRequest']['closingIssuesReferences']['edges']]
            if len(issues) == 1:
                filtered_issue_pr[repo_name].append(pr_data)
    
    if debug:
        print(f'|... that also only mention a single issue|{sum([len(filtered_issue_pr[repo]) for repo in filtered_issue_pr])}|  ')

    return filtered_issue_pr


def filter_language_PR (filtered_pr):

    filtered_lang_pr = defaultdict(list)
    
    def find_lang(text):
        if text is None:
            return True
        lang, _ = langid.classify(text)
        if lang == 'en':
            return True
        else:
            return False

    for repo_name in filtered_pr:
        for pr_data in filtered_pr[repo_name]:
            title = pr_data['repository']['pullRequest']['title']
            merge_message = pr_data['repository']['pullRequest']['mergeCommit']['message'] if pr_data['repository']['pullRequest']['mergeCommit'] is not None else None
            issue_title = pr_data['repository']['pullRequest']['closingIssuesReferences']['edges'][0]['node']['title']
            issue_body = pr_data['repository']['pullRequest']['closingIssuesReferences']['edges'][0]['node']['bodyHTML']
            issue_body = BeautifulSoup(issue_body, 'html.parser').get_text()
            if find_lang(title) and find_lang(merge_message) and find_lang(issue_title) and find_lang(issue_body):
                filtered_lang_pr[repo_name].append(pr_data)

    if debug:
        print(f'|... that also are in English|{sum([len(filtered_lang_pr[repo]) for repo in filtered_lang_pr])}|  ')
    return filtered_lang_pr

'''
Filter out PRs that are not merged to the main branch
'''
def filter_main_branch_PR (filtered_pr):
    
    if not os.path.isdir("collected/new_collected_issues"):
        os.makedirs("collected/new_collected_issues")

    filtered_main_pr = defaultdict(dict)

    for repo_name in filtered_pr:
        for pr_data in filtered_pr[repo_name]:
            pr_data = pr_data['repository']['pullRequest']

            bug_id = f'{repo_name}-{pr_data["number"]}'

            changed_test_files = [node['node']['path'] for node in pr_data['files']['edges'] if 'test' in node['node']['path'].lower() and node['node']['path'].endswith('.java')]
            closing_issue = pr_data['closingIssuesReferences']['edges'][0]['node']
            
            merge_commit_url = None
            merge_commit = None
            parents = None

            merge_commit_url = pr_data['mergeCommit']['commitUrl'] if pr_data['mergeCommit'] else None
            merge_commit = pr_data['mergeCommit']['oid'] if pr_data['mergeCommit'] else None
            parents = pr_data['mergeCommit']['parents']['nodes'] if pr_data['mergeCommit'] else None

            if merge_commit_url is None:
                merge_commit_url = pr_data['potentialMergeCommit']['commitUrl'] if pr_data['potentialMergeCommit'] else None
                merge_commit = pr_data['potentialMergeCommit']['oid'] if pr_data['potentialMergeCommit'] else None
                parents = pr_data['potentialMergeCommit']['parents']['nodes'] if pr_data['potentialMergeCommit'] else None


            if merge_commit_url is None:
                continue

            with open(f'collected/new_collected_issues/{bug_id}.json', 'w') as f:
                description = html.unescape(closing_issue['bodyHTML'])
                json.dump({
                    'issue_id': closing_issue['number'],
                    'issue_url': closing_issue['url'],
                    'title': closing_issue['title'],
                    'description': description,
                    'description_text': BeautifulSoup(description, 'html.parser').get_text(),
                }, f, indent=2)
            
            _closing_issue = {
                'url': closing_issue['url'],
                'createdAt': closing_issue['createdAt'],
                'content': f'bug_report_all/{bug_id}.json',
            }
            filtered_main_pr[repo_name][bug_id] = {
                'bug_id': f'{repo_name}-{pr_data["number"]}',
                'PR_number': pr_data['number'],
                'PR_createdAt': pr_data['createdAt'],
                'merge_commit': merge_commit,
                'buggy_commits': parents,
                'issue': _closing_issue,
                'changed_tests': changed_test_files,
                'PR_url': pr_data['url'],
                'merge_commit_url': merge_commit_url,
            }

    if debug:
        print(f'|... that also were merged in the main branch|{sum([len(filtered_main_pr[repo]) for repo in filtered_main_pr])}|  ')

    return filtered_main_pr

'''
Filter out PRs without test diff
'''

def clone_repos (filtered_pr):

    if not os.path.isdir("collected/raw_repos"):
        os.makedirs("collected/raw_repos")

    for repo_name in filtered_pr:
        owner, name = repo_name.split("_")
        link = "https://github.com/" + owner + "/" + name
        name = os.getcwd() + '/collected/raw_repos/' + name
        p = subprocess.Popen(['git', 'clone', link, name], stderr=subprocess.PIPE, stdout=subprocess.PIPE)

def filter_test_diff_PR (filtered_pr):

    new_cleaned_data = {}

    repo_path = ""
    if not os.path.isdir("collected/test_diff"):
        os.makedirs("collected/test_diff")
        
    for repo_name in filtered_pr:
        # if debug:
        #     print("filtering repo: ", repo_name)
        
        new_cleaned_data[repo_name] = {}

        owner, name = repo_name.split("_")

        repo_path = os.getcwd() + '/collected/raw_repos/' + name

        for bug_id, bug_info in filtered_pr[repo_name].items():
            merge_commit = bug_info['merge_commit']
            buggy_commits = [c['oid'] for c in bug_info['buggy_commits']]

            if len(bug_info['changed_tests']) != 0:
                test_dir = bug_info['changed_tests'][0]
                test_dir = test_dir.split('/')
                if 'test' in test_dir:
                    index = test_dir.index('test')
                    test_dir = "/".join(test_dir[:index+2])
                else:
                    test_dir = 'src/test/java'

            selected_buggy_commit = None
            diff = None

            # get diff using buggy commit and fixed commit
            for buggy_commit in buggy_commits:
                p = subprocess.run(shlex.split(f'git diff {buggy_commit} {merge_commit} -- {test_dir}')
                                   , stdout=subprocess.PIPE, stderr=subprocess.PIPE
                                   , cwd=repo_path)
                

                diff = p.stdout.decode()
                error_msg = p.stderr.decode()


                if len(error_msg) > 0:
                    if merge_commit in error_msg:
                        p = subprocess.run(shlex.split(f'git fetch origin {merge_commit}'), 
                                           stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                           cwd=repo_path)
                    elif buggy_commit in error_msg:
                        p = subprocess.run(shlex.split(f'git fetch origin {buggy_commit}'),
                                           stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                           cwd=repo_path)
                    
                    p = subprocess.run(shlex.split(f'git diff {buggy_commit} {merge_commit} -- {test_dir}'),
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       cwd=repo_path)

                    diff = p.stdout.decode()
                    error_msg = p.stderr.decode()


                if len(diff.strip()) > 0 and len(error_msg) == 0:
                    selected_buggy_commit = buggy_commit
                    break

            if selected_buggy_commit is None:
                # print(f'Failed to find test suite for {bug_id}')
                continue
            else:
                new_cleaned_data[repo_name][bug_id] = bug_info
            
            with open('collected/test_diff/{}.diff'.format(bug_info['bug_id']), 'w') as f:
                f.write(diff)
            
            new_cleaned_data[repo_name][bug_id]['buggy_commit'] = selected_buggy_commit
        
    repo_w_no_data = []
    for repo_name in new_cleaned_data:
        if len(new_cleaned_data[repo_name]) == 0:
            repo_w_no_data.append(repo_name)
    
    for repo_name in repo_w_no_data:
        del new_cleaned_data[repo_name]
    
    if debug:
        print(f'|... for which a valid test could also be extracted from the PR|{sum([len(new_cleaned_data[repo]) for repo in new_cleaned_data])}|  ')

    return new_cleaned_data

def fetch_prod_diff ():
    
    if not os.path.isdir("collected/prod_diff"):
        os.makedirs("collected/prod_diff")
    

    with open('collected/report.json', "r") as f:
        report_map = json.load(f)
    
    for repo_name in report_map:

        owner, name = repo_name.split("_")

        repo_path = os.getcwd() + '/collected/raw_repos/' + name


        for bug_id, bug_info in report_map[repo_name].items():
            merge_commit = bug_info['merge_commit']
            buggy_commits = [c['oid'] for c in bug_info['buggy_commits']]

            if len(bug_info['changed_tests']) != 0:
                test_dir = bug_info['changed_tests'][0]
                test_dir = test_dir.split('/')
                if 'test' in test_dir:
                    index = test_dir.index('test')
                    test_dir = "/".join(test_dir[:index+2])
                else:
                    test_dir = 'src/test/java'

            selected_buggy_commit = None
            diff = None

            for buggy_commit in buggy_commits:
                
                p = subprocess.run(shlex.split(f"git diff {buggy_commit} {merge_commit} -- '*.java' ':!{test_dir}/*' ':!*/test/*'")
                                , stdout=subprocess.PIPE, stderr=subprocess.PIPE
                                , cwd=repo_path)
                

                diff = p.stdout.decode()
                error_msg = p.stderr.decode()


                if len(error_msg) > 0:
                    if merge_commit in error_msg:
                        p = subprocess.run(shlex.split(f'git fetch origin {merge_commit}'), 
                                           stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                           cwd=repo_path)
                    elif buggy_commit in error_msg:
                        p = subprocess.run(shlex.split(f'git fetch origin {buggy_commit}'),
                                           stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                           cwd=repo_path)
                    
                    p = subprocess.run(shlex.split(f"git diff {buggy_commit} {merge_commit} -- '*.java' ':!{test_dir}/*' ':!*/test/*'"),
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       cwd=repo_path)

                    diff = p.stdout.decode()
                    error_msg = p.stderr.decode()


                if len(diff.strip()) > 0 and len(error_msg) == 0:
                    selected_buggy_commit = buggy_commit
                    break

            if selected_buggy_commit is None:
                #print(f'Failed to find test suite for {bug_id}')
                continue
            else:
                new_cleaned_data[repo_name][bug_id] = bug_info
            
            with open('collected/prod_diff/{}.diff'.format(bug_id), 'w') as f:
                f.write(diff)


if __name__ == "__main__":
    parser_ = argparse.ArgumentParser(description="Bug Raw Data Gatherer")
    parser_.add_argument('-t', '--api_token')
    parser_.add_argument('-f', '--repository_file', type=str, default="example/example_metadata.json")
    parser_.add_argument('-d', '--date', type=str, default="2021-07-01")
    parser_.add_argument('-e', '--existing', action='store_true')
    args = parser_.parse_args()
    
    api_token = args.api_token
    filtered_repo = args.repository_file

    if not os.path.isdir("collected"):
        os.makedirs("collected")

    if not os.path.isdir("collected/raw_data"):
        os.makedirs("collected/raw_data")

    with open("scripts/graphql/fetchPullRequests.graphql") as f:
        fetch_pr_query_raw = f.read()

    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'Bearer %s' % api_token}

    transport = RequestsHTTPTransport(url=url, headers=headers, use_json=True)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    fetch_pr_query = gql(fetch_pr_query_raw)

    '''
    [
        "name": (name of the repo),
        "owner": 
            {
                "login": (owner of the repo)
            },
        "url": (full url for git clone)
    ], 
    
    '''
    
    with open(filtered_repo, "r") as f:
        new_repo = json.load(f)
    
    iterate_repo(new_repo, client, fetch_pr_query, args.date, args.existing)

    # print("## Data Gathering Statistics")
    # print("|Category|Number of PRs|")
    # print("|---|---|")

    filtered_data = filter_old_PR ("collected/raw_data", args.date)
    filtered_data = filter_no_test_PR (filtered_data)
    filtered_data = filter_multiple_PR (filtered_data)
    filtered_data = filter_language_PR (filtered_data)
    filtered_data = filter_main_branch_PR (filtered_data)
    clone_repos(filtered_data)
    new_cleaned_data = filter_test_diff_PR (filtered_data)

    # final_data = dict()

    # for repo_name in new_cleaned_data.keys():

    #     bid = new_cleaned_data[repo_name].keys()

    #     with open(f"verified_bug/verified_bugs_{repo_name}.json", "r") as f:
    #         verified_bugs = json.load(f)
        
    #     for b in bid:
    #         if b not in verified_bugs.keys():
    #             final_data[repo_name][b] = new_cleaned_data[repo_name][b]

    
    with open('collected/report.json', 'w') as f:
        json.dump(new_cleaned_data, f, indent=2)
    
    fetch_prod_diff()

    #print([f'{repo_name}: {len(final_data[repo_name])}' for repo_name in final_data])





