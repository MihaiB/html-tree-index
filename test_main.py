import copy
import main
import os, os.path
import tempfile
import unittest


def make_tree(root_dir, tree):
    """
    Creates tree under existing root_dir.

    tree keys are string names, values are bytes if files dictionaries if dirs.
    """
    for k, v in tree.items():
        item_path = os.path.join(root_dir, k)
        if type(v) is dict:
            os.mkdir(item_path)
            make_tree(item_path, v)
        elif type(v) is bytes:
            with open(item_path, mode='xb') as f:
                f.write(v)
        else:
            raise ValueError('invalid value type: ' + str(type(v)))


def read_tree(root_dir):
    tree = {}

    for item in os.scandir(root_dir):
        item_path = os.path.join(root_dir, item.name)

        if item.is_file():
            with open(item_path, 'rb') as f:
                val = f.read()
        elif item.is_dir():
            val = read_tree(item_path)
        else:
            raise ValueError('I do not know what "{}" is'.format(item.name))

        tree[item.name] = val

    return tree


def get_size(val):
    """dict or bytes"""
    if type(val) is bytes:
        return len(val)
    if type(val) is dict:
        return sum(get_size(x) for x in val.values())
    raise ValueError('invalid type: ' + str(type(val)))


def make_html(title, tree):
    html = main.get_html_start(title)

    fmt_tree = {k + '/' if type(v) is dict else k:
            main.fmt_file_size(get_size(v))
            for k, v in tree.items()}
    fmt_tree[main.INDEX_FILE_NAME] = '-'

    for k, v in sorted(fmt_tree.items()):
        html += main.get_item_html(k, v)
    html += main.html_end
    return html.encode('utf-8')


class TestProcessTree(unittest.TestCase):

    def setUp(self):
        self.root_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.root_dir.cleanup)

        self.in_tree = {
            'arts': {
                'index.html': b'This file will not be changed\n',
                'music': {
                    'a-capella': b'without accompaniment',
                    'dirty': b'muddy\n',
                },
                'painting': b'colors',
                'words': b'literature\n',
            },
            'code': {
                'programming': b'languages\n',
            },
            'chores': b'take out the trash\n'
        }
        make_tree(self.root_dir.name, self.in_tree)

    def test_make_read_tree(self):
        self.assertEqual(read_tree(self.root_dir.name), self.in_tree)

    def test_process_tree(self):
        main.process_tree(self.root_dir.name, '<hobbies>')

        self.out_tree = copy.deepcopy(self.in_tree)
        self.out_tree['arts']['music']['index.html'] = make_html('music',
                self.out_tree['arts']['music'])
        self.out_tree['code']['index.html'] = make_html('code',
                self.out_tree['code'])
        self.out_tree['index.html'] = make_html('<hobbies>', self.out_tree)

        self.assertEqual(read_tree(self.root_dir.name), self.out_tree)
