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
import copy

import subprocess
import shlex
import enlighten
import pandas as pd
import sys


file_path = os.getcwd()

config = {
    'alibaba_fastjson': {
        'repo_path': file_path + '/repos/fastjson',
        'src_dir': 'src/main/java/',
        'test_prefix': 'src/test/java',
        'project_name': 'alibaba_fastjson',
        'project_id': 'fastjson'
    },
    'TheAlgorithms_Java': {
        'repo_path': file_path + '/repos/Java',
        'src_dir': 'src/main/java/',
        'test_prefix': 'src/test/java',
        'project_name': 'TheAlgorithms_Java',
        'project_id': 'Java'
    },
    'ReactiveX_RxJava': {
        'repo_path': file_path + '/repos/RxJava',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'ReactiveX_RxJava',
        'project_id': 'RxJava'
    },
    'LMAX-Exchange_disruptor': {
        'repo_path': file_path + '/repos/disruptor',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'LMAX-Exchange_disruptor',
        'project_id': 'disruptor'
    },
    'assertj_assertj': {
        'repo_path': file_path + '/repos/assertj',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'assertj_assertj',
        'project_id': 'assertj'
    },
    'checkstyle_checkstyle': {
        'repo_path': file_path + '/repos/checkstyle',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'checkstyle_checkstyle',
        'project_id': 'checkstyle'
    },
    'FasterXML_jackson-core': {
        'repo_path': file_path + '/repos/jackson-core',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'FasterXML_jackson-core',
        'project_id': 'jackson-core'
    },
    'FasterXML_jackson-databind': {
        'repo_path': file_path + '/repos/jackson-databind',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'FasterXML_jackson-databind',
        'project_id': 'jackson-databind'
    },
    'jhy_jsoup': {
        'repo_path': file_path + '/repos/jsoup',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'jhy_jsoup',
        'project_id': 'jsoup'
    },
    'mockito_mockito': {
        'repo_path': file_path + '/repos/mockito',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'mockito_mockito',
        'project_id': 'mockito'
    },
    'FasterXML_jackson-dataformat-xml': {
        'repo_path': file_path + '/repos/jackson-dataformat-xml',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'FasterXML_jackson-dataformat-xml',
        'project_id': 'jackson-dataformat-xml'
    },
    'google_gson': {
        'repo_path': file_path + '/repos/gson',
        'src_dir': 'gson/src/main/java',
        'test_prefix': 'gson/src/test/java',
        'project_name': 'google_gson',
        'project_id': 'gson'
    },
    'Hakky54_sslcontext-kickstart': {
        'repo_path': file_path + '/repos/sslcontext-kickstart/sslcontext-kickstart',
        'src_dir': 'sslcontext-kickstart/src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'Hakky54_sslcontext-kickstart',
        'project_id': 'sslcontext-kickstart'
    },
    'google_closure-compiler': {
        'repo_path': file_path + '/repos/closure-compiler',
        'src_dir': 'src/com/google',
        'test_prefix': 'test/com/google',
        'project_name': 'google_closure-compiler',
        'project_id': 'closure-compiler'
    },
    'netty_netty': {
        'repo_path': file_path + '/repos/netty',
        'src_dir': 'handler/src',
        'test_prefix': 'handler/src/test',
        'project_name': 'netty_netty',
        'project_id': 'netty'
    },
    'apache_rocketmq': {
        'repo_path': file_path + '/repos/rocketmq',
        'src_dir': '',
        'test_prefix': '',
        'project_name': 'apache_rocketmq',
        'project_id': 'rocketmq'
    },
    'apache_dubbo': {
        'repo_path': file_path + '/repos/dubbo',
        'src_dir': '',
        'test_prefix': '',
        'project_name': 'apache_dubbo',
        'project_id': 'dubbo',
    },
    'iluwatar_java-design-patterns': {
        'repo_path': file_path + '/repos/java-design-patterns',
        'project_name': 'iluwatar_java-design-patterns',
    },
    'dbeaver_dbeaver': {
        'repo_path': file_path + '/repos/dbeaver',
        'project_name': 'dbeaver_dbeaver'
    },
    'seata_seata': {
        'repo_path': file_path + '/repos/seata',
        'project_name': 'seata_seata',
        'project_id': 'seata'
    },
    'OpenAPITools_openapi-generator': {
        'repo_path': file_path + '/repos/openapi-generator',
        'project_name': 'OpenAPITools_openapi-generator',
        'project_id': 'openapi-generator'
    },
    'apache_shardingsphere': {
        'repo_path': file_path + '/repos/shardingsphere',
        'project_name': 'apache_shardingsphere'
    },
    'alibaba_nacos': {
        'repo_path': file_path + '/repos/nacos',
        'project_name': 'alibaba_nacos',
        'project_id': 'nacos'
    },
    'keycloak_keycloak': {
        'repo_path': file_path + '/repos/keycloak',
        'project_name': 'keycloak_keycloak'
    },
    'redisson_redisson': {
        'repo_path': file_path + '/repos/redisson',
        'project_name': 'redisson_redisson'
    },
    'elastic_elasticsearch': {
        'repo_path': file_path + '/repos/elasticsearch',
        'project_name': 'elastic_elasticsearch'
    },
    'iBotPeaches_Apktool': {
        'repo_path': file_path + '/repos/Apktool',
        'project_name': 'iBotPeaches_Apktool',
        'project_id': 'Apktool'
    },
    'spring-projects_spring-framework': {
        'repo_path': file_path + '/repos/spring-framework',
        'project_name': 'spring-projects_spring-framework'
    },
    'square_retrofit': {
        'repo_path': file_path + '/repos/retrofit',
        'project_name': 'square_retrofit',
        'project_id': 'retrofit'
    },
    'javaparser_javaparser': {
        'repo_path': file_path + '/repos/javaparser',
        'project_name': 'javaparser_javaparser',
        'project_id': 'javaparser'
    }
    }

license_sslcontext_kickstart = '''
/*
 * Copyright 2019-2022 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
'''


properties_to_replace = {
    'jackson-core': {
        r'<javac.src.version>\s*1.6\s*</javac.src.version>': '',
        r'<javac.target.version>\s*1.6\s*</javac.target.version>': '',
        r'<maven.compiler.source>\s*1.6\s*</maven.compiler.source>': '<maven.compiler.source>11</maven.compiler.source>',
        r'<maven.compiler.target>\s*1.6\s*</maven.compiler.target>': '<maven.compiler.target>11</maven.compiler.target>',
    },
    'jackson-databind': {
        r'<version>\s*2.13.0-rc1-SNAPSHOT\s*</version>': '<version>2.14.0-SNAPSHOT</version>',
        r'<source>\s*14\s*</source>': '<source>17</source>',
        r'<release>\s*14\s*</release>': '<release>17</release>',
        r'<id>\s*java17\+\s*</id>': '<id>java17+</id>',
        r'<jdk>\s*\[17\,\)\s*</jdk>': '<jdk>[17,)</jdk>'
    }
}

def split_project_bug_id(bug_key):
    s = bug_key.split('_')
    project = '_'.join(s[:-1])
    bug_id = s[-1]

    return project, bug_id


def fix_build_env(repo_dir_path):
    if 'jackson-core' in repo_dir_path or 'jackson-databind' in repo_dir_path:
        pom_file = os.path.join(repo_dir_path, 'pom.xml')

        with open(pom_file, 'r') as f:
            content = f.read()

        if 'jackson-core' in repo_dir_path:
            replace_map = properties_to_replace['jackson-core']
        elif 'jackson-databind' in repo_dir_path:
            replace_map = properties_to_replace['jackson-databind']

        for unsupported_property in replace_map:
            content = re.sub(
                unsupported_property, replace_map[unsupported_property], content)

        with open(pom_file, 'w') as f:
            f.write(content)

def pit(it, *pargs, **nargs):
    # https://stackoverflow.com/questions/23113494/double-progress-bar-in-python

    global __pit_man__
    try:
        __pit_man__
    except NameError:
        __pit_man__ = enlighten.get_manager()
    man = __pit_man__
    try:
        it_len = len(it)
    except:
        it_len = None
    try:
        ctr = None
        for i, e in enumerate(it):
            if i == 0:
                ctr = man.counter(
                    *pargs, **{**dict(leave=False, total=it_len), **nargs})
            yield e
            ctr.update()
    finally:
        if ctr is not None:
            ctr.close()

DEBUG = True

def get_project_from_bug_id(bug_id):
    for project_identifier in config:
        if project_identifier in bug_id:
            return project_identifier
        
def get_project_id_from_project(project):
    return config[project]['project_id']
        
def find_env (pid):
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "No matching project id"
        return output

    requirements = project_id[pid]["requirements"]
    if len(requirements["extra"]) != 0:
        extra = requirements["extra"]
    
    build = requirements["build"]
    jdk_required = requirements["jdk"]
    wrapper = requirements["wrapper"]

    mvn_required = None
    mvnw = False
    gradlew = False

    if build == "maven":
        if wrapper:
            mvnw = True
        else:
            mvn_required = requirements["version"]
    elif build == "gradle":
        if wrapper:
            gradlew = True

    JAVA_HOME = mvn_path = None
    if jdk_required == '8':
        JAVA_HOME = '/usr/lib/jvm/java-8-openjdk-amd64'
    elif jdk_required == '11':
        JAVA_HOME = '/usr/lib/jvm/java-11-openjdk-amd64'
    elif jdk_required == '17':
        JAVA_HOME = '/usr/lib/jvm/java-17-openjdk-amd64'
    
    if mvn_required is None:
        mvn_path = None
    elif mvn_required == '3.8.6':
        mvn_path = '/opt/apache-maven-3.8.6/bin'
    elif mvn_required == '3.8.1':
        mvn_path = '/opt/apache-maven-3.8.1/bin'

    new_env = os.environ.copy()
    new_env['JAVA_HOME'] = JAVA_HOME
    if mvn_path is not None:
        new_env['PATH'] = os.pathsep.join([mvn_path, new_env['PATH']])

    return new_env, mvnw, gradlew


def run_test (new_env, mvnw, gradlew, test_case, path, command=None):

    if not mvnw and not gradlew:
        default = ['timeout', '30m', 'mvn', 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
        if command is not None:
            extra_command = command.split()
            new_command = default + extra_command
            run = sp.run(new_command,
                         env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)
        else:
            run = sp.run(default,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)

    elif mvnw:
        default = ['timeout', '10m', './mvnw', 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
        if command is not None:
            extra_command = command.split()
            new_command = default + extra_command

            run = sp.run(new_command,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)
        else:
            run = sp.run(default,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)
    elif gradlew:
        default = ["./gradlew", "test", "--tests", f'{test_case}', '--info', '--stacktrace']
        if command is not None:
            if 'test' in command:
                new_command = ["./gradlew", command, '--tests', f'{test_case}']
                run = sp.run(new_command,
                             env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)
            else:
                run = sp.run(new_command,
                             env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)
        else:
            run = sp.run(default,
                         env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)
    
    stdout = run.stdout.decode()
    stderr = run.stderr.decode()

    return stdout, stderr
            
def verify_in_buggy_version(buggy_commit, test_patch_dir, repo_path, test_prefix, build, pid):

    #print(repo_path, buggy_commit, test_patch_dir)
    p = sp.run(['git', 'reset', '--hard', 'HEAD'],
           cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)
    
    #print(p.stdout.decode())
    
    p = sp.run(['git', 'clean', '-df'],
           cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)

    #print(p.stdout.decode())
    # checkout to the buggy version and apply patch to the buggy version
    p = sp.run(['git', 'checkout', buggy_commit], cwd=repo_path,
           stdout=sp.PIPE, stderr=sp.PIPE)
    #print(p.stderr.decode())

    p = sp.run(['git', 'apply', test_patch_dir], cwd=repo_path,
           stdout=sp.PIPE, stderr=sp.PIPE)
    
    #print(p.stdout.decode())

    p = sp.run(['git', 'status'], cwd=repo_path,
               stdout=sp.PIPE, stderr=sp.PIPE)
    
    #print(p.stdout.decode())
    

    changed_test_files = [p.strip().split()[-1] for p in p.stdout.decode(
        'utf-8').split('\n') if p.strip().endswith('.java')]
    if len(changed_test_files) == 0:
        p = sp.run(['git', 'status', '-u'], cwd=repo_path, stdout=sp.PIPE, stderr=sp.PIPE)
        changed_test_files = [p.strip().split()[-1] for p in p.stdout.decode(
        'utf-8').split('\n') if p.strip().endswith('.java')]

    
    print("changed_test_files: ", changed_test_files)

    new_env, mvnw, gradlew = find_env(pid)
    
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)
    
    if len(project_id[pid]['requirements']['extra']) != 0:
        command = project_id[pid]['requirements']['extra']['command']
    else:
        command = None

    fix_build_env(repo_path)
    
    modules = []

    def replace_index (x):
        test_dir = x.split('/')
        
        index = test_dir.index('src')
        test_dir = ".".join(test_dir[index+3:])
        test_dir = "." + test_dir
        return test_dir

    def find_repo_path (x):
        test_dir = x.split('/')
        repo = test_dir[0]
        return repo
    

    changed_test_id = list(map(lambda x: replace_index(x), changed_test_files))
    #print("changed_test_id_before: ", changed_test_id)
    if build == 'gradle':
        for i in range(len(changed_test_files)):

            changed_test_id[i] = changed_test_id[i][1:]
            changed_test_id[i] = changed_test_id[i][:-5] ## change to replace

    print("changed_test_id: ", changed_test_id)
    valid_tests = []
    for idx, test_id in enumerate(changed_test_id):

        captured_stdout, captured_stderr = run_test (new_env, mvnw, gradlew, test_id, repo_path, command)

        #print(captured_stdout)
        if 'There are test failures' in captured_stdout:
            print("There are test failures")
            valid_tests.append(test_id)
        elif 'There were failing tests' in captured_stderr:
            print("There were failing tests")
            valid_tests.append(test_id)
        

    specified_repo_path = None

    return valid_tests, repo_path, modules


def verify_in_fixed_version(fixed_commit, target_test_classes, repo_path, test_prefix, build, modules, pid):
    
    sp.run(['git', 'reset', '--hard', 'HEAD'],
           cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    sp.run(['git', 'clean', '-df'],
           cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    sp.run(['git', 'checkout', fixed_commit], cwd=repo_path)


    new_env, mvnw, gradlew = find_env(pid)
    
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)
    
    if len(project_id[pid]['requirements']['extra']) != 0:
        command = project_id[pid]['requirements']['extra']['command']
    else:
        command = None

    fix_build_env(repo_path)

    valid_tests = []

    print("target_test_classes: ", target_test_classes)
    for idx, test_id in enumerate(target_test_classes):

        captured_stdout, captured_stderr = run_test (new_env, mvnw, gradlew, test_id, repo_path, command)

        if 'BUILD SUCCESS' in captured_stdout:
            print("Maven build success")
            valid_tests.append(test_id)
        elif 'BUILD SUCCESSFUL' in captured_stdout:
            print("Gradle build success")
            valid_tests.append(test_id)
        elif 'There are test failures' in captured_stdout or 'There were failing tests' in captured_stdout:
            print("Test failed in fixed version")

    return valid_tests

def verify_bug(bug_id, buggy_commit, fixed_commit, build='maven'):
    project = get_project_from_bug_id(bug_id)
    repo_path = config[project]['repo_path']

    # src_dir = config[project]['src_dir']
    # test_prefix = config[project]['test_prefix']
    test_prefix = None
    valid_tests = 0
    success_tests = 0
    print(bug_id)
    test_patch_dir = os.path.abspath(os.path.join(
        './collected/test_diff', f'{bug_id}.diff'))
    
    pid = get_project_id_from_project (project)

    valid_tests, specified_repo_path, modules = verify_in_buggy_version(
        buggy_commit, test_patch_dir, repo_path, test_prefix, build, pid)

    success_tests = verify_in_fixed_version(
        fixed_commit, valid_tests, specified_repo_path, test_prefix, build, modules, pid)

    print("valid: ", valid_tests, "success: ", success_tests)
    return valid_tests, success_tests

def fetch_test_diff (report_map):

    new_cleaned_data = {}

    repo_path = ""
    if not os.path.isdir("collected/test_diff"):
        os.makedirs("collected/test_diff")

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
            

def fetch_prod_diff (report_map):
    
    if not os.path.isdir("collected/prod_diff"):
        os.makedirs("collected/prod_diff")
    
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

    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default="report.json")
    args = parser.parse_args()

    if not os.path.isdir("unverified"):
        os.makedirs("unverified")

    with open(args.file, 'r') as f:
        report_test_mappings = json.load(f)
    #print(report_test_mappings)
    fetch_test_diff(report_test_mappings)
    fetch_prod_diff(report_test_mappings)
    # exit(0)

    projects = report_test_mappings.keys()

    file_names = []

    for repo_name in projects:
        print(repo_name)
        dataset = report_test_mappings[repo_name]
        report = copy.deepcopy(report_test_mappings[repo_name])


        for bug_id in tqdm(dataset):
            buggy_commit = report_test_mappings[repo_name][bug_id]['buggy_commit']
            fixed_commit = report_test_mappings[repo_name][bug_id]['merge_commit']

            valid_tests, success_tests = verify_bug(
                bug_id, buggy_commit, fixed_commit)

            report[bug_id]['execution_result'] = {
                'valid_tests': valid_tests,
                'success_tests': success_tests,
            }

    
        verified_bugs = {}

        for bug_id, bug_info in report.items():
            if len(bug_info['execution_result']['success_tests']) > 0:
                verified_bugs[bug_id] = bug_info

        #print("total bugs: ", len(verified_bugs))

        file_name = f"unverified/unverified_bugs_{repo_name}.json"

        if len(verified_bugs) > 0:
            with open(file_name, 'w') as f:
                json.dump(verified_bugs, f, indent=2)
            
            file_names.append(file_name)
    
    # Remove redundant diff files
            
    cur_dir = os.getcwd()

    bug_names = []

    for file_name in file_names:
        
        with open(file_name, "r") as f:
            bug_list = json.load(f)

        bug_names += bug_list.keys()

    all_diff_list = os.listdir(cur_dir + "/collected/test_diff")

    collected_test_diff = cur_dir + "/collected/test_diff"
    collected_prod_diff = cur_dir + "/collected/prod_diff"

    data_test_diff = cur_dir + "/data/test_diff"
    data_prod_diff = cur_dir + "/data/prod_diff"

    for bug in bug_names:
        shutil.move(f"{cur_dir}/collected/test_diff/{bug}.diff", f"{cur_dir}/data/test_diff/{bug}.diff")
        if os.path.isfile(f"{cur_dir}/collected/prod_diff/{bug}.diff"):
            shutil.move(f"{cur_dir}/collected/prod_diff/{bug}.diff", f"{cur_dir}/data/prod_diff/{bug}.diff")

    #subprocess.run(["rm", "-rf", f"{cur_dir}/collected"])

    ### Auto - Verify

    unverified_bugs = []

    for bug_name in bug_names:
        bug_number = bug_name.split("-")[-1]
        owner_name = bug_name.replace("-" + bug_number, "")

        with open(f"verified_bug/verified_bugs_{owner_name}.json", "r") as f:
            v_b = json.load(f)
        
        with open(f"unverified/unverified_bugs_{owner_name}.json", "r") as ff:
            n_v_b = json.load(ff)
        
        if bug_name not in v_b.keys():
            unverified_bugs.append(bug_name)
        
        v_b[bug_name] = n_v_b[bug_name]

        with open(f"verified_bug/verified_bugs_{owner_name}.json", "w") as f:
            json.dump(v_b, f, indent=2)
        
    
    subprocess.run([sys.executable, "debug/collector.py"], stdout=subprocess.PIPE)

    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)
    
    wrong_bugs = []

    for bug_name in bug_names:
        name_number = bug_name.split("_")[1]
        bug_number = name_number.split("-")[-1]
        pid = name_number.replace("-" + bug_number, "")

        commit_db = project_id[pid]["commit_db"]
        commit_db = pd.read_csv(commit_db)

        bug_id = commit_db.loc[commit_db['report.id'] == bug_name]["bug_id"].values[0]

        delete_testing = shlex.split("rm -rf testing")
        subprocess.run(delete_testing)
        checkout = shlex.split(f"{sys.executable} cli.py checkout -p {pid} -v {bug_id}b -w /root/framework/testing")
        subprocess.run(checkout, stdout=subprocess.PIPE)
        compil = shlex.split(f"{sys.executable} cli.py compile -w /root/framework/testing")
        compile_err = subprocess.run(compil, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        compile_err = compile_err.stderr.decode()
        if len(compile_err) > 0:
            print("compile error")
            wrong_bugs.append(bug_name)
            continue

        test = shlex.split(f"{sys.executable} cli.py test -w /root/framework/testing -q")
        test_output = subprocess.run(test, stdout=subprocess.PIPE)

        test_output = test_output.stdout.decode()

        if test_output.find("Failure") == -1:
             print("no failure for buggy version")
             wrong_bugs.append(bug_name)
             continue

        subprocess.run(delete_testing)
        checkout = shlex.split(f"{sys.executable} cli.py checkout -p {pid} -v {bug_id}f -w /root/framework/testing")
        subprocess.run(checkout, stdout=subprocess.PIPE)
        compil = shlex.split(f"{sys.executable} cli.py compile -w /root/framework/testing")
        compile_err = subprocess.run(compil, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        compile_err = compile_err.stderr.decode()
        
        if len(compile_err) > 0:
            print("compile error")
            wrong_bugs.append(bug_name)
            continue
        
        test = shlex.split(f"{sys.executable} cli.py test -w /root/framework/testing -q")
        test_output = subprocess.run(test, stdout=subprocess.PIPE)
        test_output = test_output.stdout.decode()
        if test_output.find("Failure") != -1:
            print("failure for fixed version")
            wrong_bugs.append(bug_name)
            continue

    for wb in wrong_bugs:
        print("wrong bug: ", wb)

    if len(wrong_bugs) == 0:
        print("no wrong bug")

    for wrong_bug in wrong_bugs:
        bug_number = wrong_bug.split("-")[-1]
        owner_name = wrong_bug.replace("-" + bug_number, "")

        with open(f"unverified/unverified_bugs_{owner_name}.json", "r") as f:
            v_b = json.load(f)
        
        del v_b[wrong_bug]

        with open(f"unverified/unverified_bugs_{owner_name}.json", "w") as f:
            json.dump(v_b, f, indent=2)
    

    for bug_name in unverified_bugs:
        bug_number = bug_name.split("-")[-1]
        owner_name = bug_name.replace("-" + bug_number, "")

        with open(f"verified_bug/verified_bugs_{owner_name}.json", "r") as f:
            v_b = json.load(f)
        
        del v_b[bug_name]

        with open(f"verified_bug/verified_bugs_{owner_name}.json", "w") as f:
            json.dump(v_b, f, indent=2)

    subprocess.run([sys.executable, "debug/collector.py"], stdout=subprocess.PIPE)
    delete_testing = shlex.split("rm -rf testing")
    subprocess.run(delete_testing)