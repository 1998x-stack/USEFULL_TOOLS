import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
from bs4 import BeautifulSoup
from notion_client import Client

# 初始化 Notion 客户端
notion = Client(auth=os.environ.get("NOTION_API_KEY"))

def create_page(parent_page_id: str, title: str):
    new_page = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": [
                {
                    "type": "text",
                    "text": {
                        "content": title
                    }
                }
            ]
        }
    }
    response = notion.pages.create(**new_page)
    return response['id']

# 将 HTML 元素转换为 Notion 块
def html_to_notion_blocks(soup):
    blocks = []
    for element in soup:
        if element.name and element.name.startswith('h'):
            level = int(element.name[1])
            text = element.get_text()
            blocks.append(create_heading_block(text, level))
        elif element.name == 'p':
            text = element.get_text()
            blocks.append(create_paragraph_block(text))
        elif element.name == 'code':
            text = element.get_text()
            blocks.append(create_code_block(text))
        elif element.name == 'pre':
            code_element = element.find('code')
            if code_element:
                text = code_element.get_text()
                blocks.append(create_code_block(text, preformatted=True))
    return blocks

def create_heading_block(text, level):
    return {
        "object": "block",
        f"heading_{level}": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": text
                    }
                }
            ]
        }
    }

def create_paragraph_block(text):
    return {
        "object": "block",
        "paragraph": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": text
                    }
                }
            ]
        }
    }

def create_code_block(text, preformatted=False):
    return {
        "object": "block",
        "code": {
            "rich_text": [
                {
                    "type": "text",
                    "text": {
                        "content": text
                    }
                }
            ],
            "language": "markdown" if preformatted else "plaintext"
        }
    }


# Markdown 转换为 Notion 块
def markdown_to_notion_blocks(markdown_text):
    html = markdown.markdown(markdown_text)
    soup = BeautifulSoup(html, features="html.parser")
    return html_to_notion_blocks(soup)

# 添加块到页面
def add_blocks_to_page(page_id: str, blocks: list):
    for block in blocks:
        notion.blocks.children.append(block_id=page_id, children=[block])


# 主函数
def main():
    parent_page_id = "dd597f1751c148a69406ed271785984f"
    page_title = "Markdown 导入页面"
    markdown_file_path = "example.md"

    # 创建页面
    page_id = create_page(parent_page_id, page_title)
    print("新页面已创建，页面ID:", page_id)

    # 读取和解析 Markdown 文件
    with open(markdown_file_path, 'r', encoding='utf-8') as file:
        markdown_text = file.read()

    blocks = markdown_to_notion_blocks(markdown_text)
    add_blocks_to_page(page_id, blocks)
    print("Markdown 内容已导入页面。")

if __name__ == "__main__":
    main()