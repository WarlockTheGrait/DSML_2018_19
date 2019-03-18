# -*- coding: utf-8 -*-

import xml.parsers.expat
from collections import defaultdict
from io import StringIO


def _book():
    def json(actions):
        return JsonHandler(actions)

    def text():
        return TextHandler()

    def title_info():
        def author():
            return json({'first-name': text,
                         'middle-name': text,
                         'last-name': text})

        return json({'author': author,
                     'genre': text,
                     'book-title': text,
                     'annotation': text})

    def section():
        return json({'p': text,
                     'title': text,
                     'section': section})

    def body():
        return json({'section': section})

    return json({'body': body, 'title-info': title_info})


def fb2_to_json(f):
    parser = xml.parsers.expat.ParserCreate()
    book_handler = _book()

    parser.StartElementHandler = book_handler.start_element
    parser.EndElementHandler = book_handler.end_element
    parser.CharacterDataHandler = book_handler.characters

    parser.ParseFile(f)

    return book_handler.get_result()


class JsonHandler:
    def __init__(self, actions):
        self.actions = actions
        self.stack = []
        self.level = 0

        self.result = dict()

    def start_element(self, name, attr):
        if len(self.stack) > 0:
            top_action, top_level = self.stack[-1]
            top_action.start_element(name, attr)
        elif name in self.actions:
            top_action, top_level = (self.actions[name](), self.level)
            top_action.begin(attr)

            self.stack.append((top_action, top_level))

        self.level += 1

    def end_element(self, name):
        self.level -= 1

        if len(self.stack) > 0:
            top_action, top_level = self.stack[-1]
            top_action.end_element(name)

            if (name in self.actions) and (self.level == top_level):
                if name not in self.result:
                    self.result[name] = []

                top_action.end()
                action_result = top_action.get_result()
                self.result[name].append(action_result)
                self.stack.pop()

    def characters(self, data):
        if len(self.stack) > 0:
            top_action, top_level = self.stack[-1]
            top_action.characters(data)

    def get_result(self):
        return self.result

    def begin(self, attr):
        self.result['_attr'] = dict(attr)

    def end(self):
        pass


class TextHandler:
    TAG_P = 'p'
    TAG_BODY = 'body'

    TAGS_TO_IGNORE = {'title', 'subtitle', 'description', 'poem', 'v',
                      'stanza', 'image', 'binary', 'epigraph', 'a'
                      }

    STYLE_TAGS = {'style', 'strong', 'emphasis'}

    def __init__(self):
        self.cur_text = StringIO()
        self.parent_tags = defaultdict(int)
        self.result = ''

        self.is_ignore_text = 0

    def start_element(self, name, attr):
        self.parent_tags[name] += 1

        if name in TextHandler.TAGS_TO_IGNORE:
            self.is_ignore_text += 1

        if name not in TextHandler.STYLE_TAGS:
            self.cur_text.write(' ')

    def end_element(self, name):
        self.parent_tags[name] -= 1

        if name in TextHandler.TAGS_TO_IGNORE:
            self.is_ignore_text -= 1

    def characters(self, data):
        if not self.is_ignore_text > 0:
            self.cur_text.write(data)

    def get_result(self):
        return self.cur_text.getvalue()

    def begin(self, attr):
        pass

    def end(self):
        pass
