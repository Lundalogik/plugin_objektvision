# Objektvision

_Awesomeness in a package_


# What this plugin does

_Describe what this plugin does here..._

# Developing

## Setting up your environment

### Windows

Setting up a virtual environment:

```
C:\my-plugin>C:\Python34\python -m venv venv
C:\my-plugin>venv\scripts\activate
C:\my-plugin>pip install -r requirements_dev.txt
or
C:\my-plugin>pip install -r requirements_prod.txt
```

### Linux

The development environment is based on docker.

To build the docker image, run:

```
$ make build
```

## Running tests

### Windows 

```
C:\my-plugin>python manage.py test
```

### Linux

```
$ make test
```

## See what other commands are available

### Windows

```
C:my-plugin>python manage.py -h
```

### Linux

```
$ make help
```

## Configuration

To add default configuration options to this plugin, add them to plugin_objektvision/plugin_objektvision/__init__.py like so:

```python
def default_config():
    return {
        'my-option': 'its default value'
    }
```

These options can later be retrieved like this:

```python
import lime_config

def my_function():
    opt = lime_config.config.plugins['plugin_objektvision']['my-option']
```
