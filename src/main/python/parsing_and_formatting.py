"""
Utilites for parsing and formatting TEI XML Dictionaries.
Copyright (C) 2019, 2020  ache2014

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: ache2014@gmail.com
"""
import xml.etree.ElementTree as ElementTree
import re
import unicodedata
import copy


ns = {'xmlns': 'http://www.tei-c.org/ns/1.0'}


def element_to_text(element):
    """Return a formatted text content of the TEI XML element."""
    text = ''
    complex_elements = (
        'hom', 'form', 'sense', 'etym',
        're', 'dictScrap'
        )
    simple_elements = (
        'orth', 'pron', 'hyph', 'syll', 'stress',
        'gram', 'gen', 'number', 'case', 'per', 'tsn',
        'mood', 'iType', 'pos', 'subc', 'colloc', 'quote',
        'lang', 'date', 'mentioned', 'gloss', 'ref',
        'ptr', 'usg', 'def', 'lbl', 'note', 'oRef', 'pRef'
        )

    # Format some elements specially:
    if re.match(r'''(?x)    # re.VERBOSE
        (\{.*\})?   # match any xml prefix
        (           # group for form tags
            pron         # pronunciation
            | hyph       # hyphenated form
            | syll       # syllabification of the headword
            | stress     # stress pattern for a headword
        )
        ''', element.tag) is not None:
        if (element.text is not None
            and not element.text.startswith('[')
            and not element.text.endswith(']')):
            element.text = '[{}]'.format(element.text)
    elif re.match(r'''(?x)    # re.VERBOSE
        (\{.*\})?   # match any xml prefix
        (           # group for complex elements
            gramGrp      # grammatical information
            | re         # related entry
            | etym       # etymological information
            | dictScrap  # other phrase-level elements
        )
        ''', element.tag) is not None:
        if element.text is None:
            element.text = '('
        elif not element.text.startswith('('):
            element.text = '({}'.format(element.text)
        if element.tail is None:
            element.tail = ')'
        elif not element.tail.endswith(')'):
            element.tail = '{})'.format(element.tail)

    # For simple TEI XML elements
    if (re.match(r'(\{.*\})?(\w+)', element.tag).group(2)
        in simple_elements):
        if element.text is not None:
            text += element.text.strip()
        subelements = (element_to_text(subelement)
                       for subelement in element.findall('./*')
                       if subelement is not None)
        text += ' '.join(subelements)
        if element.tail is not None:
            text += element.tail.strip()

    # For complex TEI XML elements     
    elif (re.match(r'(\{.*\})?(\w+)', element.tag).group(2)
          in complex_elements):
        if element.text is None:
            text += '<br/>'
        elif element.text is not None:
            text += '<br/>' + element.text.strip()
        subelements = (element_to_text(subelement)
                       for subelement in element.findall('./*')
                       if subelement is not None)
        text += ', '.join(subelements)
        if element.tail is not None:
            text += element.tail.strip() 

    # For other XML elements
    else:
        if element.text is not None:
            text += element.text.strip()
        subelements = (element_to_text(subelement)
                       for subelement in element.findall('./*')
                       if subelement is not None)
        text += ', '.join(subelements)
        if element.tail is not None:
            text += element.tail.strip()

    return text


def load_entries(tei_file):
    """Return a list of all entries from the TEI XML file."""
    with open(tei_file, 'r', encoding='utf-8') as fp:
        tree = ElementTree.parse(fp)
        entries = (
            tree.findall('.//xmlns:entry', ns)
            + tree.findall('.//xmlns:entryFree', ns)
            )
    return entries


def normalize_nfc(text):
    """Return NFC version of the unicode string."""
    try:
        text = unicodedata.normalize('NFC', text.strip().casefold())
    except AttributeError:
        pass
    else:
        return text


def parse_sentence(sentence):
    """Return a list of word combinations from the sentence."""
    words = re.split(r'\s+', sentence)
    words = list(map(normalize_nfc, words))
    combinations = [
        ' '.join(words[i:j])
        for i in range(len(words))
        for j in range(len(words), i, -1)
        ]
    return combinations


def have_matches(entry, words):
    """Return True if entry contains any of the words from the list."""
    forms = (
        entry.findall('.//xmlns:orth', ns)
        + entry.findall('.//xmlns:quote', ns)
        )
    for element in forms:
        if normalize_nfc(element.text) in words:
            return True


def highlight_orths_and_quoutes(entry):
    """Appends html tag to highlight translations."""
    elements = (
        entry.findall('.//xmlns:orth', ns)
        + entry.findall('.//xmlns:quote', ns)
        )
    for element in elements:
        if element.text:
            element.text = "<b>" + element.text + "</b>"


def translate(sentence, entries):
    """Scan XML entries to find matches for the sentence and return
    a list of text contents in matched entries."""
    translations = []
    words = parse_sentence(sentence)
    matches = (
        copy.deepcopy(entry)
        for entry in entries
        if have_matches(entry, words)
        )
    for entry in matches:
        highlight_orths_and_quoutes(entry)
        translations.append(element_to_text(entry))
    return translations
