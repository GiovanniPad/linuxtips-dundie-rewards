# Contributing to Dundie Project

Summary of project

## Guidelines

- Backwards compatibility
- Multiplataform
- Python 3 only

## Code of Conduct

- Be gentle

## How to contribute

### Fork repository

- Clock fork button on [github repo](https://github.com/geovannepad/linuxtips-dundie-rewards)

### Clone to local dev environment

```bash
git clone git@github.com:GeovannePad/linuxtips-dundie-rewards
```

### Prepare virtual env

```bash
cd dundie-rewards
make virtualenv
make install
```

### Coding style

- This project follows PEP8

### Run tests

```bash
make test
# or
make watch
```

### Commit rules

- We follow conventional commit messages ex: `[bugfix] reason #issue`.
- We required signed commits

### Pull Request Rules

- We require all tests to be passed.