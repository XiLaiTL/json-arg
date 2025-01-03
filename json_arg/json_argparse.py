import argparse
import json
import os
import sys
from pathlib import Path
from typing import Union, Optional, Sequence, overload, List

from json_arg.argparse_to_json import convert_parser_to_json
from json_arg.argparse_schema import parser as argparse_schema_parser

class Parser:
    def __init__(self,
                 parser:argparse.ArgumentParser=argparse.ArgumentParser(),
                 schema: Optional[Union[dict, str, Path]] = None):
        self.parser = parser
        self._add_json_load = False
        if schema is not None:
            argparse_schema_parser(self.parser, schema)

    def to_json_schema(self)->dict:
        return convert_parser_to_json(self.parser)

    def save_json_schema(self,path:Optional[Path] = None)-> str:
        json_schema = self.to_json_schema()
        json_str = json.dumps(json_schema, ensure_ascii=False, indent=4)
        if path is not None:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(json_str)
        return json_str


    def add_json_schema(self,schema: Union[dict, str, Path])->'Parser':
        argparse_schema_parser(self.parser, schema)
        return self

    def json_to_args(self,json_args: Union[dict, str, Path])->Sequence[str]:
        json_args = get_json_args(json_args)
        return  list(json_to_args(json_args,self.parser._actions))

    def parse_args(self,args: Optional[Sequence[str]] = None)->argparse.Namespace:
        if args is None:
            args = sys.argv[1:]
        if self._add_json_load:
            if args[0] == '--json-load':
                path = args[1] if len(args)>1 and isinstance(args[1],str) else os.getcwd()+"/run_config.json"
                args = self.json_to_args(path)
        res = self.parser.parse_args(args=args)
        if '--json-save' in args:
            path = res.json_save
            json_args = vars(res)
            json_args.pop('json_save')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(json_args,f, ensure_ascii=False, indent=4)
        return res

    def add_argument_json_load(self):
        self._add_json_load = True

    def add_argument_json_save(self):
        default_path = os.getcwd()+"/run_config.json"  # 获取当前工作目录作为默认值
        self.parser.add_argument('--json-save', dest="json_save", nargs="?" ,type=str, const=default_path,
                                 help=f'Path to save JSON file. Default is the current working directory: {default_path}')

def json_to_args(json_args:dict, actions: List[argparse.Action]):
    for action in actions:
        if action.dest in json_args.keys() and json_args[action.dest] is not None:
            action_name = type(action).__name__
            if action_name == '_StoreAction':
                if action.option_strings:
                   yield action.option_strings[0]
                if isinstance(json_args[action.dest],list):
                    for value in json_args[action.dest]:
                        yield str(value)
                else:
                    yield str(json_args[action.dest])
            elif action_name in ['_StoreConstAction','_StoreTrueAction','_StoreFalseAction']:
                yield action.option_strings[0]
            elif action_name == '_AppendAction':
                assert isinstance(json_args[action.dest],list),f'{action.dest} in json is not a list'
                for value in action.dest:
                    yield action.option_strings[0]
                    yield str(value)
            elif action_name == '_AppendConstAction':
                assert isinstance(json_args[action.dest], list), f'{action.dest} in json is not a list'
                for value in action.dest:
                    yield action.option_strings[0]
            elif action_name == '_SubParsersAction':
                choice = json_args[action.dest]
                yield choice
                sub_actions = action.choices[choice]._actions
                yield from json_to_args(json_args, sub_actions)

def get_json_args(json_args: Union[dict, str, Path])->dict:
    if not isinstance(json_args, dict):
        with open(str(json_args),'r', encoding='utf-8') as f:
            json_args: dict = json.load(f)
    return json_args