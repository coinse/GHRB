# GHRB: GitHub Recent Bugs

GitHub Recent Bugs (GHRB) is a collection of real-world bugs merged _after_
the OpenAI LLM training cutoff point (Sep. 2021), along with a command-line
interface to easily execute code. It was constructed to facilitate
evaluation of LLM-based automated debugging techniques, free from concern
of training data contamination.

## Available Bugs

As of March 1st, 2024:

| Project | Bugs |
| ------- | ---- |
| fastjson | 1 |
| nacos | 6 |
| dubbo | 1 |
| rocketmq | 19 |
| assertj | 4 |
| checkstyle | 16 |
| jackson-core | 3 |
| jackson-databind | 5 |
| jackson-dataformat-xml | 1 |
| gson | 12 |
| sslcontext-kickstart | 6 |
| jsoup | 5 |
| openapi-generator | 6 |
| seata | 2 |
| retrofit | 1 |
| Apktool | 1 |
| **Total** | **89** |


## Setting up GHRB

First, build the docker image:
```bash
cd Docker
docker build -t ghrb_framework .
```

Next, make a docker container:
```bash
sh run_docker_container.sh
```

Inside the docker, the following commands need to be executed to complete setup:

```bash
cd /root/framework
chmod +x cli.py

cd debug
python collector.py
cd ..
```

Finally, check whether cli.py runs correctly via:
```bash
./cli.py -h
```

## Using GHRB

Some example commands for the command-line interface are as follows:

(Note that all directory paths given to the tool need to be absolute paths 
within the container.)

 1. `info` - View information about a project or a particular bug.
    *  Example: `./cli.py info -p gson`
 2. `checkout` - checkout the buggy or fixed version of a bug.
    *  Example: `./cli.py checkout -p gson -v 1b -w /root/framework/testing` 
 3. `compile` - compile the code in a directory.
    *  Example: `./cli.py compile -w /root/framework/testing`
 4. `test` - run the tests for a project.
    *  Example: `./cli.py test -w /root/framework/testing`


Information of other commands can be retrieved using the `-h` flag.

## Using Fetch/Filter Scripts

#### Fetching Metadata of Repositories

With a file that consists of a list of url to the repositories, use
```
python filter_repo.py --repository_list <link_file>
```
to collect the metadata of repositories prior to gathering pull request information. `<link_file>` should look like:

```
https://github.com/coinse/GHRB
https://github.com/coinse/libro
...
```

Note that the script will automatically filter out non-English repositories and repositories where Java consists <90% according to GitHub language statistics.
<br />

#### Fetching Pull Request Data

With the metadata of repositories, gather the actual pull request data with:

```bash
python collect_raw_data.py --api_token <github_api_token> --repository_file <repo_info_file> --date <cut_off_date>
```

`<cut_off_date>` should be in the format `YYYY-MM-DD`, and it is the parameter for cut-off date of the pull requests (ex. Setting it to 2021-07-01 will make the script to collect pull requests created after 2021-07-01).

`<repo_info_file>` should have a format like:

```jsonc

    [
        {
        "name": // name of the repo,
        "owner": 
            {
                "login": // owner of the repo
            },
        "url": // full url for git clone
        },
    ]

```

and it should be included in the repository manually. Note that each metadata item should be inside a list. An example of such file can be found under the `example/` directory.

The output of the `collect_raw_data.py` script is a json file consisting of pull requests that could possibly be reproducible. The format of the output file, with its name in the format `verified_bugs_OWNER_NAME`, is:

```jsonc

    [
        "{Owner}_{Name} (of Repository)": {
            "{Owner}_{Name}-{PR no.}": {...},
            "{Owner}_{Name}-{PR no.}": {...},
            ...
        }
    ]
```

#### Verifying the Pull Requests

The `verify_bug.py` script accounts for verifying the bugs collected from above. In short, it does the following:

* Fetch git diff of the test files (test_diff) and production files (prod_diff) of each pull request data collected from above, which are to be located in `collected/test_diff` and `collected/prod_diff` accordingly. **This can be neglected if diff files were already collected from running `collect_raw_data.py`.**
* For each pull request:
    * Checkout to the buggy commit, apply test diff only, and verify that the **test fails**.
    * Checkout to the buggy commit, apply both test diff and prod diff, and verify that the **test passes**.
* Move the diff files for the verified pull requests from above into `data/test_diff` and `data/prod_diff`

Moving the diff files to `data` directory, moving the output file of `collect_raw_data.py` to `verified_bug`, and running `collector.py` in `/debug` will make the bugs to be accessible from `./cli.py`.

The current script is specifically designed for the automated pipeline for maintenance, therefore in=n order to verify the bugs of your choice, please modify the script at your will before running.

## Maintenance

The current workflow is implemented to collect new reproducible bugs from the existing repositories at first day of each month.

## Publication

The companion preprint for our work is here: [http://arxiv.org/abs/2310.13229](http://arxiv.org/abs/2310.13229).
