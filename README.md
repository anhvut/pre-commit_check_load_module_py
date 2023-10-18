# pre-commit check load module

This is a pre-commit hook that just loads python module.

### Why ?

By configuring an interpreter (virtual env) and PYTHONPATH per folder, detect early offending imports
such as using a package which is not included in virtual env, or importing a package which is not in PYTHONPATH.

### How ?

This package is based on [pre-commit](https://pre-commit.com/) framework.

#### Configure check load module

Create a configuration file `.check_load_module` in root repository folder.

```
[DEFAULT]
# optional logfile
logfile = /tmp/check_load_module.log

# add any number of section per folder to configure
[common]
# prefix of file path
prefix = common/
# python path for allowed imports in repository
PYTHONPATH = common
# interpreter path in virtual env
interpreter = ../../.venv/bin/python

[app]
prefix = app/
# separate folders with colon or semi-colon, it will be adapted depending on platform
PYTHONPATH = app:common
# if no interpreter specified, the default interpreter will be used
# for Windows/Linux compatibility, interpreter can have several values separated by a coma
# e.g. interpreter = .venv/bin/python, .venv/Scripts/python.exe
```

In this example, modules in `app/` can import modules in `common/` but the inverse is not possible.

#### Configure pre-commit to use this hook

Add this content in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/anhvut/pre-commit_check_load_module_py
    rev: 0.0.7
    hooks:
      - id: check-load-module-py
        name: Check module loads
```

Install hook:

```commandline
pre-commit install-hooks
```

Update hook version

```commandline
pre-commit autoupdate
```

### Contribute to this hook

#### Virtual env

Use poetry to install virtual env:

```commandline
poetry install
```

#### Run test

Use pytest with poetry:

```commandline
poetry run pytest
```