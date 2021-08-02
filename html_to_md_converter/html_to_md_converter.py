from html.parser import HTMLParser
import os
import codecs
from typing import Tuple
from shutil import copyfile


class Converter(HTMLParser):
    md_file: str
    temp_tag: str
    code_box: bool
    div_count: int
    code_box_div_num: int
    ol_count: int
    related_data: list
    is_link: bool
    link_ref: str
    ignore_data: bool
    class_div_count: int
    ignore_div: bool

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
        self.class_div_count = 0
        self.ignore_div = False

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.md_file += '  \n'
        elif tag == 'hr':
            self.md_file += '\n***  \n'
        elif tag == 'title':
            self.md_file += '# '
        elif tag == 'h1':
            self.md_file += '# '
        elif tag == 'h2':
            self.md_file += '## '
        elif tag == 'h3':
            self.md_file += '### '
        elif tag == 'b' or tag == 'strong':
            self.md_file += '**'
        elif tag == 'ul':
            self.temp_tag = 'ul'
            self.md_file += '  \n'
        elif tag == 'ol':
            self.ol_count = 0
            self.temp_tag = 'ol'
            self.md_file += '  \n'
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
            elif 'class' in attrs_dict:
                self.class_div_count = self.div_count
                self.ignore_div = True
        elif tag == 'en-codeblock':
            self.code_box = True
            self.md_file += '\n```  \n'
        elif tag == 'a':
            self.is_link = True
            attrs_dict = dict(attrs)
            self.link_ref = attrs_dict['href']
            if not self.link_ref.startswith('http') and not self.link_ref.endswith('html') and not '@' in self.link_ref:
                self.related_data.append(self.link_ref)
        elif tag == 'style':
            self.ignore_data = True
        elif tag == 'symbol':
            self.ignore_data = True
        elif tag == 'svg':
            self.ignore_data = True
        elif tag == 'path':
            self.ignore_data = True
        elif tag == 'img':
            attrs_dict = dict(attrs)
            img_ref = attrs_dict['src']
            alt_name = attrs_dict['alt'] if 'alt' in attrs_dict else 'Placeholder'
            if self.is_link:
                self.related_data.append(img_ref)
                self.md_file += f'[![{alt_name}]({img_ref})]({self.link_ref})'
            else:
                self.related_data.append(img_ref)
                self.md_file += f'![{alt_name}]({img_ref})'

    def handle_endtag(self, tag):
        if tag == 'b' or tag == 'strong':
            self.md_file += '**  \n'
        elif tag == 'div':
            if self.code_box and self.code_box_div_num == self.div_count:
                self.code_box = False
                self.md_file += '```  \n'
            elif self.ignore_div and self.class_div_count == self.div_count:
                self.ignore_div = False
            else:
                self.md_file += '  \n'
            self.div_count -= 1
        elif tag == 'en-codeblock':
            self.code_box = False
            self.md_file += '```  \n'
        elif tag == 'a':
            self.is_link = False
        elif tag == 'style':
            self.ignore_data = False
        elif tag == 'symbol':
            self.ignore_data = False
        elif tag == 'svg':
            self.ignore_data = False
        elif tag == 'li':
            self.md_file += '  \n'

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.md_file += '  \n'
        elif tag == 'hr':
            self.md_file += '\n***  \n'
        elif tag == 'img':
            attr_dict = dict(attrs)
            name = attr_dict['data-filename']
            img_ref = attr_dict['src']
            self.related_data.append(img_ref)
            self.md_file += f'![{name}]({img_ref})'

    def handle_data(self, data):
        if self.is_link:
            self.md_file += f'[{data}]({self.link_ref})'
        elif self.ignore_data:
            pass
        else:
            self.md_file += data

    def save_file(self, filename: str='export.md') -> None:
        with open(filename, 'w') as file:
            file.write(self.md_file)


class HtmlToMdConverter:
    @staticmethod
    def _convert_to_markdown(html: str) -> Tuple[str, list[str]]:
        converter = Converter()
        converter.feed(html)
        return converter.md_file, converter.related_data

    @staticmethod
    def _open_file(file: str) -> str:
        with codecs.open(file, 'r', 'utf-8') as file:
            return file.read()

    @staticmethod
    def _save_file(markdown_text: str, complete_path_to_filename: str, export_folder: str, related_data: list[str] = None) -> None:
        base_path, filename = os.path.split(complete_path_to_filename)

        full_path_export_folder = os.path.join(base_path, export_folder)
        path_to_new_file = os.path.join(full_path_export_folder, filename).replace('.html', '.md')

        if not os.path.exists(full_path_export_folder):
            os.mkdir(full_path_export_folder)

        if related_data:
            for path_to_file in related_data:
                abs_file_path = os.path.join(base_path, path_to_file)
                if not os.path.isfile(abs_file_path):
                    continue
                new_file_path = abs_file_path.replace(base_path, full_path_export_folder)
                dir_name = os.path.dirname(new_file_path)
                if not os.path.exists(dir_name):
                    os.mkdir(dir_name)
                copyfile(abs_file_path, new_file_path)

        with codecs.open(path_to_new_file, 'w', 'utf-8') as file:
            file.write(markdown_text)

    def convert_file(self, filename: str, export_folder:str = None) -> None:
        html = self._open_file(filename)
        md_text, related_data = self._convert_to_markdown(html)
        self._save_file(md_text, filename, export_folder, related_data)

    def convert_all_files_in_folder(self, folder: str, export_folder: str = None) -> None:
        files = (file for file in os.listdir(folder) if file.endswith('.html'))
        for file in files:
            self.convert_file(file, export_folder)

    def convert_all_files_in_directory_tree(self, folder: str, export_folder: str = None) -> None:
        files_in_dir = os.listdir(folder)
        full_path_to_files = [os.path.join(folder, file) for file in files_in_dir]
        for element in full_path_to_files:
            if os.path.isfile(element) and element.endswith('.html'):
                self.convert_file(element, export_folder)
            elif os.path.isdir(element):
                sub_folder = os.path.join(folder, element)
                sub_export_folder = os.path.join(export_folder, element)
                self.convert_all_files_in_directory_tree(sub_folder, sub_export_folder)
