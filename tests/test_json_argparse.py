import argparse
import unittest

from json_arg import Parser


class JsonArgparseTestCase(unittest.TestCase):
    def test_json_schema_multi_sub(self):
        parser = argparse.ArgumentParser(description="示例程序，包含 add 和 subtract 子命令")

        # 创建子命令解析器
        subparsers = parser.add_subparsers(dest="command", help="子命令")

        # 创建 add 子命令解析器
        parser_add = subparsers.add_parser('add', help='执行加法运算')
        parser_add.add_argument('x', type=int, help='第一个整数')
        parser_add.add_argument('y', type=int, help='第二个整数')

        # 创建 subtract 子命令解析器
        parser_subtract = subparsers.add_parser('subtract', help='执行减法运算')
        parser_subtract.add_argument('x', type=int, help='被减数')
        parser_subtract.add_argument('y', type=int, help='减数')
        json_schema_parser = Parser(parser)

        # 解析命令行参数
        print(json_schema_parser.save_json_schema())

    def test_json_schema(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command', required=True, help='Sub-commands for this script.')
        json_parser = subparsers.add_parser('json', help='Process input from a JSON file.')
        json_parser.add_argument('json_file', type=str, help='Path to the JSON file.')
        parser.add_argument("name", type=str)
        parser.add_argument("--test", "-t", type=bool)

        json_schema_parser = Parser(parser)
        json_schema_parser.save_json_schema('./schema.json')
        first_schema = json_schema_parser.to_json_schema()

        json_schema_parser_after = Parser(schema='./schema.json')
        second_schema = json_schema_parser_after.to_json_schema()
        self.assertEqual(first_schema,second_schema)

    def test_save_and_load_json(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command', required=True, help='Sub-commands for this script.')
        json_parser = subparsers.add_parser('json', help='Process input from a JSON file.')
        json_parser.add_argument('json_file', type=str, help='Path to the JSON file.')
        parser.add_argument("name", type=str)
        parser.add_argument("--test", "-t", type=bool)
        json_schema_parser = Parser(parser)
        json_schema_parser.add_argument_json_save()
        json_schema_parser.add_argument_json_load()
        # json_schema_parser.parse_args(["json","/path/this","name","--json-save"])
        print(json_schema_parser.json_to_args("./run_config.json"))
        args = json_schema_parser.parse_args(["--json-load","./run_config.json"])
        print(args)


    def test_nargs(self):
        parser = argparse.ArgumentParser(description='Example of nargs usage.')
        parser.add_argument('--foo', nargs='*', help='Zero or more FOO values.')
        parser.add_argument('--bar', nargs='+', help='One or more BAR values.')
        parser.add_argument('--baz', nargs=2, help='Exactly two BAZ values.')
        print(parser._actions)
        json_schema_parser = Parser(parser)
        # json_schema_parser.add_argument_json_save()
        # json_schema_parser.parse_args(["--foo" ,"a" ,"b" ,"c", "--bar", "1", "2" ,"3" ,"--baz" ,"x" ,'y',"--json-save"])
        print(json_schema_parser.json_to_args("./run_config.json"))