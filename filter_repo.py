import glob
import os
import html
import json
import datetime
import pandas as pd
import subprocess 
import shlex
import shutil
from time import sleep
import tqdm
from bs4 import BeautifulSoup

from collections import defaultdict
from dateutil import parser

from langdetect import detect, detect_langs
from textblob import TextBlob
import langid

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError

'''
Collected repositories
'''
def collect_repo_data (file):
    '''
    file needs to be composed of "github links"
    '''

    with open("scripts/graphql/fetchSpecificRepositoryData.graphql") as f:
        fetch_specific = f.read()

    api_token = input("GitHub API Token: ")
    url = 'https://api.github.com/graphql'
    headers = {'Authorization': 'Bearer %s' % api_token}

    transport = RequestsHTTPTransport(url=url, headers=headers, use_json=True)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    fetch_specific = gql(fetch_specific)
    param = {}
    repo_list = {}

    with open(file, 'r') as f:
        links = f.readlines()

    for link in tqdm(links):
        if link == '\n':
            break
        link = link.split("/")
        owner = link[-2]
        name = link[-1].replace("\n", "")
        param["name"] = name
        param["owner"] = owner

        error = 0
        done = False
        while done == False or error < 20:
            try:
                repo_result = client.execute(fetch_specific, variable_values=param)
                repo_list[name] = repo_result
                done = True
            except TransportQueryError as err:
                sleep(60 * 5)
                error += 1
        
    with open('collected/repo_metadata.json', 'w') as f:
        json.dump(repo_list, f, indent=2)

'''
Filter out PRs that are not in Eng
'''
def filter_language_repo ():
    collected_repos = {}
    filtered_repos = {}

    with open("collected/repo_metadata.json", 'rt', encoding='UTF8') as f:
        raw_repo = json.load(f)

    for repo in raw_repo.keys():
        collected_repos[repo] = raw_repo[repo]["repository"]


    for repo in collected_repos.keys():
        description = BeautifulSoup(collected_repos[repo]["descriptionHTML"], 'html.parser').get_text()
        lang, _ = langid.classify(description)
        if lang == 'en':
            filtered_repos[repo] = collected_repos[repo]
    
    return filtered_repos

'''
Filter out PRs that are not mainly in Java
'''
def filter_pl_repo (input_repos):
    output_repos = {}

    for repo, repo_data in input_repos.items():
        language_data = repo_data["languages"]['edges']
        total_size = repo_data["languages"]["totalSize"]
        for language in language_data:
            if language['node']['name'] == "Java" and language['size'] / total_size > 0.9:
                output_repos[repo] = repo_data
                break

    return output_repos 

if __name__ == "__main__":

    input_file = input("Name of the file, composed of GitHub links: ")
    collect_repo_data(input_file)

    output_repo = filter_language_repo()
    output_repo = filter_pl_repo(output_repo)

    new_repo = []
    for repo_data in output_repo.values():
        new_repo.append({"name": repo_data["name"], "owner": repo_data["owner"], "url": repo_data["url"]})
    
    with open('collected/filtered_repo_metadata.json', 'w') as f:
        json.dump(new_repo, f, indent = 2)
    

