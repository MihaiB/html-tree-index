#! /usr/bin/env python3

import argparse
import html
import humansize
import os, os.path
import string
import urllib.parse


def parseArgs():
    p = argparse.ArgumentParser(description='Create index files in dir tree.')
    p.add_argument('dir', help='Root of directory tree to process')
    p.add_argument('--index-file', default='index.html',
            help='''File name to create, default %(default)s.
            Existing files are not overwritten.''')
    return p.parse_args()


htmlStartTempl = string.Template('''\
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>$title</title>
</head>
<body>
''')

def getHtmlStart(title):
    """
    >>> print(getHtmlStart('<script>'), end='')
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>&lt;script&gt;</title>
    </head>
    <body>
    """
    return htmlStartTempl.substitute({'title': html.escape(title)})

htmlEnd = '''\
</body>
</html>
'''


itemTempl = string.Template('''\
    <a href="$href">$name</a> $size<br>
''')

def getItemHtml(name, size):
    size = '{} {}'.format(*humansize.approxFileSize(size))

    return itemTempl.substitute({
        'href': urllib.parse.quote(name),
        'name': html.escape(name),
        'size': html.escape(size),
        })


def processTree(root, title, indexFile):
    """
    Process the directory tree at root and return its size.

    The index page uses 'title'.
    The returned size does not include index pages we created.
    """
    itemSize = {}
    for entry in os.scandir(root):
        if entry.is_dir():
            itemSize[entry.name + '/'] = processTree(
                    os.path.join(root, entry.name), entry.name, indexFile)
        elif entry.is_file():
            itemSize[entry.name] = entry.stat().st_size

    try:
        with open(os.path.join(root, indexFile),
                mode='x', encoding='utf-8') as f:
            f.write(getHtmlStart(title))
            for name in sorted(itemSize):
                f.write(getItemHtml(name, itemSize[name]))
            f.write(htmlEnd)
    except FileExistsError:
        pass

    return sum(itemSize.values())


def main():
    args = parseArgs()
    processTree(args.dir, '/', args.index_file)


if __name__ == '__main__':
    main()
