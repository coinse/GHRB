import os

import json
from collections import Counter, defaultdict

import subprocess as sp

import pandas as pd

def clone_repo (owner, name):
    link = "https://github.com/" + owner + "/" + name
    print(link)
    name = '/root/framework/repos/' + name
    p = sp.Popen(['git', 'clone', link, name], stderr=sp.PIPE, stdout=sp.PIPE)

def project_id_collector():
    project_map = defaultdict(dict)
    
    for file in os.listdir("/root/framework/verified_bug/"): 
        project_id = file.split("_")[-1].replace(".json", "")
        owner = file.split("_")[-2]
        
        with open("/root/framework/verified_bug/" + file, 'r') as f:
            active_bug_list = json.load(f)
        
        number_of_bugs = len(active_bug_list)
        commit_db = f"commit_db/{project_id}_bugs.csv"

        with open("/root/framework/data/requirements.json", 'r') as f:
            requirements = json.load(f)

        repo_path = None

        clone_repo(owner, project_id)

        for dir in os.listdir("/root/framework/repos/"):
            if project_id in dir:
                repo_path = os.path.abspath(os.path.join('/root/framework/repos/', f'{dir}'))
        project_map[project_id]["owner"] = owner
        project_map[project_id]["number_of_bugs"] = number_of_bugs
        project_map[project_id]['commit_db'] = commit_db
        project_map[project_id]['repo_path'] = repo_path
        project_map[project_id]['requirements'] = requirements[project_id]

    
    with open('/root/framework/data/project_id.json', 'w') as f:
        json.dump(project_map, f, indent=2)

def commit_db_collector():
    for file in os.listdir("/root/framework/verified_bug/"): 
        project_id = file.split("_")[-1].replace(".json", "")
        owner = file.split("_")[-2]
        
        with open("/root/framework/verified_bug/" + file, 'r') as f:
            active_bug_list = json.load(f)
        
        commit_db = pd.DataFrame(columns=['bug_id', 'revision.id.buggy', 'revision.id.fixed', 'report.id', 'report.url'], 
                                 index=list(range(len(active_bug_list))))

        commit_db = commit_db.fillna(0)

        commit_db.index += 1

        index = 1
        for key, value in active_bug_list.items():
            commit_db.loc[index] = [index, value['buggy_commit'], value['merge_commit'], value["bug_id"], value['issue']['url']]
            index += 1
        
        commit_db.to_csv("/root/framework/commit_db/" + project_id + "_bugs.csv", index=False)

def find_og_collector():
    total_list = set()
    filtered = []
    with open('/root/framework/data/og_mapping.json', 'r') as f:
        og_mapping = json.load(f)
    
    for key, value in og_mapping.items():
        total_list.add(key)

    for file in os.listdir("/root/framework/verified_bug/"):
        with open("/root/framework/verified_bug/" + file, 'r') as f:
            active_bug_list = json.load(f)
        for key in active_bug_list.keys():
            #print(key)
            project_name = key.split('-')[0]
            bug_id = key.split('-')[1]
            if key in total_list:
                filtered.append(key)

            elif project_name == 'assertj_assertj' and "".join(project_name + '-core-' + bug_id) in total_list:
                filtered.append(key)


def find_total_bug():
    bug_dict = defaultdict(int)
    total = 0
    for file in os.listdir("/root/framework/verified_bug/"):
        with open("/root/framework/verified_bug/" + file, 'r') as f:
            active_bug_list = json.load(f)
        name = str(file).replace(".json", '')
        bug_dict[name.split("_")[-1]] = len(active_bug_list)
        total += len(active_bug_list)
    
    print(bug_dict)
    print('total: ', total)


def remove_test_diff ():
    all_bug = []
    for file in os.listdir("/root/framework/verified_bug/"):
        with open("/root/framework/verified_bug/" + file, 'r') as f:
            active_bug_list = json.load(f)
        for key in active_bug_list.keys():
            all_bug.append(key)
    i = 0
    bug_dict = defaultdict(int)
    
    for diff in os.listdir("/root/framework/data/test_diff/"):
        bug_dict[diff.split("_")[-2] + "_" + diff.split("_")[-1].split("-")[0]] += 1
        name = diff.replace(".diff", "")
        if name not in all_bug:
            sp.run(["rm", "-rf", f"/root/framework/data/test_diff/{name}.diff"])

def remove_prod_diff ():
    all_bug = []
    for file in os.listdir("/root/framework/verified_bug/"):
        with open("/root/framework/verified_bug/" + file, 'r') as f:
            active_bug_list = json.load(f)
        for key in active_bug_list.keys():
            all_bug.append(key)
    i = 0
    bug_dict = defaultdict(int)
    
    for diff in os.listdir("/root/framework/data/prod_diff/"):
        bug_dict[diff.split("_")[-2] + "_" + diff.split("_")[-1].split("-")[0]] += 1
        name = diff.replace(".diff", "")
        if name not in all_bug:
            sp.run(["rm", "-rf", f"/root/framework/data/prod_diff/{name}.diff"])

    

if __name__ == '__main__':
    project_id_collector()
    commit_db_collector()
    find_og_collector()
    find_total_bug()
    remove_test_diff()
    remove_prod_diff()