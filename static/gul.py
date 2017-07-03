
import functools
import argparse
import logging

__tasks = {}


def task(task_name: str):
    global __tasks
    def decorator(f):
        __tasks[task_name] = f
        return f
    return decorator


@task('all')
def all():
    global __tasks
    for f in __tasks.values():
        f()


def run():
    """Run the gulpy copy."""
    global __tasks
    parser = argparse.ArgumentParser(description='Run gulpy tasks.')
    parser.add_argument('task', metavar='T', type=str,
                    help='Specify name of task')
    args = parser.parse_args()
    logging.info('Running task %s' % args.task)
    __tasks[args.task]()
