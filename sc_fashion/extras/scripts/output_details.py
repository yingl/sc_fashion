import argparse
import importlib
import sys
import traceback
sys.path.append('../')
import scf_database as database

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',
                        '--config',
                        default='product_config')
    parser.add_argument('-f',
                        '--file')
    parser.add_argument('-b',
                        '--brand')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    brand = args.brand
    config = importlib.import_module(args.config)
    database.init_database(config.db)
    results = database.Result.select()
    with open(args.file, 'w+', encoding='utf-8') as f:
        for result in results:
            data = eval(result.content)
            if data['brand'] == brand:
                f.write(result.content + '\n')