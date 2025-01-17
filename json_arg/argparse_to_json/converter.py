import argparse

from typing import Optional


class Converter:
    def convert(
        self,
        parser: argparse.ArgumentParser,
        schema: Optional[dict] = None,
        form: Optional[list] = None
    ) -> dict:
        schema = {} if schema is None else schema
        form = [] if form is None else form
        self.parse_parser(parser, schema, form)
        required = schema.pop('required')
        object = {
            'type': "object",
            'properties': schema,
        }
        if required is not None and len(required)>0 :
            object['required'] = required
        if parser.description is not None:
            object['description'] = parser.description
        if len(form) > 0:
            object['form'] = form
        return object

    def parse_parser(self, parser: argparse.ArgumentParser, schema: Optional[dict] = None, form: Optional[list] = None):
        schema = {} if schema is None else schema
        form = [] if form is None else form
        schema['required'] = []
        for action in parser._actions[1:]:
            self.parse_action(action, schema, form)
        return schema, form

    def parse_action(self, action: argparse.Action, schema: dict, form: list):
        action_name = type(action).__name__
        fn = {
            '_StoreAction': self.parse_store_action,
            '_StoreConstAction': self.parse_store_const_action,
            '_StoreTrueAction': self.parse_store_const_action,
            '_StoreFalseAction': self.parse_store_const_action,
            '_AppendAction': self.parse_append_action,
            '_AppendConstAction': self.parse_append_const_action,
            '_SubParsersAction': self.parse_subparsers_action,
        }[action_name]
        fn(action, schema, form)

    def parse_store_action(self, action: argparse.Action, schema: dict, form: list):
        data = {
            'type': self.get_type(action),
        }
        if not action.option_strings:
            data['positional'] = True
        if action.help:
            data['description'] = action.help
        if action.required:
            data['required'] = action.required
            schema['required'].append(action.dest)
        if action.choices:
            data['enum'] = action.choices
        if action.metavar:
            data['title'] = action.metavar
        if isinstance(action.type, argparse.FileType):
            constructor:dict = {}
            if action.type._mode != 'r':
                constructor['mode'] = action.type._mode
            if action.type._bufsize != -1:
                constructor['bufsize'] = action.type._bufsize
            if action.type._encoding is not None:
                constructor['encoding'] = action.type._encoding
            if action.type._errors is not None:
                constructor['errors'] = action.type._errors
            type_form = {
                'key': action.dest,
                'type': 'file'
            }
            if constructor:
                type_form['constructor'] = constructor
            form.append(type_form)
        schema[action.dest] = data

    def parse_store_const_action(self, action: argparse.Action, schema: dict, form: list):
        data = {
            'type': 'boolean',
        }
        if action.help:
            data['description'] = action.help
        if action.metavar:
            data['title'] = action.metavar
        schema[action.dest] = data

    def parse_append_action(self, action: argparse.Action, schema: dict, form: list):
        data = {
            'type': 'array',
            'items': {
                'type': self.get_type(action),
            },
        }
        if action.help:
            data['description'] = action.help
        if action.metavar:
            data['title'] = action.metavar
        schema[action.dest] = data

    def parse_append_const_action(self, action: argparse.Action, schema: dict, form: list):
        data = {
            'type': 'array',
            'items': {
                'type': 'boolean',
            },
        }
        if action.help:
            data['description'] = action.help
        if action.metavar:
            data['title'] = action.metavar
        schema[action.dest] = data

    def parse_subparsers_action(self, action: argparse.Action, schema: dict, form: list):
        form.append({
            'type': 'selectfieldset',
            'title': 'Choose command',
            'items': [{
                'key': name,
                'legend': name,
            } for name in action.choices],
        })
        for name, subparser in action.choices.items():
            subparser_schema, subparser_form = self.parse_parser(subparser)
            required = subparser_schema.pop('required')
            schema[name] = {
                'type': 'object',
                'properties': subparser_schema,
            }
            if required is not None and len(required)>0:
                schema[name]['required'] = required
            form.extend(subparser_form)

    def get_type(self, action):
        return 'integer' if action.type is int else 'string'
