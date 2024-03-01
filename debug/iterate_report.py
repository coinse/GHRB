#!/usr/bin/python3.9

import os
import json

#from util import config, fix_build_env
import re
import subprocess as sp
import argparse
import pandas as pd
from datetime import datetime

def call_iterate():

    output = ""
    with open("collected/report.json", 'r') as f:
        report = json.load(f)
    
    repo_dict = dict()
    
    for repo_name in report.keys():
        
        bid = report[repo_name].keys()

        with open(f"verified_bug/verified_bugs_{repo_name}.json", 'r') as f:
            verified_bugs = json.load(f)

        count = 0

        for b in bid:
            if b not in verified_bugs.keys():
                count += 1
        
        if count != 0:
            repo_dict[repo_name] = count
    
    # output += "## Output Summary  \n\n"
    
    if len(repo_dict.keys()) != 0:
        # output += "|Repo|Number of Possible Bugs|  \n\n"
        # output += "|---|---|  \n\n"
        for k, v in repo_dict.items():
            output += f"|{k}|{v}|  "
        print(output)
    else:
        print("No new bugs detected")


if __name__ == '__main__':

    output = call_iterate()
    
