#!/usr/bin/python3.9

import os
import json

#from util import config, fix_build_env
import re
import subprocess as sp
import argparse
import pandas as pd
from datetime import datetime

def call_compare():

    output = ""
    with open("collected/report.json", 'r') as f:
        report = json.load(f)
    
    for repo_name in report.keys():
        
        bid = report[repo_name].keys()

        with open(f"verified_bug/verified_bugs_{repo_name}.json", 'r') as f:
            verified_bugs = json.load(f)

        for b in bid:
            if b not in verified_bugs.keys():
                output += f"{repo_name}_{b}\n"
        
    if len(output) != 0:
        print(output)
        print(report)
    else:
        print("No new bugs detected")


if __name__ == '__main__':

    output = call_compare()
    
