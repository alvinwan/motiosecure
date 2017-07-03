"""Compile the website"""

import os.path
import glob
import jinja2
import subprocess
import json

from gul import task
from gul import run


@task('html')
def html():
    write_html(
        source='src/html/*.html',
        dest='dist',
        context=json.load(open('src/data/global.json')))


def write_html(source: str, dest: str, context: dict):
    """Generate all HTML from templates"""
    os.makedirs(dest, exist_ok=True)
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))
    for path in glob.iglob(source):
        filename = os.path.basename(path).split('.')[0]
        if filename == 'index':
            dest_path = os.path.join(dest, 'index.html')
        else:
            dest_path = os.path.join(
                dest, filename, 'index.html')
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, 'w') as target:
            target.write(env.get_template(path).render(context))


@task('sass')
def sass():
    write_sass(
        source='src/scss/*.scss',
        dest='dist/css'
    )


def write_sass(source: str, dest: str):
    """Compile css from sass"""
    os.makedirs(dest, exist_ok=True)
    for path in glob.iglob(source):
        dest_path = os.path.join(
            dest, os.path.basename(path).replace('.scss', '.css'))
        subprocess.call(['sass', path, dest_path])


if __name__ == '__main__':
    run()
