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

    for bug in collected:
        project = bug.split("bugs_")[1]
        
        with open(bug, "r") as f:
            bug_list = json.load(f)
        
        num_bug = len(bug_list.keys())
        
        if num_bug != 0:
            output[project] = num_bug
        total += len(bug_list.keys())
    
    print(output)
    print(total)


