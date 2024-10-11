
import os
import re
import json
from notion_client import Client
from typing import List, Set, Dict, Any
from datetime import datetime, timedelta
from icalendar import Calendar, Event

class NotionDirectoryProcessor:
    """处理目录结构并在Notion中创建相应页面的类
    
    Attributes:
        notion (Any): Notion API客户端实例
        used_cleaned_names (Set[str]): 已经使用过的清理后的文件名集合
        title_url_map (Dict[str, str]): 标题和Notion URL的映射
    """
    
    def __init__(self, notion: Any):
        """
        初始化NotionDirectoryProcessor实例
        
        Args:
            notion (Any): Notion API客户端实例
        """
        self.notion = notion
        self.used_cleaned_names: Set[str] = set()
        self.title_url_map: Dict[str, str] = {}
    
    def create_page(self, parent_page_id: str, title: str) -> str:
        """
        创建一个新的Notion页面
        
        Args:
            parent_page_id (str): 父页面ID
            title (str): 页面标题
        
        Returns:
            str: 创建的页面ID
        """
        response = self.notion.pages.create(
            parent={"page_id": parent_page_id},
            properties={
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        )
        page_id = response['id']
        return page_id
    
    @staticmethod
    def clean_name(name: str) -> str:
        """
        清理文件名，移除模式前缀和后缀
        
        Args:
            name (str): 原始文件名
        
        Returns:
            str: 清理后的文件名
        """
        name = re.sub(r'\.pdf$', '', name)  # 移除.pdf后缀
        name = re.sub(r'\.html$', '', name)  # 移除.html后缀
        name = re.sub(r'\(.*?\)', '', name)  # 移除括号内数字模式
        name = name.strip()  # 去除两端的空格
        return name
    
    def process_directory(self, directory: str, parent_page_id: str, parent_title_path: str = "") -> None:
        """
        处理目录结构，在Notion中创建相应的页面
        
        Args:
            directory (str): 当前处理的目录路径
            parent_page_id (str): 父页面ID
            parent_title_path (str): 父页面的标题路径
        """
        items = sorted(os.listdir(directory))  # 对目录项进行排序
        for item in items:
            item_path = os.path.join(directory, item)
            cleaned_name = self.clean_name(item)
            full_title_path = f"{parent_title_path}_{cleaned_name}" if parent_title_path else cleaned_name
            
            if cleaned_name in self.used_cleaned_names:
                print(f"Skip: {item}")
                continue  # 如果清理后的名称已经使用过，跳过

            if os.path.isdir(item_path):
                # 如果是文件夹，递归处理
                page_id = self.create_page(parent_page_id, cleaned_name)
                self.used_cleaned_names.add(cleaned_name)
                self.process_directory(item_path, page_id, full_title_path)
                print(f"Create page: {cleaned_name}")
            elif item.endswith(".pdf") or item.endswith(".html"):
                # 如果是PDF文件或HTML文件，创建页面
                page_id = self.create_page(parent_page_id, cleaned_name)
                self.used_cleaned_names.add(cleaned_name)
                self.title_url_map[full_title_path] = f"https://www.notion.so/{page_id}"
                print(f"Create page: {cleaned_name}")
    
    def save_title_url_map_to_json(self, file_path: str) -> None:
        """
        将标题和Notion URL的映射保存为JSON文件
        
        Args:
            file_path (str): JSON文件保存路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.title_url_map, f, ensure_ascii=False, indent=4)
        print(f"Title-URL map saved to {file_path}")
    
    def create_calendar(self, start_date: str, end_date: str, file_path: str) -> None:
        """
        创建一个日历，包含每个工作日6:15 AM到8:45 AM的提醒事件
        
        Args:
            start_date (str): 日历开始日期，格式为YYYY-MM-DD
            end_date (str): 日历结束日期，格式为YYYY-MM-DD
            file_path (str): ics文件保存路径
        """
        calendar = Calendar()
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        delta = timedelta(days=1)
        
        current = start
        while current <= end:
            if current.weekday() < 5:  # 周一到周五
                for title, url in self.title_url_map.items():
                    event = Event()
                    event.name = f"Reminder: {title}"
                    event.begin = current.replace(hour=6, minute=15)
                    event.end = current.replace(hour=8, minute=45)
                    event.description = f"请访问以下Notion页面: {url}"
                    event.url = url
                    calendar.events.add(event)
            current += delta
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(calendar)
        print(f"Calendar saved to {file_path}")

def main():
    # 初始化Notion API客户端实例
    notion = Client(auth=os.environ.get("NOTION_API_KEY"))

    # 定义根目录和根页面ID
    root_directories: List[str] = [
        # "/Users/mx/Documents/0-GitHub/新产业链全景图新材料领域行业研究报告金融股票分析发展趋势分析/01-100大新材料产业链全景图"
        "/Users/mx/Downloads/极客时间/经济学人"
    ]
    root_page_ids: List[str] = [
        "90ff759f501c4c28897b94676e534d7e"
    ]

    # 创建处理器实例并开始处理目录
    processor = NotionDirectoryProcessor(notion)
    for root_directory, root_page_id in zip(root_directories, root_page_ids):
        processor.process_directory(root_directory, root_page_id)
    
    # 将标题和URL映射保存为JSON文件
    processor.save_title_url_map_to_json("data/经济学人.json")
    
    # 创建并保存日历文件
    # processor.create_calendar("2024-08-06", "2025-08-06", "notion_reminders.ics")

if __name__ == "__main__":
    main()
