#!/usr/bin/python3.9

import os
import json
from os import path
from collections import defaultdict
from tqdm import tqdm
import glob
import shlex

#from util import config, fix_build_env
import re
import subprocess as sp
import argparse
import pandas as pd

def call_info(pid, bid):

    '''
    Summary of configuration for Project: {pid}
    ------------------------------------------
        Script dir: .../framework
        Base dir:   ...
        Major root: .../major
        Repo dir:   .../project_repos
    ------------------------------------------
        Project ID: 
        Program:    (name)
        Buildfile:  .../framework/projects/{pid}/{pid}.build.xml
    ------------------------------------------
        Number of bugs: 
        Commit db:
    '''

    '''
    bug_id, revision.id.buggy, revision.id.fixed, report.id, report.url
    '''
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)
    
    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    owner = project_id[pid]["owner"]
    number_of_bugs = project_id[pid]["number_of_bugs"]
    commit_db = project_id[pid]["commit_db"]
    repo_path = project_id[pid]["repo_path"]


    output= (f'''
    Summary of configuration for Project: {pid}
    ------------------------------------------
        Repo dir:   {repo_path}
    ------------------------------------------
        Project ID: {pid}
        Program:    {owner}
        Buildfile:  .../framework/projects/{pid}/{pid}.build.xml
    ------------------------------------------
        No. of bugs:    {number_of_bugs}
        Commit db:      {commit_db}
    ''')

    

    if bid is not None:
        active_bugs = pd.read_csv(commit_db)
        with open(f"verified_bug/verified_bugs_{owner}_{pid}.json", "r") as f:
            extra_info = json.load(f)

        with open(f"/root/framework/data/bug_cause.json", "r") as f:
            bug_cause = json.load(f)
        
        
        for b_id in bid:
            revision_id_fixed = active_bugs.loc[active_bugs['bug_id'] == int(b_id)]["revision.id.fixed"].values[0]
            revision_id_buggy = active_bugs.loc[active_bugs['bug_id'] == int(b_id)]["revision.id.buggy"].values[0]
            report_id = active_bugs.loc[active_bugs['bug_id'] == int(b_id)]["report.id"].values[0]
            report_url = active_bugs.loc[active_bugs['bug_id'] == int(b_id)]["report.url"].values[0]
            root_cause = bug_cause[report_id]
            output += (f'''
    Summary for Bug: {pid}-{b_id}
    ------------------------------------------
        Revision ID (fixed version):
        {revision_id_fixed}
    ------------------------------------------
        Revision date (fixed version):
        {extra_info[report_id]['PR_createdAt']}
    ------------------------------------------
        Bug report id:
        {report_id}
    ------------------------------------------
        Bug report url:
        {report_url}
    ------------------------------------------
        Revision ID (buggy version):
        {revision_id_buggy}
    ------------------------------------------
        Root cause in triggering tests:
        {root_cause}
    ------------------------------------------
        List of modified sources:
    ''')
            for modified_file in extra_info[report_id]['changed_tests']:
                output += '\t' + modified_file + '\n'
    return output

def call_checkout(pid, vid, dir, patch):
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    commit_db = project_id[pid]["commit_db"]
    repo_path = project_id[pid]["repo_path"]

    active_bugs = pd.read_csv(commit_db)

    bid = vid[:-1]
    version = vid[-1]

    commit = None
    
    output = "" 
    abs_path = os.getcwd()
    report_id = active_bugs.loc[active_bugs['bug_id'] == int(bid)]["report.id"].values[0]

    test_patch_dir = os.path.abspath(os.path.join('./data/test_diff/', f'{report_id}.diff'))
    
    prod_diff_dir = os.path.abspath(os.path.join('./data/prod_diff/', f'{report_id}.diff'))

    if version == "b":
        #buggy version
        commit = active_bugs.loc[active_bugs['bug_id'] == int(bid)]['revision.id.buggy'].values[0]
    
    elif version == "f":
        #fixed version
        # commit = active_bugs.loc[active_bugs['bug_id'] == int(bid)]['revision.id.fixed'].values[0]
        commit = active_bugs.loc[active_bugs['bug_id'] == int(bid)]['revision.id.buggy'].values[0]

    else:
        output = "Choose 'b' for buggy version, 'f' for fixed version"
        return output
    
    ### Updating bug_cause

    # with open("bug_cause.json", "r") as f:
    #     try:
    #         bug_cause = json.load(f)
    #     except:
    #          bug_cause = defaultdict(str)

    
    # bug_cause[report_id] = ""

    # with open("bug_cause.json", "w") as f:
    #     json.dump(bug_cause, f, indent=2)

    ### Delete this part
    
    '''
    The working directory to which the buggy or fixed project version 
    shall be checked out. The working directory
    has to be either empty or a previously used working directory.

    ALL files in a previously used working directory are deleted prior 
    to checking out the requested project version.
    '''


    if commit != None:

        sp.run(['git', 'reset', '--hard', 'HEAD'],
            cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        sp.run(['git', 'clean', '-df'],
            cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

        # checkout to the buggy version and apply patch to the buggy version

        if dir is not None:
            #print("dir is not None 1")
            if not os.path.isdir(dir):
                os.mkdir(dir)

            p = sp.run(['git', 'fetch', 'origin', commit], 
                                        stderr=sp.PIPE, stdout=sp.PIPE,
                                        cwd=repo_path)

            run = sp.run(['git', f'--work-tree={dir}', 'checkout', commit, '--', '.'], cwd=repo_path)
            output += (f"Checking out \033[92m{commit}\033[0m to \033[92m{dir}\033[0m\n")
        else:
            sp.run(['git', 'checkout', commit], cwd=repo_path,
                stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            output += (f"Checking out {commit} to {repo_path}\n")
        
        # if version == "b" and patch == True:
        #     if dir is not None:
        #         #print("dir is not None 2")
        #         sp.run(['git', f'--work-tree={dir}', 'apply', '--unsafe-paths', f'--directory={dir}', 
        #                 '--ignore-space-change', '--ignore-whitespace', test_patch_dir], cwd=repo_path)
        #     else:
        #         sp.run(['git', 'apply', test_patch_dir], cwd=repo_path,
        #             stdout=sp.DEVNULL, stderr=sp.DEVNULL)

        #     output += (f"Applying patch\n")

        if (version == "b" or version == "f") and patch == True:
            if dir is not None:
                #print("dir is not None 2")
                sp.run(['git', f'--work-tree={dir}', 'apply', '--unsafe-paths', f'--directory={dir}', 
                        '--ignore-space-change', '--ignore-whitespace', test_patch_dir], cwd=repo_path)
            else:
                sp.run(['git', 'apply', test_patch_dir], cwd=repo_path,
                    stdout=sp.DEVNULL, stderr=sp.DEVNULL)

            output += (f"Applying test patch\n")

        if version == "f":
            if dir is not None:
                #print("dir is not None 2")
                sp.run(['git', f'--work-tree={dir}', 'apply', '--unsafe-paths', f'--directory={dir}', 
                        '--ignore-space-change', '--ignore-whitespace', prod_diff_dir], cwd=repo_path)
            else:
                sp.run(['git', 'apply', prod_diff_dir], cwd=repo_path,
                    stdout=sp.DEVNULL, stderr=sp.DEVNULL)

            output += (f"Applying prod diff\n")
        

        
        output += (f"Check out program version \033[4m{pid}-{vid}\033[0m\n")

        with open(f"{dir}/.ghrb.config", "w") as f:
            f.write("#File automatically generated by GHRB\n")
            f.write(f"pid={pid}\n")
            f.write(f"vid={vid}")
            f.close()
    else:
        output += "Cannot find version..."
    
    return output

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
    # if requirements["gradle"] != "0":
    #     gradle_required = requirements["gradle"]

    mvn_required = None
    mvnw = False
    gradlew = False

    if build == "maven":
        if wrapper:
            mvnw = True
            #print("Using Maven Wrapper")
        else:
            mvn_required = requirements["version"]
            #print(f"Required Maven Version: {mvn_required}")
    elif build == "gradle":
        if wrapper:
            gradlew = True
            #print("Using Gradle Wrapper")

    #print(f"Required JDK Version: {jdk_required}")

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

def call_compile(dir):
    '''
    Docker:
        maven 3.8.1, 3.8.6
        jdk 8, 11, 17
        gradle 7.6.2
    
    '''
    output = ""

    if not os.path.isfile(os.path.join(dir, ".ghrb.config")):
        output += "GHRB config file not found...\n"
        output += "Re-run compile"
        return output
    
    with open(f"{dir}/.ghrb.config", "r") as f:
        content = f.read()

    pid_pattern = r'(pid=)(.*)\n'
    out = re.search(pid_pattern, content)
    pid = out.group(2)

    # vid_pattern = r'(vid=)(.*)'
    # out = re.search(vid_pattern, content)
    # vid = out.group(2)

    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "No matching project id"
        return output

    repo_path = project_id[pid]["repo_path"]

    new_env, mvnw, gradlew = find_env(pid)

    path = repo_path if dir is None else dir
    #print(path)
    if pid == "jackson-core" or pid == "jackson-databind":
        fix_build_env(pid, path)

    if not mvnw and not gradlew:
        out = sp.run(['mvn', 'clean', 'compile'], env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, check=True, cwd=path)
    elif mvnw:
        out = sp.run(['./mvnw', 'clean', 'compile'], env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, check=True, cwd=path)
    
    elif gradlew:
        out = sp.run(['./gradlew', 'clean', 'compileJava'], env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, check=True, cwd=path)

    if "BUILD SUCCESS" in out.stdout.decode():
        output += "\033[92mBuild Success\033[0m"
    else:
        output += "\033[91mBuild Failed\033[0m"
    '''
    mvn clean install -DskipTests=true
    mvn clean package -Dmaven.buildDirectory='target'
    '''
    return output

def run_test (new_env, mvnw, gradlew, test_case, path, command=None):

    output = ""
    if not mvnw and not gradlew:
        default = ['mvn', 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
        if command is not None:
            extra_command = command.split()
            new_command = default + extra_command
            run = sp.run(new_command,
                         env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)
        else:
            run = sp.run(default,
                        env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=path)

    elif mvnw:
        default = ['./mvnw', 'test', f'-Dtest={test_case}', '-DfailIfNoTests=false', '--errors']
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
        #print("gradlew")
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
    '''
    Modify for gradle
    '''
    stdout = run.stdout.decode()
    stderr = run.stderr.decode()

    # print(stdout)
    # print(stderr)

    clean = True    ### Remove

    test_output = False
    if "BUILD SUCCESS" in stdout:
        output += (f'''
\033[1mTEST: {test_case}\033[0m 

\033[92mTest Success\033[0m
------------------------------------------------------------------------\n''')
        test_output = True
    elif "There are test failures" in stdout:
        clean = False   ### Remove
        pattern = r'\[ERROR\] Failures:(.*?)\[INFO\]\s+\[ERROR\] Tests run:'
        match = re.search(pattern, stdout, re.DOTALL)
        if match is None:
            pattern = r'\[ERROR\] Errors:(.*?)\[INFO\]\s+\[ERROR\] Tests run:'
            match = re.search(pattern, stdout, re.DOTALL)
        if match is None:
            pattern = r'Results[^\n]*\n(.*?)Tests run'
            match = re.search(pattern, stdout, re.DOTALL)
        fail_part = match.group(1).strip()
        fail_part = re.sub(r'\[ERROR\]', '', fail_part).strip()
        output += (f'''
\033[1mTEST: {test_case}\033[0m

\033[91mFailure/Error info:\033[0m
    {fail_part}
------------------------------------------------------------------------\n''')
        test_output = False
    elif 'There were failing tests' in stderr:
        clean = False
        pattern = r'Task\s+:\S+\s+FAILED\n([\s\S]*)Throwable that failed the check'
        match = re.search(pattern, stdout, re.DOTALL)
        if match is None:
            pattern = r"Successfully started process 'Gradle Test Executor \d+'(.*)\n([\s\S]*)Finished generating"
            match = re.search(pattern, stdout, re.DOTALL)
        fail_part = match.group(1).strip()
        output += (f'''
\033[1mTEST: {test_case}\033[0m

\033[91mFailure/Error info:\033[0m
    {fail_part}
------------------------------------------------------------------------\n''')
        test_output = False
    ######################################################
    ### Updating bug_cause

    # if not clean:
    #     with open("bug_cause.json", "r") as f:
    #         bug_cause = json.load(f)
        
    #     with open(f"{path}/.ghrb.config", "r") as f:
    #         content = f.read()

    #     with open("/root/framework/data/project_id.json", "r") as f:
    #         project_id = json.load(f)

    #     pid_pattern = r'(pid=)(.*)\n'
    #     out = re.search(pid_pattern, content)
    #     pid = out.group(2)

    #     vid_pattern = r'(vid=)(.*)'
    #     out = re.search(vid_pattern, content)
    #     vid = out.group(2)
    #     bid = vid[:-1]

    #     commit_db = project_id[pid]["commit_db"]

    #     active_bugs = pd.read_csv(commit_db)

    #     report_id = active_bugs.loc[active_bugs['bug_id'] == int(bid)]["report.id"].values[0]

    #     bug_cause[report_id] += fail_part

    #     with open("bug_cause.json", "w") as f:
    #         json.dump(bug_cause, f, indent=2)
    

    ### Delete this part
    ######################################################
    return output, test_output, stdout

def call_test(dir, test_case, test_class, test_suite, log, quiet):
    '''
    default is the current directory
    test_case -> By default all tests are executed
    test_suite -> The archive file name of an external test suite. 
    test_class
    '''
    output = ""

    if not os.path.isfile(os.path.join(dir, ".ghrb.config")):
        output += "GHRB config file not found...\n"
        output += "Re-run compile"
        return output
    
    with open(f"{dir}/.ghrb.config", "r") as f:
        content = f.read()

    pid_pattern = r'(pid=)(.*)\n'
    out = re.search(pid_pattern, content)
    pid = out.group(2)

    vid_pattern = r'(vid=)(.*)'
    out = re.search(vid_pattern, content)
    vid = out.group(2)
    bid = vid[:-1]

    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "No matching project id"
        return output

    commit_db = project_id[pid]["commit_db"]
    repo_path = project_id[pid]["repo_path"]

    owner = project_id[pid]["owner"]

    repo_name = owner + "_" + pid

    command = None

    if len(project_id[pid]['requirements']['extra']) != 0:
        command = project_id[pid]['requirements']['extra']['command']
    
    with open(f"verified_bug/verified_bugs_{repo_name}.json", "r") as f:
        verified_bugs = json.load(f)

    active_bugs = pd.read_csv(commit_db)
    report_id = active_bugs.loc[active_bugs['bug_id'] == int(bid)]['report.id'].values[0]
    
    target_tests = verified_bugs[report_id]["execution_result"]["success_tests"]

    new_env, mvnw, gradlew = find_env(pid)

    path = repo_path if dir is None else dir

    def find_test (input):
        for test in target_tests:
            if test.find(input) != -1:
                return test
            else:
                return None
    
    def write_output (_content, _test_output, _quiet, _output):
        if _test_output is True and _quiet is True:
            pass
        else:
            _output += _content
        return _output
            
    if test_case is not None:
        found_test_case = find_test(test_case)
        test_case = test_case.replace(":", "#")

        if found_test_case is None:
            #print("External test case")
            content, test_output, stdout = run_test(new_env, mvnw, gradlew, test_case, path, command)
            output = write_output(content, test_output, quiet, output)
        else:
            #print("Internal test case")
            content, test_output, stdout = run_test(new_env, mvnw, gradlew, test_case, path, command)
            output = write_output(content, test_output, quiet, output)
    elif test_class is not None:
        content, test_output, stdout = run_test(new_env, mvnw, gradlew, test_class, path, command)
        output = write_output(content, test_output, quiet, output)
    elif test_suite is not None:
        #print("External test suite")
        pass
    else:
        #print("Running all relevant test cases")
        for test in target_tests:
            content, test_output, stdout = run_test(new_env, mvnw, gradlew, test, path, command)
            output = write_output(content, test_output, quiet, output)


    # if test_output is True and quiet is True:
    #     output = ""

    marker = ""

    if test_case is not None:
        marker += "_" + test_case
    elif test_class is not None:
        marker += "_" + test_class
    elif test_suite is not None:
        marker += "_" + test_suite
    
    if quiet is True:
        marker += "_quiet"

    if log is True:
        if not os.path.isdir("log"):
            os.mkdir("log")
        
        with open(f"log/{pid}_{vid}{marker}.log", "w") as f:
            f.writelines(stdout)
        
        f.close()
    
    return output


def call_bid(pid, quiet):
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    number_of_bugs = project_id[pid]["number_of_bugs"]
    commit_db = project_id[pid]["commit_db"]
    output = ""
    if not quiet:
        output += f'''
    Bug Information for {pid}

    Total number of bugs: {number_of_bugs}
    ------------------------------------------
'''

    active_bugs = pd.read_csv(commit_db)

    for bug_id in active_bugs["bug_id"]:
        output += f"\t{bug_id}\n"
    
    return output

def call_pid(quiet):

    if quiet:
        output = ""
    else:
        output = '''
    Owner:\t\tProject ID
    ----------------------------------------
''' 
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)
    
    for pid in project_id.keys():
        project_name = project_id[pid]["owner"]
        if quiet:
            output += f"{pid}\n"
        else:
            output += f"    {project_name}:\t\t{pid}\n"
    
    return output

def call_env(pid):
    
    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)
    
    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    requirements = project_id[pid]["requirements"]

    output = requirements

    return output

def call_ptr(pid):

    with open("/root/framework/data/project_id.json", "r") as f:
        project_id = json.load(f)

    if pid not in project_id.keys():
        output = "Wrong project id"
        return output
    
    with open("contamination.json", "r") as f:
        portrait_result = json.load(f)

    owner = project_id[pid]["owner"]
    
    output += portrait_result[f'{owner}_{pid}']
    
    return output


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

def fix_build_env(project, path):

    pom_file = os.path.join(path, 'pom.xml')

    with open(pom_file, 'r') as f:
        content = f.read()

    if project == 'jackson-core':
        replace_map = properties_to_replace['jackson-core']
    elif project == 'jackson-databind':
        replace_map = properties_to_replace['jackson-databind']

    for unsupported_property in replace_map:
        content = re.sub(
            unsupported_property, replace_map[unsupported_property], content)

    with open(pom_file, 'w') as f:
        f.write(content)

def call_export(prop, output_file, working_dir):
    
    output = ""

    # print(working_dir)
    # call_compile(working_dir)
    # print("compile done")
    # call_test(working_dir, None, None, None, False, False)
    # print("test done")

    with open(f"{working_dir}/.ghrb.config", "r") as f:
        content = f.read()

    pid_pattern = r'(pid=)(.*)\n'
    out = re.search(pid_pattern, content)
    pid = out.group(2)

    new_env, mvnw, gradlew = find_env(pid)

    if mvnw: 
        prefix = ["./mvnw"]
    elif gradlew:
        prefix = []
    else:
        prefix = ["mvn"]

    if prop == "cp.test":
    
        if gradlew:
            command = []
        else:
            template = ["dependency:build-classpath", f"-Dmdep.outputFile={working_dir}/cp.txt", "-q"]
            command = prefix + template
    
        

        run = sp.run(command, env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=working_dir)
        
        run = sp.run(["cat", f"{working_dir}/cp.txt"], stdout=sp.PIPE, stderr=sp.PIPE, cwd=working_dir)

        output += run.stdout.decode()

        if gradlew:
            command = []
        else:
            template = ["help:evaluate", "-Dexpression=project.build.outputDirectory", "-q", "-DforceStdout"]
            command = prefix + template
        
        run = sp.run(command,
                     env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=working_dir)
        
        output += ":" + run.stdout.decode()

        if gradlew:
            command = []
        else:
            template = ["help:evaluate", "-Dexpression=project.build.testOutputDirectory", "-q", "-DforceStdout"]
            command = prefix + template

        run = sp.run(command,
                     env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=working_dir)
        output += ":" + run.stdout.decode()

        output += ":" + '/root/framework/junit-4.13.2.jar'

    
    elif prop == "dir.bin.classes":

        if gradlew:
            command = []
        else:
            template = ["help:evaluate", "-Dexpression=project.build.outputDirectory", "-q", "-DforceStdout"]
            command = prefix + template
        
        run = sp.run(command,
                     env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=working_dir)
        output += run.stdout.decode()
        # new = run.stdout.decode().split("/")
        # new[3] = new[3] + "/gson"
        # output += "/".join(new)

    elif prop == "dir.bin.tests":

        if gradlew:
            command = []
        else:
            template = ["help:evaluate", "-Dexpression=project.build.testOutputDirectory", "-q", "-DforceStdout"]
            command = prefix + template

        run = sp.run(command,
                     env=new_env, stdout=sp.PIPE, stderr=sp.PIPE, cwd=working_dir)
        output += run.stdout.decode()
        # new = run.stdout.decode().split("/")
        # new[3] = new[3] + "/gson"
        # output += "/".join(new)

    elif prop == "test-classes":

        test_working_dir = working_dir + '/target/classes/com'
        #print(working_dir)
        #files = glob.glob(working_dir, recursive=True)
        for root, dirs, files in os.walk(test_working_dir):
            for file in files:
                if file.endswith(".class"):
                    new_file = file.replace(".class", "") + "\n"
                    add = root.replace(f"{working_dir}/target/classes/", "") + '/'
                    total = (add + new_file).replace("/", ".")
                    output += total
                    
                    #output = ''
        
        test_working_dir = working_dir + '/target/test-classes/com'

        for root, dirs, files in os.walk(test_working_dir):
            for file in files:
                if file.endswith(".class"):
                    new_file = file.replace(".class", "") + "\n"
                    add = root.replace(f"{working_dir}/target/test-classes/", "") + '/'
                    total = (add + new_file).replace("/", ".")
                    output += total
                    
                    #output = ''
        with open(f"{working_dir}/test-classes.txt", "w") as f:
            f.write(output)
    return output

if __name__ == '__main__':

    default_dir = os.getcwd()

    parser = argparse.ArgumentParser(description="Command-line Interface for GHRB")

    subparsers = parser.add_subparsers(dest="command")

    #  d4j-info -p project_id [-b bug_id]
    parser_info = subparsers.add_parser('info',
                                        help="View configuration of a specific project or summary of a specific bug")
    
    parser_info.add_argument('-p', dest="project_id", action="store",
                             help="The id of the project for which the information shall be printed")
    
    parser_info.add_argument('-b', dest='bug_id', action="store", type=int, nargs="*",
                             help="The id of the bug for which the information shall be printed. Format: \d+")
    

    #  d4j-checkout -p project_id -v version_id -w work_dir
    parser_checkout = subparsers.add_parser('checkout',
                                        help="Check out a buggy or a fixed project version")

    parser_checkout.add_argument("-p", dest="project_id", action="store",
                                 help="The id of the project for which the information shall be checked out")
    
    parser_checkout.add_argument("-v", dest="version_id", action="store",
                                 help="The version id that shall be checked out. Format: \d+[bf]")
    
    parser_checkout.add_argument("-w", dest="work_dir", action="store",
                                 help="The working directory to which the buggy or fixed project version shall be checked out")
    
    parser_checkout.add_argument("-pch", dest="patch", action="store", default=True,
                                 help="(Only for buggy versions) Checkout with/without patch")
    

    # d4j-compile -- compile a checked-out project version.
    parser_compile = subparsers.add_parser('compile',
                                        help="Compile sources and developer-written tests of a buggy or a fixed project version")
    
    parser_compile.add_argument("-w", dest="work_dir", action="store",
                                help="The working directory of the checked-out project version (optional). Default is the current directory")
    

    #  d4j-test [-w work_dir] [-r | [-t single_test] [-s test_suite]]
    parser_test = subparsers.add_parser('test',
                                        help="Run a single test method or a test suite on a buggy or a fixed project version")
    
    parser_test.add_argument("-w", dest="work_dir", action="store",
                             help="The working directory of the checked-out project version (optional). Default is the current directory")
    
    parser_test.add_argument("-t", dest="single_test", action="store",
                             help="Only run this single test method (optional). By default all tests are executed. Format: <test_class>:<test_method>")
    
    parser_test.add_argument("-c", dest="test_class", action="store",
                             help="Only run this single test class (optional). Format: <test_class>")
    
    parser_test.add_argument("-s", dest="test_suite", action="store",
                             help="The archive file name of an external test suite (optional)")

    parser_test.add_argument("-l", "--log", dest="log", action='store_true',
                             help="Output a log file of the test result")
    
    parser_test.add_argument("-q", "--quiet", dest="quiet", action='store_true',
                             help="Print nothing if the test passes")
    
    #   d4j-bids -p project_id [-D|-A]

    parser_bid = subparsers.add_parser('bid',
                                       help="Print the list of available active bug IDs")
    
    parser_bid.add_argument("-p", dest='project_id', action="store",
                            help="The ID of the project for which the list of bug IDs is returned")
    
    parser_bid.add_argument("-q", "--quiet", dest='quiet', action='store_true',
                            help="Print only the bug IDs")
    
    #   d4j-pids
    
    parser_pid = subparsers.add_parser('pid',
                                       help="Print the list of available project IDs")
    
    parser_pid.add_argument("-q", "--quiet", dest="quiet", action="store_true",
                            help="Print only the Project IDs")
    
    #   d4j-env

    parser_env = subparsers.add_parser('env',
                                       help="Print the environment of each project")
    
    parser_env.add_argument("-p", dest='project_id', action="store",
                            help="The ID of the project for which the environment is returned")
    
    #   extra--portrait

    parser_portrait = subparsers.add_parser('ptr',
                                            help="Print the collected results from dataportraits.org (oldest commit for each project)")
    
    parser_portrait.add_argument("-p", dest='project_id', action="store",
                                 help="The ID of the project for which the result is returned")

    #   d4j-export

    parser_export = subparsers.add_parser('export',
                                          help="Export version-specific properties")
    
    parser_export.add_argument("-p", dest='property', action="store",
                               help="Export the values of this property")
    
    parser_export.add_argument("-o", dest='output_file', action="store",
                               help="Write output to this file")
    
    parser_export.add_argument("-w", dest='working_dir', action="store",
                               help="The working directory of the checked-out project version")
    
    args = parser.parse_args()
    #print(args)
    if args.command == "info":
        output = call_info(args.project_id, args.bug_id)
        print(output)
    elif args.command == "checkout":
        output = call_checkout(args.project_id, args.version_id, args.work_dir, args.patch)
        print(output)
    elif args.command == "compile":
        output = call_compile(args.work_dir)
        print(output)
    elif args.command == "test":
        output = call_test(args.work_dir, args.single_test, args.test_class, args.test_suite, args.log, args.quiet)
        print(output)
    elif args.command == "bid":
        output = call_bid(args.project_id, args.quiet)
        print(output)
    elif args.command == "pid":
        output = call_pid(args.quiet)
        print(output)
    elif args.command == "env":
        output = call_env(args.project_id)
        print(output)
    elif args.command == "ptr":
        output = call_ptr(args.project_id)
        print(output)
    elif args.command == "export":
        output = call_export(args.property, args.output_file, args.working_dir)
        print(output)

    
