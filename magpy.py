import os
import shutil
import markdown
import re
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def load_toml(path):
    if not Path(path).exists():
        return {}
    try:
        import tomllib as _toml  # Python 3.11+
        with open(path, "rb") as f:
            return _toml.load(f)
    except Exception:
        try:
            import toml as _toml  # third-party package
            with open(path, "r", encoding="utf-8") as f:
                return _toml.load(f)
        except Exception:
            return {}

def generate_html_from_md(md_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content)
    return html_content

def generate_static_site(input_dir, output_dir, template_file):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_file)

    for filename in os.listdir(input_dir):
        print(f"Processing: {filename}")
        if filename.endswith('.md'):
            md_file_path = os.path.join(input_dir, filename)
            html_content = generate_html_from_md(md_file_path)

            # Render HTML content into template
            title = os.path.splitext(filename)[0].replace('-', ' ').title()
            rendered_content = template.render(title=title, content=html_content)

            # Write rendered content to corresponding file in output directory
            html_filename = os.path.splitext(filename)[0] + '.html'
            html_file_path = os.path.join(output_dir, html_filename)
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(rendered_content)

            print(f"Generated: {html_filename}")
        elif filename == 'posts':
            posts_dir = os.path.join(input_dir, filename)
            for post_filename in os.listdir(posts_dir):
                md_file_path = os.path.join(posts_dir, post_filename)
                html_content = generate_html_from_md(md_file_path)

                # Extract metadata from filename (expecting "YYYY-MM-DD-title.md")
                match = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md", post_filename)
                if match:
                    date = match.group(1)
                    title = match.group(2).replace('-', ' ').title()
                else:
                    print(f"Filename {post_filename} does not match the expected pattern.")
                    date = ""
                    title = os.path.splitext(post_filename)[0].replace('-', ' ').title()

                # Render HTML content into template once
                rendered_content = template.render(title=title, content=html_content, date=date)

                # Write rendered content to corresponding file in output directory
                html_filename = os.path.splitext(post_filename)[0] + '.html'
                html_file_path = os.path.join(output_dir, html_filename)
                with open(html_file_path, 'w', encoding='utf-8') as f:
                    f.write(rendered_content)

                print(f"Generated: {html_filename}")

        elif os.path.isfile(os.path.join(input_dir, filename)):
            src_image_path = os.path.join(input_dir, filename)
            dest_image_path = os.path.join(output_dir, filename)
            shutil.copy(src_image_path, dest_image_path)
            print(f"Copied: {filename}")

if __name__ == "__main__":
    input_directory = "input"
    output_directory = "output"
    
    config = load_toml("config.toml")
    template_file = (
        config.get("template_file")
        or config.get("template")
        or (config.get("site") or {}).get("template_file")
        or "blog.html"
    )

    generate_static_site(input_directory, output_directory, template_file)
