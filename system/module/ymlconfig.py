import os
import sys
import yaml
import argparse


def get_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-env', choices=['PROD', 'PREPROD', 'UAT', 'DEV', 'LOCAL'],
                            default='DEV')
    arg_parser.add_argument('-debug', choices=['DEBUG', 'INFO', 'WARNING'], default='DEBUG')
    arg_parser.add_argument('-name', default='')
    args = sys.argv[1:]
    if args and args[0].startswith('test'):  # This is args from tests, skip them
        args = args[1:]
    args = arg_parser.parse_args(args)
    args_name = f'_{args.name}' if args.name else ''
    cfg_file = f'./config_{args.env}{args_name}.yml'
    return cfg_file, args


class YmlConfig:
    def __init__(self, cfg_name_file='./config.yml', args=None):
        self.args = args
        with open(os.environ.get('ENGINE_CONFIG') or cfg_name_file, encoding='utf8') as f:
            self.config = yaml.safe_load(f)

    def __getattr__(self, name: str):
        return self.config.get(name.lower())
