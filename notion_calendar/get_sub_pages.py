import json
from pprint import pprint
from notion_client import Client
from typing import Dict, List, Any

def get_sub_pages(notion: Client, parent_page_id: str) -> List[Dict]:
    """
    获取给定页面下的所有子页面
    
    Args:
        notion (Client): Notion API 客户端
        parent_page_id (str): 父页面的ID
    
    Returns:
        List[Dict]: 所有子页面的信息列表
    """
    sub_pages = []
    try:
        # 初始化分页
        next_cursor = None
        
        while True:
            # 获取子页面，考虑分页情况
            response = notion.blocks.children.list(
                block_id=parent_page_id,
                start_cursor=next_cursor
            )
            
            # 迭代响应中的页面信息
            for block in response['results']:
                if block['type'] == 'child_page':
                    sub_pages.append({
                        "id": block["id"],
                        "title": block["child_page"]["title"],
                        "url": block.get("url", "")  # 获取页面的 URL
                    })
                    # 打印子页面信息
                    print(f"Fetched sub-page: ID = {block['id']}, Title = {block['child_page']['title']}, URL = {block.get('url', '')}")
            
            # 检查是否还有下一页
            next_cursor = response.get('next_cursor')
            if not next_cursor:
                break
                
    except Exception as e:
        print(f"Error fetching sub pages: {e}")
    
    return sub_pages

def get_page_hierarchy(notion: Client, page_id: str, depth: int = 3) -> Dict[str, Any]:
    """
    递归获取给定页面下的所有子页面及其层次结构
    
    Args:
        notion (Client): Notion API 客户端
        page_id (str): 页面ID
        depth (int): 递归深度，默认为3层
    
    Returns:
        Dict[str, Any]: 当前页面及其子页面的层次结构，JSON 结构
    """
    if depth == 0:
        return {"id": page_id, "title": "Max depth reached", "children": []}
    
    page_info = {
        "id": page_id,
        "title": None,
        "children": []
    }
    
    try:
        # 获取页面的标题
        page_details = notion.pages.retrieve(page_id=page_id)
        page_info["title"] = page_details["properties"]["title"]["title"][0]["plain_text"]
        
        # 打印当前页面信息
        print(f"Processing page: ID = {page_id}, Title = {page_info['title']}, Depth remaining = {depth}")
        
        # 初始化分页
        next_cursor = None
        
        while True:
            # 获取页面的子页面或块
            response = notion.blocks.children.list(
                block_id=page_id,
                start_cursor=next_cursor
            )
            
            # 遍历子块
            for block in response['results']:
                if block['type'] == 'child_page':
                    # 递归获取子页面信息，深度递减
                    child_page = get_page_hierarchy(notion, block['id'], depth - 1)
                    page_info["children"].append(child_page)
            
            # 检查是否还有下一页
            next_cursor = response.get('next_cursor')
            if not next_cursor:
                break
                
    except Exception as e:
        print(f"Error fetching page hierarchy: {e}")
    
    return page_info

if __name__ == "__main__":
    # 初始化 Notion 客户端
    notion = Client(auth=os.environ.get("NOTION_API_KEY"))
    # 指定根页面的ID
    root_page_id = "ae6222d5609649e998b2786a83dc15a2"
    # 获取页面层次结构并打印
    page_hierarchy = get_page_hierarchy(notion, root_page_id)
    pprint(page_hierarchy)
    with open("page_hierarchy.json", "w") as f:
        json.dump(page_hierarchy, f, indent=4)