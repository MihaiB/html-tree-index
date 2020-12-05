import copy
import main
import os, os.path
import tempfile
import unittest


def makeTree(rootDir, tree):
    """
    Creates tree under existing rootDir.

    tree keys are string names, values are bytes if files dictionaries if dirs.
    """
    for k, v in tree.items():
        itemPath = os.path.join(rootDir, k)
        if type(v) is dict:
            os.mkdir(itemPath)
            makeTree(itemPath, v)
        elif type(v) is bytes:
            with open(itemPath, mode='xb') as f:
                f.write(v)
        else:
            raise ValueError('invalid value type: ' + str(type(v)))


def readTree(rootDir):
    tree = {}
    for item in os.scandir(rootDir):
        itemPath = os.path.join(rootDir, item.name)

        if item.is_file():
            with open(itemPath, 'rb') as f:
                val = f.read()
        elif item.is_dir():
            val = readTree(itemPath)
        else:
            raise ValueError('I do not know what "{}" is'.format(item.name))

        tree[item.name] = val
    return tree


def getSize(val):
    """dict or bytes"""
    if type(val) is bytes:
        return len(val)
    if type(val) is dict:
        return sum(getSize(x) for x in val.values())
    raise ValueError('invalid type: ' + str(type(val)))


def makeHTML(title, tree):
    html = main.getHtmlStart(title)
    for k, v in sorted(tree.items()):
        name = k + '/' if type(v) is dict else k
        html += main.getItemHtml(name, getSize(v))
    html += main.htmlEnd
    return html.encode('utf-8')


class TestProcessTree(unittest.TestCase):

    def setUp(self):
        self.rootDir = tempfile.TemporaryDirectory()
        self.addCleanup(self.rootDir.cleanup)

        self.inTree = {
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
        makeTree(self.rootDir.name, self.inTree)

    def testMakeReadTree(self):
        self.assertEqual(readTree(self.rootDir.name), self.inTree)

    def testProcessTree(self):
        main.processTree(self.rootDir.name, '<hobbies>')

        self.outTree = copy.deepcopy(self.inTree)
        self.outTree['arts']['music']['index.html'] = makeHTML('music',
                self.inTree['arts']['music'])
        self.outTree['code']['index.html'] = makeHTML('code',
                self.inTree['code'])
        self.outTree['index.html'] = makeHTML('<hobbies>', self.inTree)

        self.assertEqual(readTree(self.rootDir.name), self.outTree)
