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


file_path = os.getcwd()

config = {
    # 'google_gson': {
    #     'repo_path': '/root/data/GHRB/repos/gson/gson/',
    #     'src_dir': 'src/main/java/',
    #     'test_prefix': 'src/test/java/',
    #     'project_name': 'google_gson',
    #     'project_id': 'gson'
    # },
    # 'assertj_assertj-core': {
    #     'repo_path': '/root/data/GHRB/repos/assertj-core/',
    #     'src_dir': 'src/main/java/',
    #     'test_prefix': 'src/test/java/',
    #     'project_name': 'assertj_assertj-core',
    #     'project_id': 'assertj'
    # },
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
    'EnterpriseQualityCoding_FizzBuzzEnterpriseEdition': {
        'repo_path': file_path + '/repos/FizzBuzzEnterpriseEdition',
        'src_dir': 'src/main/java',
        'test_prefix': 'src/test/java',
        'project_name': 'EnterpriseQualityCoding_FizzBuzzEnterpriseEdition',
        'project_id': 'FizzBuzzEnterpriseEdition'
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
        'project_name': 'iluwatar_java-design-patterns'
    },
    'dbeaver_dbeaver': {
        'repo_path': file_path + '/repos/dbeaver',
        'project_name': 'dbeaver_dbeaver'
    },
    'seata_seata': {
        'repo_path': file_path + '/repos/seata',
        'project_name': 'seata_seata'
    },
    'OpenAPITools_openapi-generator': {
        'repo_path': file_path + '/repos/openapi-generator',
        'project_name': 'OpenAPITools_openapi-generator'
    },
    'apache_shardingsphere': {
        'repo_path': file_path + '/repos/shardingsphere',
        'project_name': 'apache_shardingsphere'
    },
    'alibaba_nacos': {
        'repo_path': file_path + '/repos/nacos',
        'project_name': 'alibaba_nacos'
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
        'project_name': 'iBotPeaches_Apktool'
    },
    'spring-projects_spring-framework': {
        'repo_path': file_path + '/repos/spring-framework',
        'project_name': 'spring-projects_spring-framework'
    },
    'termux_termux-app': {
        'repo_path': file_path + '/repos/termux-app',
        'project_name': 'termux_termux-app'
    },
    'bumptech_glide': {
        'repo_path': file_path + '/repos/glide',
        'project_name': 'bumptech_glide'
    },
    'square_retrofit': {
        'repo_path': file_path + '/repos/retrofit',
        'project_name': 'square_retrofit'
    },
    "skylot_jadx": {
        'repo_path': file_path + '/repos/jadx',
        'project_name': 'skylot_jadx'
    },
    "grpc_grpc-java": {
        'repo_path': file_path + '/repos/grpc-java',
        'project_name': 'grpc_grpc-java'
    },
    "cucumber_cucumber-jvm": {
        'repo_path': file_path + '/repos/cucumber-jvm',
        'project_name': 'cucumber_cucumber-jvm'
    },
    'javaparser_javaparser': {
        'repo_path': file_path + '/repos/javaparser',
        'project_name': 'javaparser_javaparser'
    },
    "hazelcast_hazelcast": {
        'repo_path': file_path + '/repos/hazelcast',
        'project_name': 'hazelcast_hazelcast'
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
'''
alibaba_fastjson:
    Maven 3.8.0 
    Java version 1.8.0
    git config --global --add safe.directory '*'
    wget https://archive.apache.org/dist/maven/maven-3/3.8.6/binaries/apache-maven-3.8.6-bin.tar.gz -P /tmp # for running projects in GHRB benchmark
    tar -xzvf /tmp/apache-maven-3.8.6-bin.tar.gz -C /opt
    4003 is suspicious, build fail (not because of test fail) -> build success


ReactiveX_RxJava:
    wget https://services.gradle.org/distributions/gradle-7.6.2-bin.zip -P /tmp
    unzip -d /opt/gradle /tmp/gradle-*.zip
    export GRADLE_HOME=/opt/gradle/gradle-7.6.2
    export PATH=${GRADLE_HOME}/bin:${PATH}
    JDK 11

TheAlgorithms_Java:
    JDK 17
    Maven 3.8

LMAX-Exchange_disruptor:
    gradle
'''

DEBUG = True

def get_project_from_bug_id(bug_id):
    for project_identifier in config:
        if project_identifier in bug_id:
            return project_identifier


def verify_in_buggy_version(buggy_commit, test_patch_dir, repo_path, test_prefix, build):

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
    fix_build_env(repo_path)
    
    modules = []
    # if build == 'gradle':
    #     for test_file in changed_test_files:
    #         module = test_file.split("/")
    #         src = module.index("src")
    #         module = ":".join(module[:src])
    #         modules.append(module)
    def replace_index (x):
        test_dir = x.split('/')
        
        # index = test_dir.index('test') ## change to src
        # test_dir = ".".join(test_dir[index+2:])
        # test_dir = "." + test_dir
        #test_dir = ".".join(test_dir)

        index = test_dir.index('src')
        test_dir = ".".join(test_dir[index+3:])
        test_dir = "." + test_dir
        return test_dir

    def find_repo_path (x):
        test_dir = x.split('/')
        repo = test_dir[0]
        return repo
    
    # specified_repo_path = repo_path + "/" + find_repo_path(changed_test_files[0])
    # print(specified_repo_path)
    # changed_test_id = list(map(lambda x: x.split(
    #     test_prefix)[-1].split('.')[0].replace('/', '.'), changed_test_files))
    #print(repo_path)
    changed_test_id = list(map(lambda x: replace_index(x), changed_test_files))
    #print("changed_test_id_before: ", changed_test_id)
    if build == 'gradle':
        for i in range(len(changed_test_files)):

            changed_test_id[i] = changed_test_id[i][1:]
            changed_test_id[i] = changed_test_id[i][:-5] ## change to replace

    print("changed_test_id: ", changed_test_id)
    #repo_path = repo_path + "/quarkus/"
    valid_tests = []
    for idx, test_id in enumerate(changed_test_id):

        if build == "maven":
            #sp.run(['mvn', 'clean', 'install', '-Dmaven.compiler.source=1.8', '-Dmaven.compiler.target=1.8'], stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path)
            #sp.run(['mvn', 'dependency:resolve', '-U'], cwd=repo_path)
            test_process = sp.run(['timeout', '30m', 'mvn', 'clean', 'test', '-Denforcer.skip=true',
                                f'-Dtest={test_id}', '-DfailIfNoTests=false', '-Dsurefire.failIfNoSpecifiedTests=false'], stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path)
        elif build == 'gradle':
            # module = modules[idx]
            # print(module)
            # if "x-pack" in module:
            #     continue
            test_process = sp.run(['./gradlew', 'clean', ':test',
                                '--tests', f'{test_id}'], stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path)
        elif build == "maven-specify":
            # test_process = sp.run(['timeout', '20m', 'mvn', 'clean',  '-DargLine="-Xmx1024m"', 'test', '-Dcheckstyle.skip', '-Denforcer.skip=true',
            #                     f'-Dtest={test_id}', '-DfailIfNoTests=false'], stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path)
            # test_process = sp.run(['timeout', '20m', '../mvnw', '-f', '../pom.xml',
            #                         'clean', 'test', '-Denforcer.skip=true', '-DskipExamples',
            #                     f'-Dtest={test_id}', '-DfailIfNoTests=false'], stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path)
            #run_process = sp.run(['./mvnw', 'clean', 'install', '-DskipTests'], stdout=sp.PIPE, cwd=repo_path)
            # test_process = sp.run(['timeout', '25m', './mvnw', 'clean', 'test', '-DfailIfNoTests=false', '-T1C', '-Prelease', '-Denforcer.skip=true',
            #                        '-Djacoco.skip=true', '-Dcheckstyle.skip=true', '-Drat.skip=true',
            #                        '-Dmaven.javadoc.skip=true', '-DskipTests=javaparser-core,javaparser-core-testing,javaparser-core-testing-bdd'
            #                     f'-Dtest={test_id}',
            #                     '-Dsurefire.failIfNoSpecifiedTests=false'], stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path)
            test_process = sp.run(['timeout', '10m', './mvnw', 'clean', 'test', '-DfailIfNoTests=false', '-Denforcer.skip=true',
                                   '-Djacoco.skip=true', '-Dcheckstyle.skip=true',
                                   '-Dmaven.javadoc.skip=true', "-Dargline='-Xmx1024m'",
                                f'-Dtest={test_id}',
                                '-Dsurefire.failIfNoSpecifiedTests=false'], stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path)
        
        captured_stdout = test_process.stdout.decode()
        captured_stderr = test_process.stderr.decode()

        # print(captured_stdout)
        # print(captured_stderr)


        # if DEBUG:
        #     if build == 'maven':
        #         log_content = captured_stdout
        #     elif build == 'gradle':
        #         log_content = captured_stderr
        #     os.makedirs(f'log/{repo_path.split("/")[-2]}', exist_ok=True)
        #     with open(f'./log/{repo_path.split("/")[-2]}/verify_bug_{buggy_commit}_{test_id}.log', 'w') as f:
        #         f.write(log_content)

        if build == 'maven' and 'There are test failures' in captured_stdout:
            print("There are test failures")
            valid_tests.append(test_id)
        elif build == 'maven-specify' and 'There are test failures' in captured_stdout:
            print("There are test failures")
            valid_tests.append(test_id)
        elif build == 'gradle' and 'There were failing tests' in captured_stderr:
            print("There were failing tests")
            valid_tests.append(test_id)
        

    specified_repo_path = None
    # output_repo = specified_repo_path if build=="maven-specify" else repo_path
    return valid_tests, repo_path, modules


def verify_in_fixed_version(fixed_commit, target_test_classes, repo_path, test_prefix, build, modules):
    
    sp.run(['git', 'reset', '--hard', 'HEAD'],
           cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    sp.run(['git', 'clean', '-df'],
           cwd=repo_path, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

    sp.run(['git', 'checkout', fixed_commit], cwd=repo_path)

    fix_build_env(repo_path)

    valid_tests = []

    print("target_test_classes: ", target_test_classes)
    for idx, test_id in enumerate(target_test_classes):
        print(test_id)
        if build == 'maven':
            test_process = sp.run(['mvn', 'clean', 'test', '-Denforcer.skip=true',
                                f'-Dtest={test_id}', '-DfailIfNoTests=false', '-Dsurefire.failIfNoSpecifiedTests=false'], capture_output=True, cwd=repo_path)

        elif build == 'gradle':
            # module = modules[idx]
            test_process = sp.run(['./gradlew', 'clean', ':test',
                                '--tests', f'{test_id}'], stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path)
        elif build == "maven-specify":
            test_process = sp.run(['timeout', '25m', './mvnw', 'clean', 'test', '-DfailIfNoTests=false', '-Denforcer.skip=true',
                                   '-Djacoco.skip=true', '-Dcheckstyle.skip=true',
                                   '-Dmaven.javadoc.skip=true', "-Dargline='-Xmx1024m'",
                                f'-Dtest={test_id}',
                                '-Dsurefire.failIfNoSpecifiedTests=false'], stdout=sp.PIPE, stderr=sp.PIPE, cwd=repo_path)
        captured_stdout = test_process.stdout.decode()
        captured_stderr = test_process.stderr.decode()

        # print(captured_stdout)
        # print(captured_stderr)

        if build == 'maven' and 'BUILD SUCCESS' in captured_stdout:
            print("Maven build success")
            valid_tests.append(test_id)
        elif build == 'gradle' and 'BUILD SUCCESSFUL' in captured_stdout:
            print("Gradle build success")
            valid_tests.append(test_id)
        elif build == 'maven-specify' and 'BUILD SUCCESS' in captured_stdout:
            print("Maven specify build success")
            valid_tests.append(test_id)
        elif (build=='maven-specify' or build=='maven') and 'There are test failures' in captured_stdout:
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

    #repo_path = "/root/GHRB/repos/sslcontext-kickstart"

    valid_tests, specified_repo_path, modules = verify_in_buggy_version(
        buggy_commit, test_patch_dir, repo_path, test_prefix, build)
    # print('valid test: ', valid_tests)
    success_tests = verify_in_fixed_version(
        fixed_commit, valid_tests, specified_repo_path, test_prefix, build, modules)

    print("valid: ", valid_tests, "success: ", success_tests)
    return valid_tests, success_tests


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument('projects', nargs='*', default=[])
    parser.add_argument('--bug', default=None)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--build', default='maven')
    parser.add_argument('--project', nargs="*", default=None)
    args = parser.parse_args()

    if args.debug:
        DEBUG = True

    with open('report.json') as f:
        report_test_mappings = json.load(f)


    if args.bug is not None:
        bug_id = args.bug
        repo_name = '-'.join(bug_id.split('-')[:-1])
        buggy_commit = report_test_mappings[repo_name][bug_id]['buggy_commit']
        fixed_commit = report_test_mappings[repo_name][bug_id]['merge_commit']


        valid_tests, success_tests = verify_bug(
            bug_id, buggy_commit, fixed_commit, args.build)

        print("valid test:", valid_tests)
        print("success_tests:", success_tests)

    else:
        # if len(args.projects) == 0:
        #     target_projects = [config[p]['project_name'] for p in config]

        # else:
        target_projects = [config[p]['project_name']
                            for p in args.project]
        print(target_projects)
        #repo_name = args.project
        for repo_name in target_projects:
            if os.path.exists('data-collector/report_test_mappings_w_execution_result.json'):
                with open('data-collector/report_test_mappings_w_execution_result.json') as f:
                    report_test_mappings_w_execution_result = json.load(f)
            else:
                report_test_mappings_w_execution_result = {}
            print(repo_name)
            assert repo_name in report_test_mappings.keys()

            # owner, name = repo_name.split("_")
            # link = "https://github.com/" + owner + "/" + name
            # name = os.getcwd() + '/repos/' + name
            # p = subprocess.Popen(['git', 'clone', link, name], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            report_test_mappings_w_execution_result[repo_name] = {}
            dataset = report_test_mappings[repo_name]


            for bug_id in tqdm(dataset):
                repo_name = '-'.join(bug_id.split('-')[:-1])
                buggy_commit = report_test_mappings[repo_name][bug_id]['buggy_commit']
                fixed_commit = report_test_mappings[repo_name][bug_id]['merge_commit']
                
                changed_tests = report_test_mappings[repo_name][bug_id]["changed_tests"]

                valid_tests, success_tests = verify_bug(
                    bug_id, buggy_commit, fixed_commit, args.build)

                dataset[bug_id]['execution_result'] = {
                    'valid_tests': valid_tests,
                    'success_tests': success_tests,
                }

                report_test_mappings_w_execution_result[repo_name][bug_id] = dataset[bug_id]
            
            verified_bugs = {}

            for repo_name in report_test_mappings_w_execution_result:
                for bug_id, bug_info in report_test_mappings_w_execution_result[repo_name].items():
                    if len(bug_info['execution_result']['success_tests']) > 0:
                        verified_bugs[bug_id] = bug_info
            print("total bugs: ", len(verified_bugs))
            with open(f'_verified_bugs_{repo_name}.json', 'w') as f:
                json.dump(verified_bugs, f, indent=2)