# rs-utils
Modules used across all RS IAM deployment projects

## Setup

### Pre-requisites
- Python > 3.x
- python-devel
- pip3 (package-management system)

## Deploy
To install/upgrade Round Services &copy; python-commons library, execute the following command on your server

- SSH deploy (last version)
```sh
pip install --upgrade git+ssh://git@github.com:RoundServices/rs-utils.git@master
```
- HTTPS deploy
```sh
pip install --upgrade git+https://github.com/RoundServices/rs-utils.git@master
```

- zip file downloaded from github
```sh
unzip -d ./ ./rs-utils-main.zip
pip3 install --upgrade --force-reinstall ./rs-utils-main/.
rm -rf ./rs-utils-main/
```

## Coding

All classes contained in **rs** folder can be used for develop awesome scripts or classes, just import the dependencies on your python code:
```python
from rs.package.MyClass import MyClass
```
