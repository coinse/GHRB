import os
import re
import glob
import json
from os import path
from collections import Counter
from tqdm import tqdm


import subprocess as sp
import javalang
import argparse
import shutil

import os
import re
import glob
import subprocess
import shlex
import enlighten

def fetch_test_diff (report):

    new_cleaned_data = {}

    repo_path = ""
    if not os.path.isdir("collected/test_diff"):
        os.makedirs("collected/test_diff")
    

    with open(report, "r") as f:
        report_map = json.load(f)

    for repo_name in report_map:
        
        new_cleaned_data[repo_name] = {}

        owner, name = repo_name.split("_")

        link = "https://github.com/" + owner + "/" + name
        repo_path = os.getcwd() + '/repos/' + name
        p = subprocess.Popen(['git', 'clone', link, repo_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        

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
                print(f'Failed to find test suite for {bug_id}')
                continue
            else:
                new_cleaned_data[repo_name][bug_id] = bug_info
            
            with open('collected/test_diff/{}.diff'.format(bug_info['bug_id']), 'w') as f:
                f.write(diff)
            

def fetch_prod_diff (report):
    
    if not os.path.isdir("collected/prod_diff"):
        os.makedirs("collected/prod_diff")
    

    with open(report, "r") as f:
        report_map = json.load(f)
    
    for repo_name in report_map:

        owner, name = repo_name.split("_")

        repo_path = os.getcwd() + '/repos/' + name


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
                print(f'Failed to find prod diff for {bug_id}')
                continue
            
            with open('collected/prod_diff/{}.diff'.format(bug_id), 'w') as f:
                f.write(diff)

if __name__ == '__main__':

    # with open('report.json') as f:
    #     report_test_mappings = json.load(f)


    # fetch_test_diff('report.json')
    # fetch_prod_diff('report.json')
    with open('report.json', "r") as f:
        report_map = json.load(f)

    for report in report_map:
        print(report)
    print("DONE")