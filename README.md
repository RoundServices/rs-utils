# rs-utils

Modules used across all RS IAM deployment projects

## Setup

### Pre-requisites

- Python > 3.x
- python-devel
- pip3 (package-management system)

## Deploy

```sh
python3 -m pip install --upgrade --force-reinstall git+https://github.com/RoundServices/rs-utils.git@main
```

## Coding

All classes contained in **rs** folder can be used for develop awesome scripts or classes, just import the dependencies on your python code:
```python
from rs.package.MyClass import MyClass
```
