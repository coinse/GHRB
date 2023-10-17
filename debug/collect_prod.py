
import os
import json
import pandas as pd
import subprocess 
import shlex
import shutil


def fetch_prod_diff ():

    if os.path.isdir("prod_diff"):
        shutil.rmtree("prod_diff")
    
    if not os.path.isdir("prod_diff"):
        os.makedirs("prod_diff")
    


    new_cleaned_data = {}

    with open('project_id.json') as f:
        project_id = json.load(f)
    
    for repo_name in project_id:
        print(repo_name)
        

        new_cleaned_data[repo_name] = {}

        #owner, name = repo_name.split("_")

        name = repo_name.split("_")

        repo_path = project_id[repo_name]["repo_path"]
        commit_db = project_id[repo_name]["commit_db"]
        owner = project_id[repo_name]["owner"]
        num_bugs = project_id[repo_name]["number_of_bugs"]

        if repo_name == 'gson':
            test_dir = 'gson/src/test/java'
        elif repo_name == 'sslcontext-kickstart':
            test_dir = 'sslcontext-kickstart/src/test/java'
        elif repo_name == 'closure-compiler':
            test_dir = 'test/com/google'
        else:
            test_dir = 'src/test/java'

        active_bugs = pd.read_csv(commit_db)

        for b_id in range(1, num_bugs+1):
            revision_id_fixed = active_bugs.loc[active_bugs['bug_id'] == int(b_id)]["revision.id.fixed"].values[0] # merge_commit
            revision_id_buggy = active_bugs.loc[active_bugs['bug_id'] == int(b_id)]["revision.id.buggy"].values[0] # buggy_commit
            report_id = active_bugs.loc[active_bugs['bug_id'] == int(b_id)]["report.id"].values[0]


            diff = None
            
            p = subprocess.run(shlex.split(f"git diff {revision_id_buggy} {revision_id_fixed} -- ':!{test_dir}'")
                                , stdout=subprocess.PIPE, stderr=subprocess.PIPE
                                , cwd=repo_path)
            
            
            diff = p.stdout.decode()
            error_msg = p.stderr.decode()

            if len(error_msg) > 0:
                if revision_id_fixed in error_msg:
                    p = subprocess.run(shlex.split(f'git fetch origin {revision_id_fixed}'), 
                                        stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                        cwd=repo_path)
                elif revision_id_buggy in error_msg:
                    p = subprocess.run(shlex.split(f'git fetch origin {revision_id_buggy}'),
                                        stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                        cwd=repo_path)
                
                p = subprocess.run(shlex.split(f"git diff {revision_id_buggy} {revision_id_fixed} -- ':!{test_dir}'"),
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    cwd=repo_path)

                diff = p.stdout.decode()
                error_msg = p.stderr.decode()

            
            with open('prod_diff/{}.diff'.format(report_id), 'w') as f:
                f.write(diff)
            
        

    print("Done")

if __name__ == '__main__':
    fetch_prod_diff()
