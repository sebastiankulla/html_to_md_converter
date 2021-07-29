# html_to_md_converter

A small tool that converts websites (*.html-files) to Markdown (*.md-files).

## Installation
```
pip install html_to_md_converter
```


## Usage

You can convert a single html-file by
```python
from html_to_md_converter import HtmlToMdConverter
converter = HtmlToMdConverter()
converter.convert_file('file_name', 'export_folder')
```

or you can convert all html files in a folder
```python
from html_to_md_converter import HtmlToMdConverter
converter = HtmlToMdConverter()
converter.convert_all_files_in_folder('folder_name', 'export_folder')
```

or you can convert all html files in a nested directoy
```python
from html_to_md_converter import HtmlToMdConverter
converter = HtmlToMdConverter()
converter.convert_all_files_in_directory_tree('nested_directory', 'export_folder')
```
