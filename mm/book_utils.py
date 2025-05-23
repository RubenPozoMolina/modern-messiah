import logging
import mimetypes
import os
import subprocess


class BookUtils:
    input_path = None
    output_path = None
    title = None
    authors = None
    cover = None
    language = None
    text_files = []
    book_type = None

    def __init__(
            self,
            input_path,
            output_path,
            title,
            authors,
            cover,
            language='es',
            book_type='epub'

    ):
        self.input_path = input_path
        self.output_path = output_path
        self.title = title
        self.authors = authors
        self.cover = cover
        self.language = language
        self.book_type = book_type
        self.get_files_recursively()

    def get_files_recursively(self):
        try:
            if not os.path.isdir(self.input_path) or not os.path.exists(
                    self.input_path):
                logging.error(
                    f"Error: {self.input_path} is not a valid directory")
            else:
                for root, dirs, files in os.walk(self.input_path):
                    dirs.sort()
                    files.sort()
                    for file in files:
                        file_path = os.path.join(root, file)
                        if mimetypes.guess_type(file)[0] == 'text/plain':
                            self.text_files.append(file_path)
        except Exception as e:
            print(f"Error scanning directory {self.input_path}: {e}")

    def get_file_name(self):
        return self.title.replace(" ", "_")

    def create_book(self):
        metadata = {
            'title': self.title,
            'authors': self.authors,
            'language': self.language,
            'cover': self.cover
        }
        html_file = self.create_html_from_text(metadata)
        return self.create_from_html(html_file, metadata, self.book_type)

    def create_html_from_text(self, metadata=None):
        html_content = [
            '<!DOCTYPE html>', '<html>', '<head>',
            '<meta charset="UTF-8">',
            f'<title>{metadata["title"]}</title>',
            '</head>', '<body>'
        ]
        html_content_index = [
            '<h1> Table of Contents </h1>',
            '<p style="text-indent:0pt">',
        ]
        html_content_chapters = []
        for text_file in self.text_files:
            try:
                with open(text_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                    chapter = []
                    chapter_id = os.path.splitext(os.path.basename(text_file))[0]
                    chapter_title = chapter_id.replace("_", " ")
                    html_content_index.append(f"<a href='#{chapter_id}'>{chapter_title}</a><br/>")
                    paragraphs = content.split('\n\n')
                    for paragraph in paragraphs:
                        paragraph = paragraph.strip()
                        if paragraph:
                            chapter.append(f'<p>{paragraph}</p>')
                    chapter = "\n".join(
                        [
                            f'<div id="{chapter_id}">',
                            f'<h1>{chapter_title}</h1>',
                            "".join(chapter),
                            "</div>"
                        ]
                    )
                    html_content_chapters.append(chapter)
            except Exception as e:
                print(f"Error processing file {text_file}: {e}")

        html_content.extend(html_content_index)
        html_content.extend(html_content_chapters)
        html_content.extend(['</body>', '</html>'])
        output_html = os.path.join(
            self.output_path,
            f'{self.get_file_name()}.html'
        )

        with open(output_html, 'w', encoding='utf-8') as html_file:
            html_file.write('\n'.join(html_content))

        return output_html

    def create_from_html(self, html_file, metadata, book_type='epub'):
        output = os.path.join(
            self.output_path,
            self.get_file_name() + '.' + book_type
        )
        cmd = [
            'ebook-convert',
            html_file,
            output,
            '--cover', metadata['cover'],
        ]
        print("cmd:", cmd)
        try:
            result = subprocess.run(
                cmd, check=True,
                capture_output=True,
                text=True
            )
            print("Successfully converted: ", result.stdout.strip())
            return output
        except subprocess.CalledProcessError as e:
            print(f"Conversion error: {e}")
            print(f"Output error: {e.stderr}")
            return None
