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


if __name__ == '__main__':
    cur_dir = os.getcwd()
    file_list = os.listdir(cur_dir)

    collected = []

    for f in file_list:
        if "_verified" in f:
            collected.append(f)
    
    output = dict()

    total = 0

    names = []

    for bug in collected:
        project = bug.split("bugs_")[1]
        
        with open(bug, "r") as f:
            bug_list = json.load(f)
        
        num_bug = len(bug_list.keys())
        
        if num_bug != 0:
            output[project] = num_bug
        total += len(bug_list.keys())

        names += bug_list.keys()
    
    print(names)
    print(output)
    print(total)

    prod_diff_list = os.listdir(cur_dir + "/collected/prod_diff")
    test_diff_list = os.listdir(cur_dir + "/collected/test_diff")

    for prod in prod_diff_list:
        prod = prod.split(".diff")[0]
        if prod not in names:
            subprocess.run(["rm", "-rf", f"{cur_dir}/collected/prod_diff/{prod}.diff"])
    for test in test_diff_list:
        test = test.split(".diff")[0]
        if test not in names:
            subprocess.run(["rm", "-rf", f"{cur_dir}/collected/test_diff/{test}.diff"])

    

