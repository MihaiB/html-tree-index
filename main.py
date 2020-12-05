#! /usr/bin/env python3

import argparse
import html
import humansize
import os, os.path
import string
import urllib.parse

INDEX_FILE_NAME = 'index.html'


def parseArgs():
    p = argparse.ArgumentParser(description=f'''Create {INDEX_FILE_NAME} files
            in a directory tree.''',
            epilog=f'Existing {INDEX_FILE_NAME} files are not overwritten.')
    p.add_argument('dir', help='The root of the directory tree to process')
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

def getItemHtml(name, filesize):
    """
    >>> print(getItemHtml('"/\\'<&', 7), end='')
        <a href="%22/%27%3C%26">&quot;/&#x27;&lt;&amp;</a> 7 B<br>
    """
    size_str = '{} {}'.format(*humansize.approxFileSize(filesize))

    return itemTempl.substitute({
        'href': urllib.parse.quote(name),
        'name': html.escape(name),
        'size': html.escape(size_str),
        })


def processTree(root, title):
    """
    Process the directory tree at root and return its size.

    The index page at root uses ‘title’.
    The returned size does not include the index pages we created.
    """
    itemSize = {}
    for entry in os.scandir(root):
        if entry.is_dir():
            itemSize[entry.name + '/'] = processTree(
                    os.path.join(root, entry.name), entry.name)
        elif entry.is_file():
            itemSize[entry.name] = entry.stat().st_size

    try:
        with open(os.path.join(root, INDEX_FILE_NAME),
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
    processTree(args.dir, '/')


if __name__ == '__main__':
    main()
