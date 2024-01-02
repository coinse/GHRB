# GHRB: GitHub Recent Bugs

GitHub Recent Bugs (GHRB) is a collection of real-world bugs merged _after_
the OpenAI LLM training cutoff point (Sep. 2021), along with a command-line
interface to easily execute code. It was constructed to facilitate
evaluation of LLM-based automated debugging techniques, free from concern
of training data contamination.

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

## Using Fetch/Filter Scripts

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

With the pull request information, gather the actual pull request data with:

```bash
python collect_raw_data.py --api_token <github_api_token> --repository_file <repo_info_file> --date <cut_off_date>
```

`<cut_off_date>` should be in the format `YYYY-MM-DD', and it is the parameter for cut-off date of the pull requests (ex. Setting it to 2021-07-01 will make the script to collect pull requests created after 2021-07-01).

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


## Publication

The companion preprint for our work is here: [http://arxiv.org/abs/2310.13229](http://arxiv.org/abs/2310.13229).
