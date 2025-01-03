import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional, Sequence, Union


class Kwargs:
    def __init__(self):
        self.type = None
        self.default: Any = None
        self.required: bool = False
        self.help: Optional[str] = None
        self.action: Optional[str] = None
        self.choices: Optional[list] = None


_type_map = {
    'string': str,
    'integer': int,
    'number': float,
    'boolean': bool
}

def get_schema(schema: Union[dict, str, Path])->dict:
    if not isinstance(schema, dict):
        with open(str(schema)) as f:
            schema: dict = json.load(f)
    assert 'type' in schema and schema['type'] == 'object'
    assert 'properties' in schema
    return schema

def parser(deco_parser:argparse.ArgumentParser, schema: Union[dict, str, Path])->argparse.ArgumentParser:
    schema = get_schema(schema)
    required_set = set(schema.get('required', []))
    subparsers = None
    deco_parser.description = schema.get('description')

    file_type_map:dict = {}
    for form in schema.get('form', []):
        if ('key' in form
                and 'type' in form and form['type'] == 'file'
                and 'constructor' in form):
            file_type_map[form['key']]= argparse.FileType(**form['constructor'])

    for name, value in schema.get('properties', {}).items():
        assert isinstance(value, dict)

        kwargs = Kwargs()
        kwargs.default = value.get('default')
        kwargs.help = value.get('description')
        kwargs.required = name in required_set

        if kwargs.default is not None:
            kwargs.help = f'{kwargs.help}, [{kwargs.default}] in default'

        if 'enum' in value:
            enum_list = value['enum']
            assert len(enum_list) > 0, "Enum List is Empty"
            arg_type = type(enum_list[0])
            assert all(arg_type is type(item) for item in enum_list), f"Items in [{enum_list}] with Different Types"

            kwargs.type = arg_type
            kwargs.choices = enum_list
        elif value.get('type') == 'object': #处理subcommand去了
            subparsers = subparsers if subparsers is not None else deco_parser.add_subparsers()
            subparse = subparsers.add_parser(name=name,description=kwargs.help)
            value['form'] = schema.get('form', [])
            parser(subparse,value)
            continue
        else:
            kwargs.type = _type_map[value.get('type')]
            if value.get('type') == 'str' and name in file_type_map:
                kwargs.type = file_type_map[name]
            del kwargs.choices

        positional = value.get('positional')
        if positional:
            del kwargs.required
        else:
            name = f'--{name}'

        if kwargs.type is bool:
            assert not kwargs.default, "boolean have to be False in default"
            kwargs.default = False
            kwargs.action = 'store_true'
            del kwargs.type
        else:
            del kwargs.action

        if 'title' in value:
            kwargs.metavar = value['title']

        deco_parser.add_argument(name, **vars(kwargs))
    return deco_parser


def parse(schema: Union[dict, str, Path], args: Optional[Sequence[str]] = None) -> dict:
    _parser = parser(argparse.ArgumentParser(),schema)
    return vars(_parser.parse_args(args=args))


def main():  # pragma: no cover
    schema_path = parse(schema={
        'type': 'object',
        'properties': {
            'schema_path': {
                'type': 'string',
                'positional': True,
                'description': 'argparse schema file path'
            }
        },
        'required': [
            'schema_path'
        ],
    })['schema_path']

    sys.argv[0] = 'YOUR-COMMAND'
    print(f'Show help for schema file [{schema_path}]:')
    parse(schema=schema_path, args=['-h'])


if __name__ == '__main__':  # pragma: no cover
    main()
