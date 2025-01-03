import argparse
import unittest

from json_arg.argparse_to_json import convert_parser_to_json as convert


class TestConverter(unittest.TestCase):
    def test_empty_parser(self):
        parser = argparse.ArgumentParser()
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {}
        }, jsonform)

    def test_positional_argument(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input1')
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'string',
                    'required': True,
                    'positional': True
                },
            },
            'required':['input1']
        }, jsonform)

    def test_positional_int_argument(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input1', type=int)
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'integer',
                    'required': True,
                    'positional': True
                },
            },
            'required':['input1']
        }, jsonform)

    def test_positional_argument_with_choices(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input1', choices=['foo', 'bar'])
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'string',
                    'enum': ['foo', 'bar'],
                    'required': True,
                    'positional': True
                },
            },
            'required': ['input1']
        }, jsonform)

    def test_positional_file_argument(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input1', type=argparse.FileType('w'))
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'string',
                    'required': True,
                    'positional': True
                },
            },
            'required': ['input1'],
            'form': [
                {
                    'key': 'input1',
                    'type': 'file',
                    'constructor': {
                        'mode': 'w'
                    }
                }
            ],
        }, jsonform)

    def test_positional_argument_metavar(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('input1', metavar='Input')
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'string',
                    'required': True,
                    'positional': True,
                    'title': 'Input',
                },
            },
            'required': ['input1'],
        }, jsonform)

    def test_optional_argument(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input1')
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'string',
                },
            },
        }, jsonform)

    def test_optional_store_const(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input1', action='store_const', const=None)
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'boolean',
                },
            },
        }, jsonform)

    def test_optional_store_true(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input1', action='store_true')
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'boolean',
                },
            },
        }, jsonform)

    def test_optional_store_false(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input1', action='store_false')
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'boolean',
                },
            },
        }, jsonform)

    def test_optional_append(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input1', action='append')
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                    }
                },
            },
        }, jsonform)

    def test_optional_append_const(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--input1', action='append_const', const=None)
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'input1': {
                    'type': 'array',
                    'items': {
                        'type': 'boolean',
                    }
                },
            },
        }, jsonform)

    def test_subparsers(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers()
        subparsers.add_parser('subparser1')
        subparsers.add_parser('subparser2')
        jsonform = convert(parser)
        self.assertEqual({
            'type': "object",
            'properties': {
                'subparser1': {
                    'type': 'object',
                    'properties': {},
                },
                'subparser2': {
                    'type': 'object',
                    'properties': {},
                },
            },
            'form': [
                {
                    'type': 'selectfieldset',
                    'title': 'Choose command',
                    'items': [
                        {
                            'key': 'subparser1',
                            'legend':'subparser1'
                        },
                        {
                            'key': 'subparser2',
                            'legend': 'subparser2'
                        }
                    ],
                },
            ],
        }, jsonform)
