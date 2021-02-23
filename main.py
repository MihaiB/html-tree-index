#! /usr/bin/env python3

import argparse
import html
import humansize
import os, os.path
import string
import urllib.parse

INDEX_FILE_NAME = 'index.html'


def parse_args():
    p = argparse.ArgumentParser(description=f'''Create {INDEX_FILE_NAME} files
            in a directory tree.''',
            epilog=f'Existing {INDEX_FILE_NAME} files are not overwritten.')
    p.add_argument('dir', help='The root of the directory tree to process')
    return p.parse_args()


html_start_templ = string.Template('''\
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>$title</title>
  </head>
  <body>
''')

def get_html_start(title):
    """
    >>> print(get_html_start('<script>'), end='')
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>&lt;script&gt;</title>
      </head>
      <body>
    """
    return html_start_templ.substitute({'title': html.escape(title)})

html_end = '''\
  </body>
</html>
'''


item_templ = string.Template('''\
    <a href="$href">$name</a> $size<br>
''')

def get_item_html(name, filesize):
    """
    >>> print(get_item_html('"/\\'<&', 7), end='')
        <a href="%22/%27%3C%26">&quot;/&#x27;&lt;&amp;</a> 7 B<br>
    """
    size_str = '{} {}'.format(*humansize.approx_file_size(filesize))

    return item_templ.substitute({
        'href': urllib.parse.quote(name),
        'name': html.escape(name),
        'size': html.escape(size_str),
        })


def process_tree(root, title):
    """
    Process the directory tree at root and return its size.

    The index page at root uses ‘title’.
    The returned size does not include the index pages we created.
    """
    item_size = {}
    for entry in os.scandir(root):
        if entry.is_dir():
            item_size[entry.name + '/'] = process_tree(
                    os.path.join(root, entry.name), entry.name)
        elif entry.is_file():
            item_size[entry.name] = entry.stat().st_size

    try:
        with open(os.path.join(root, INDEX_FILE_NAME),
                mode='x', encoding='utf-8') as f:
            f.write(get_html_start(title))
            for name in sorted(item_size):
                f.write(get_item_html(name, item_size[name]))
            f.write(html_end)
    except FileExistsError:
        pass

    return sum(item_size.values())


def main():
    args = parse_args()
    process_tree(args.dir, '/')


if __name__ == '__main__':
    main()
