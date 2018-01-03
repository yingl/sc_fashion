import argparse
import importlib
import sys
import traceback
sys.path.append('../')
import scf_database as database

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f',
                        '--file')
    parser.add_argument('-c',
                        '--config',
                        default='entry_config')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    config = importlib.import_module(args.config)
    try:
        urls = []
        with open(args.file, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line:
                    urls.append(line)
        urls = set(urls) # 原始数据去重复
        database.init_database(config.db)
        for url in urls:
            result = database.Source.select(). \
                                     where(database.Source.url == url)
            if not result:
                database.Source(url=url).save()
    except Exception as e:
        print('%s\n%s' % (e, traceback.print_exc()))
