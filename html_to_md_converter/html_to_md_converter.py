from html.parser import HTMLParser
import os
import codecs
from typing import List, Tuple
from shutil import copyfile


"""

make image act as link
[![homepage][1]][2]

[1]:  http://commonmark.org/help/images/favicon.png
[2]:  http://commonmark.org "Redirect to homepage"

"""

class Converter(HTMLParser):
    md_file: str
    temp_tag: str
    code_box: bool
    div_count: int
    code_box_div_num: int
    ol_count: int
    related_data: List
    is_link: bool
    link_ref: str
    ignore_data: bool

    def __init__(self):
        super().__init__()
        self.md_file = ''
        self.code_box = False
        self.div_count = 0
        self.code_box_div_num = 0
        self.ol_count = 0
        self.temp_tag = ''
        self.related_data = []
        self.is_link = False
        self.link_ref = ''
        self.ignore_data = False

    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.md_file += '# '
        elif tag == 'b' or tag == 'strong':
            self.md_file += '**'
        elif tag == 'ul':
            self.temp_tag = 'ul'
        elif tag == 'ol':
            self.ol_count = 0
            self.temp_tag = 'ol'
        elif tag == 'li':
            if self.temp_tag == 'ul':
                self.md_file += '* '
            elif self.temp_tag == 'ol':
                self.ol_count += 1
                self.md_file += f'{self.ol_count}. '
        elif tag == 'div':
            self.div_count += 1
            attrs_dict = dict(attrs)
            if 'style' in attrs_dict and 'codeblock' in attrs_dict['style']:
                self.code_box_div_num = self.div_count
                self.code_box = True
                self.md_file += '```  \n'
        elif tag == 'a':
            self.is_link = True
            attrs_dict = dict(attrs)
            self.link_ref = attrs_dict['href']
            if not self.link_ref.startswith('http') and not self.link_ref.endswith('html') and not '@' in self.link_ref:
                self.related_data.append(self.link_ref)
        elif tag == 'img':
            attrs_dict = dict(attrs)
            img_ref = attrs_dict['src']
            alt_name = attrs_dict['alt'] if 'alt' in attrs_dict else 'Placeholder'
            if self.is_link:
                self.related_data.append(img_ref)
                self.md_file += f'[![{alt_name}]({img_ref})]({self.link_ref})'
        elif tag == 'style':
            self.ignore_data = True

    def handle_endtag(self, tag):
        if tag == 'b' or tag == 'strong':
            self.md_file += '**'
        elif tag == 'div':
            if self.code_box and self.code_box_div_num == self.div_count:
                self.code_box = False
                self.md_file += '```'
            self.div_count -= 1
            self.md_file += '  \n'
        elif tag == 'a':
            self.is_link = False
        elif tag == 'style':
            self.ignore_data = False

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.md_file += '  \n'
        elif tag == 'hr':
            self.md_file += '\n***\n'
        elif tag == 'img':
            attr_dict = dict(attrs)
            name = attr_dict['data-filename']
            path = attr_dict['src']
            self.related_data.append(path)
            self.md_file += f'![{name}]({path})'

    def handle_data(self, data):
        if self.is_link:
            self.md_file += f'[{data}]({self.link_ref})'
        elif self.ignore_data:
            pass
        else:
            self.md_file += data

    def save_file(self, filename='export.md'):
        with open(filename, 'w') as file:
            file.write(self.md_file)


class HtmlToMdConverter:
    @staticmethod
    def _convert_to_markdown(html: str) -> Tuple[str, List[str]]:
        converter = Converter()
        converter.feed(html)
        return converter.md_file, converter.related_data

    @staticmethod
    def _open_file(file):
        with codecs.open(file, 'r', 'utf-8') as file:
            return file.read()

    @staticmethod
    def _save_file(markdown_text, complete_path_to_filename, export_folder, related_data: List[str] = None):
        base_path, filename = os.path.split(complete_path_to_filename)
        new_filename = filename.replace('.html', '.md')
        if export_folder:
            new_filename = os.path.join(export_folder, new_filename)
            if not os.path.exists(export_folder):
                os.mkdir(export_folder)

            if related_data:
                for file_path in related_data:
                    abs_file_path = os.path.join(base_path, file_path)
                    new_file_path = os.path.join(export_folder, file_path)
                    dir_name = os.path.dirname(new_file_path)
                    if not os.path.exists(dir_name):
                        os.mkdir(dir_name)
                    copyfile(abs_file_path, new_file_path)

        with codecs.open(new_filename, 'w', 'utf-8') as file:
            file.write(markdown_text)

    def convert_file(self, filename, export_folder = None):
        html = self._open_file(filename)
        md_text, related_data = self._convert_to_markdown(html)
        self._save_file(md_text, filename, export_folder, related_data)

    def convert_all_files_in_folder(self, folder, export_folder=None):
        files = (file for file in os.listdir(folder) if file.endswith('.html'))
        for file in files:
            self.convert_file(file, export_folder)

    def convert_all_files_in_directory_tree(self, folder, export_folder=None):
        files_in_dir = os.listdir(folder)
        full_path_to_files = [os.path.join(folder, file) for file in files_in_dir]
        for element in full_path_to_files:
            if os.path.isfile(element) and element.endswith('.html'):
                self.convert_file(element, export_folder)
            elif os.path.isdir(element):
                sub_folder = os.path.join(folder, element)
                sub_export_folder = os.path.join(export_folder, element)
                self.convert_all_files_in_directory_tree(sub_folder, sub_export_folder)
