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

```
filter_repo.py
collect_raw_data.py
```

Above python scripts can be used to fetch and filter the pull requests. Note that these scripts can be run inside the Docker container.

<br />

If you have a file that consists of a list of url to the repositories, use
```
python filter_repo.py
```
to collect the metadata of repositories. After running the script, please provide the path to the file. An example of such 'file' would be ``` example.txt ```, where its content is:

```
https://github.com/coinse/GHRB
https://github.com/coinse/libro
...
```
<br />

If not, a file that consists of the metadata of repositories under the following format:

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

should be included in the repository manually. Note that each metadata item should be inside a list. \
An example of such file can be found under the ``` example/ ``` directory.


## Publication

The companion preprint for our work is here: [http://arxiv.org/abs/2310.13229](http://arxiv.org/abs/2310.13229).
