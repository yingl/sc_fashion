import argparse
import datetime as datetime
import importlib
import sys
sys.path.append('../')
import scf_database as database
import scf_queue as queue

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',
                        '--config')
    parser.add_argument('-a',
                        '--action')
    parser.add_argument('-tid',
                        '--task_id',
                        type=int,
                        default=0)
    parser.add_argument('-d',
                        '--domain')
    return parser.parse_args()

def create_task(config):
    task = database.Task(status=config.ts_new)
    task.save() # 创建新任务
    queue_ = queue.Queue(task.id, config.queue) # 创建工作队列
    sources = database.Source.select(). \
                              where(database.Source.enabled & \
                                    database.Source.url.contains(config.domain))
    for source in sources:
        job = database.Job(task_id=task.id, \
                           source_id=source.id, \
                           status=config.js_new) # job与task绑定
        job.save()
        queue_.put({'id': job.id, \
                    'source_id': source.id, \
                    'url': source.url})
    task.status = config.ts_inprogress
    task.jobs = len(sources)
    task.save()
    print('Task %d is scheduled with %d jobs.' % (task.id, task.jobs))

def view_task(task_id, config):
    result = database.Task.select(). \
                           where(database.Task.id == task_id)
    if result:
        task = result.get()
        if task.status == config.ts_inprogress:
            jobs = database.Job.select(). \
                                where(database.Job.task_id == task_id)
            failed = 0
            finished = 0
            unfinished = 0
            for job in jobs:
                if job.status == config.js_finished:
                    finished += 1
                elif job.status == config.js_failed:
                    failed += 1
                elif job.status == config.js_new:
                    unfinished += 1
            task.failed = failed
            task.finished = finished
            task.unfinished = unfinished
            if (task.jobs == (finished + failed)) and (unfinished == 0):
                task.status = config.ts_finished
            task.save()
            print('Task %d (%d jobs): finished %d, failed %d.' % \
                  (task.id, task.jobs, task.finished, task.failed))
        elif task.status == config.ts_finished:
            print('Task %d (%d jobs): finished %d, failed %d.' % \
                  (task.id, task.jobs, task.finished, task.failed))
        elif task.status == config.ts_new:
            print('Task %d not scheduled yet.' % task_id)
    else:
        raise Exception('Task %d not found.' % task_id)

def retry_task(task_id, config):
    result = database.Task.select(). \
                           where(database.Task.id == task_id)
    if result:
        task = result.get()
        queue_ = queue.Queue(task.id, config.queue)
        jobs = database.Job.select(). \
                            where((database.Job.task_id == task_id) & \
                                  (database.Job.status != config.js_finished))
        for job in jobs:
            source = database.Source.select(). \
                                     where(database.Source.id == job.source_id).get()
            if source.enabled:
                queue_.put({'id': job.id, \
                            'source_id': source.id, \
                            'url': source.url})
                job.status = config.js_new
                job.save()
        task.status = config.ts_inprogress
        task.save() # 进度不用管，下次调view就刷新了。
        print('Retry %d jobs of task %d' % (len(jobs), task_id))
    else:
        raise Exception('Task %d not found.' % task_id)

if __name__ == '__main__':
    args = parse_args()
    config = importlib.import_module(args.config)
    config.domain = args.domain
    database.init_database(config.db)
    if args.action == 'create':
        create_task(config)
    elif args.action == 'view':
        view_task(args.task_id, config)
    elif args.action == 'retry':
        retry_task(args.task_id, config)
    else:
        raise Exception('Unknown action: %s' % args.action)