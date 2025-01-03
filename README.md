# JSON argparse

## Feature

- Load json as args
- Save args to json
- Convert arg parser to json-schema (fork and modify from [argparse-to-json](https://github.com/childsish/argparse-to-json))
- Convert json-schema to arg parser (fork and modify from [argparse-schema](https://github.com/FebruaryBreeze/argparse-schema))

## Install

```shell
pip install json-arg
```
Or use poetry
```shell
poetry add json-arg
```

## Usage

### Setup a parser

Set up a parser and wrap it

```python
import argparse
from json_arg import Parser

parser = argparse.ArgumentParser()
parser.add_argument("name")
json_argparser = Parser(parser)
# use `json_argparser.parser` to get the wrapped one
```

Set up a parser from json-schema

```python
from json_arg import Parser

# Use dict as json
json_schema: dict = {}
json_argparser = Parser(schema=json_schema)

# Or from a path
json_schema_path = "./config.json"
json_argparser = Parser(schema=json_schema_path)
```

Add json-schema to existed parser

```python
json_schema_path = "./config.json"
json_argparser.add_json_schema(schema = json_schema_path)
```

### Load json as args
The format of json you can find which in saving args firstly.

Add argument `--json-load` for load json as args:

```python
json_argparser.add_argument_json_load()

# get args result
args = json_argparser.parse_args()
```

Using in commandline is like below.

```shell
python main.py --json-load ./config.json
```

### Save args to json

Add argument `--json-save` for save args as json:

```python
json_argparser.add_argument_json_save()
```

Using in commandline, you just add the `--json-save /path/file.json` after the command.

Otherwise, if you just add `--json-save`, it will be saved in `./run_config.json`.

```shell
python main.py --other argument --json-save ./config.json
```

Then you will find the json file in `config.json`

```json
{
  "other": "argument"
}
```

### Convert arg parser to json-schema
To dict.

```python
from json_arg import Parser

# wrapped the existed parser
json_argparser = Parser(parser)
json_args = json_argparser.to_json_schema()
json_argparser.save_json_schema()
```

To string.
```python
json_args = json_argparser.save_json_schema()
```

Save as json-schema file.

```python
json_argparser.save_json_schema("./file.json")
```
## TODO List:

- [x] The test of argparse-to-schema and schema-to-argparse
- [x] The test of load-from-json and save-to-json
- [x] The positional argument of argparse-to-schema, 
- [x] The subcommand support of schema-to-argparse
- [x] The subcommand support of load-from-json
- [ ] Support nargs in schema
- [ ] More tests in nested subcommand of argparse-to-schema