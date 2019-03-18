# -*- coding: utf-8 -*-

import re

WHITESPACES = re.compile(r'\s+')


def trim_text(text):
    return WHITESPACES.sub(' ', text.strip())


def truncate_text(text, min_len):
    truncate_points = {'.', '?', '!', '\n'}

    for i in range(min_len, len(text)):
        if text[i] in truncate_points:
            return text[:(i + 1)]

    return text


def json_query(json, query, default=''):
    for path in query.split('.'):
        if path in json:
            json = json[path]
        elif path.isdigit() and isinstance(json, list):
            val = int(path)
            if len(json) > val:
                json = json[val]
        else:
            return default

        if isinstance(json, list) and len(json) == 1:
            json = json[0]

    return str(json)


def walk_text(json):
    if isinstance(json, dict):
        for k, v in json.items():
            if k == 'p':
                yield from v
            else:
                yield from walk_text(v)
    elif isinstance(json, list):
        for v in json:
            yield from walk_text(v)


def walk_paragraphs(json):
    if 'section' in json:
        for section in json['section']:
            yield from walk_paragraphs(section)
    else:
        title = json_query(json, 'title')
        if 'p' in json:
            for p in json['p']:
                yield title, p


def num_symbols(json):
    return sum((len(text.strip()) for text in walk_text(json)))


def extract_book_metadata(json):
    author_fields = ['first-name', 'middle-name', 'last-name']

    author = ' '.join([json_query(json, 'title-info.author.%s' % x) for x in author_fields])
    genre = json_query(json, 'title-info.genre')
    title = json_query(json, 'title-info.book-title')
    annotation = json_query(json, 'title-info.annotation')

    return tuple(trim_text(x) for x in [title, author, genre, annotation])


def filter_body(body):
    return json_query(body, '_attr.name') not in {'comments', 'notes'}


def filter_section(section, author_last_name):
    title = json_query(section, 'title')

    for stop_word in ['сокращен', 'иллюстраци', 'список', 'данные']:
        if stop_word in title:
            return False

    #author_last_name = author_last_name[:-2]
    for p in walk_text(section):
        if author_last_name in p.lower():
            return False

    return True


def extract_paragraphs(json):
    bodies = [(num_symbols(x), x) for x in json['body'] if filter_body(x)]

    bodies.sort(key=lambda x: -x[0])
    num_sym, body = bodies[0]

    author = trim_text(json_query(json, 'title-info.author.last-name')).lower()
    top_sections = [x for x in body['section'] if filter_section(x, author)]

    for top_section in top_sections:
        yield from walk_paragraphs(top_section)
