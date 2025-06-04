# depsize

This python package helps you measure the disk space used by your python dependencies. The purpose of this package is to help you understand how much each package contributes to the size of your app, and to help you find ways to reduce the size of the app.

When used in combination with `docker image history` this tool helps you find ways to reduce the total size of the docker image.

This package has no third party dependencies. The [program](/src/depsize/depsize.py) only uses the built-in packages of python.

Supports python version 3.8 and newer.

## Install

Install depsize with your tools of choice, for example

**pip**

```bash
pip install depsize
```

or add depsize to your `requirements-dev.txt` file and install it with your other dev requirements using ` `pip install -r requirements-dev.txt`. 

**uv**

```bash
uv add depsize --dev
```

Or just copy the main python program as a script. It runs on all versions greater than and including python 3.7.

## How to use depsize

You can run the depsize package from within your application repository from the terminal by running 

Run ```depsize``` to get a description of the tool

```bash
> depsize
depsize: Get the total size of installed python dependencies in MB.
 Use 'depsize total' to get a summary including total size and the largest packages.
 Use 'depsize --o FILE' to export as JSON, f.ex 'depsize --o data/packages.json'
```

Run ```depsize total``` to print the size of all packages in MB, and name the largest:

```bash
> depsize total
Total size of all packages: 56.27 MB
==================================================
Packages larger than 1 MB:
debugpy: 27.93 MB
zmq: 4.99 MB
jedi: 4.75 MB
pygments: 4.50 MB
IPython: 3.48 MB
prompt_toolkit: 2.24 MB
tornado: 1.76 MB

Packages smaller than 1 MB: 68 packages
Combined size of packages smaller than 1 MB: 6.62 MB
```

You can store the results as a json file with ```depsize --o File```, which will contain the python packages by name, package version and size in megabytes.

```bash
> depsize --o data/packages.json
Dependencies written to data/packages.json
```

Example JSON file contents:

<details>
```json
[
  {
    "name": "appnope",
    "version": "0.1.4",
    "size_MB": 0.01
  },
  {
    "name": "asttokens",
    "version": "3.0.0",
    "size_MB": 0.02
  },
  {
    "name": "comm",
    "version": "0.2.2",
    "size_MB": 0.03
  },
  {
    "name": "debugpy",
    "version": "1.8.14",
    "size_MB": 0.04
  },
  {
    "name": "decorator",
    "version": "5.2.1",
    "size_MB": 0.02
  },
  {
    "name": "executing",
    "version": "2.2.0",
    "size_MB": 0.16
  },
  {
    "name": "ipykernel",
    "version": "6.29.5",
    "size_MB": 0.0
  },
  {
    "name": "ipython",
    "version": "9.3.0",
    "size_MB": 0.02
  },
  {
    "name": "ipython-pygments-lexers",
    "version": "1.1.1",
    "size_MB": null
  },
  {
    "name": "jedi",
    "version": "0.19.2",
    "size_MB": 0.24
  },
  {
    "name": "jupyter-client",
    "version": "8.6.3",
    "size_MB": null
  },
  {
    "name": "jupyter-core",
    "version": "5.8.1",
    "size_MB": null
  },
  {
    "name": "matplotlib-inline",
    "version": "0.1.7",
    "size_MB": null
  },
  {
    "name": "nest-asyncio",
    "version": "1.6.0",
    "size_MB": null
  },
  {
    "name": "packaging",
    "version": "25.0",
    "size_MB": 0.23
  },
  {
    "name": "parso",
    "version": "0.8.4",
    "size_MB": 0.02
  },
  {
    "name": "pexpect",
    "version": "4.9.0",
    "size_MB": 0.01
  },
  {
    "name": "platformdirs",
    "version": "4.3.8",
    "size_MB": 0.01
  },
  {
    "name": "prompt-toolkit",
    "version": "3.0.51",
    "size_MB": null
  },
  {
    "name": "psutil",
    "version": "7.0.0",
    "size_MB": 0.03
  },
  {
    "name": "ptyprocess",
    "version": "0.7.0",
    "size_MB": 0.0
  },
  {
    "name": "pure-eval",
    "version": "0.2.3",
    "size_MB": null
  },
  {
    "name": "pygments",
    "version": "2.19.1",
    "size_MB": 0.04
  },
  {
    "name": "python-dateutil",
    "version": "2.9.0.post0",
    "size_MB": null
  },
  {
    "name": "pyzmq",
    "version": "26.4.0",
    "size_MB": 0.04
  },
  {
    "name": "ruff",
    "version": "0.11.12",
    "size_MB": 0.0
  },
  {
    "name": "six",
    "version": "1.17.0",
    "size_MB": 0.03
  },
  {
    "name": "stack-data",
    "version": "0.6.3",
    "size_MB": null
  },
  {
    "name": "tornado",
    "version": "6.5.1",
    "size_MB": 1.78
  },
  {
    "name": "traitlets",
    "version": "5.14.3",
    "size_MB": 0.01
  },
  {
    "name": "wcwidth",
    "version": "0.2.13",
    "size_MB": 0.51
  }
]
```
</details>

## Developing locally

```bash
just install # to install dependencies for depsize
just build # to build depsize
uv pip install -e . # to install an editable build
```