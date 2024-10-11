import json
import os
from typing import List, Tuple, Dict, Any
from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
from notion_client import Client

class NotionCalendarManager:
    """
    NotionCalendarManager 类用于从 Notion 页面信息中递归获取层次结构并生成 iCalendar 事件文件。

    Attributes:
        notion_client (Client): Notion API 客户端实例。
        calendar (Calendar): iCalendar 实例，用于创建日历事件。
    """

    def __init__(self, notion_client: Client):
        """
        初始化 NotionCalendarManager 实例。

        Args:
            notion_client (Client): Notion API 客户端实例。
        """
        self.notion_client = notion_client
        self.calendar = Calendar()

    def get_sub_pages(self, parent_page_id: str) -> List[Dict[str, Any]]:
        """
        获取给定页面下的所有子页面。

        Args:
            parent_page_id (str): 父页面的 ID。

        Returns:
            List[Dict[str, Any]]: 所有子页面的信息列表。
        """
        sub_pages = []
        try:
            next_cursor = None
            while True:
                response = self.notion_client.blocks.children.list(
                    block_id=parent_page_id,
                    start_cursor=next_cursor
                )
                for block in response['results']:
                    if block['type'] == 'child_page':
                        page_id = block["id"].replace("-", "")
                        sub_page = {
                            "id": block["id"],
                            "title": block["child_page"]["title"],
                            "url": f"https://www.notion.so/{page_id}"  # 手动构建页面的 URL
                        }
                        sub_pages.append(sub_page)
                        print(f"Fetched sub-page: ID = {sub_page['id']}, Title = {sub_page['title']}, URL = {sub_page['url']}")
                next_cursor = response.get('next_cursor')
                if not next_cursor:
                    break
        except Exception as e:
            print(f"Error fetching sub pages: {e}")
        return sub_pages

    def get_page_hierarchy(self, page_id: str) -> Dict[str, Any]:
        """
        递归获取给定页面下的所有子页面及其层次结构。

        Args:
            page_id (str): 页面 ID。

        Returns:
            Dict[str, Any]: 当前页面及其子页面的层次结构。
        """
        page_info = {
            "id": page_id,
            "title": None,
            "url": None,
            "children": []
        }

        try:
            page_details = self.notion_client.pages.retrieve(page_id=page_id)
            page_info["title"] = page_details["properties"]["title"]["title"][0]["plain_text"]
            page_info["url"] = f"https://www.notion.so/{page_id.replace('-', '')}"

            print(f"Processing page: ID = {page_id}, Title = {page_info['title']}, URL = {page_info['url']}")

            sub_pages = self.get_sub_pages(page_id)
            for sub_page in sub_pages:
                child_page = self.get_page_hierarchy(sub_page["id"])
                page_info["children"].append(child_page)

        except Exception as e:
            print(f"Error fetching page hierarchy: {e}")

        return page_info

    def save_page_info(self, page_info: Dict[str, Any], file_name: str = "page_info.json"):
        """
        将页面信息保存为 JSON 文件。

        Args:
            page_info (Dict[str, Any]): 页面信息。
            file_name (str): 保存的文件名。
        """
        data_folder = "data"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        
        file_path = os.path.join(data_folder, file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(page_info, f, ensure_ascii=False, indent=4)
            print(f"Page info has been saved to {file_path}")
        except Exception as e:
            print(f"Error saving page info: {e}")

    def parse_page_info(self, page_info: Dict[str, Any], parent_path: List[str] = None) -> List[Tuple[str]]:
        """
        递归解析页面信息，获取所有路径并包含页面 URL。

        Args:
            page_info (Dict[str, Any]): 页面信息。
            parent_path (List[str]): 父路径列表。

        Returns:
            List[Tuple[str]]: 所有路径的列表，路径中包括页面 URL。
        """
        if parent_path is None:
            parent_path = []

        paths = []
        current_path = parent_path + [page_info['title'], page_info['url']]

        if not page_info['children']:
            paths.append(tuple(current_path))
        else:
            for child in page_info['children']:
                paths.extend(self.parse_page_info(child, current_path))

        return paths

    def generate_calendar_events(self, paths: List[Tuple[str]], output_file: str):
        """
        生成 iCalendar 事件并保存为 .ics 文件。

        Args:
            paths (List[Tuple[str]]): 所有页面路径的列表。
            output_file (str): 输出的 .ics 文件路径。
        """
        start_time = datetime(2024, 8, 22, 7, 30)  # 假设从今天开始生成日历事件
        duration = timedelta(minutes=30)  # 每个事件持续半小时

        for i in range(0, len(paths), 3):  # 每三个路径为一组
            if i + 2 >= len(paths):  # 如果剩余不足三个路径，跳出循环
                break
            try:
                event_time = start_time + timedelta(days=(i // 3) // 5, weeks=0, hours=0, minutes=0)
                title = f"【{event_time.strftime('%Y-%m-%d')} 上午任务提醒】课程"
                descriptions = [
                    f"任务1: 《{'》《'.join(paths[i][::2])}》 -> 访问 Notion 页面: [点击访问]({paths[i][-1]})",
                    f"任务2: 《{'》《'.join(paths[i][::2])}》 -> 访问 Notion 页面: [点击访问]({paths[i+1][-1]})",
                    f"任务3: 《{'》《'.join(paths[i+2][::2])}》 -> 访问 Notion 页面: [点击访问]({paths[i+2][-1]})"
                ]
                description = "\n".join(descriptions)

                # 创建事件
                event = Event()
                event.add('summary', title)
                event.add('description', description)
                event.add('dtstart', event_time)
                event.add('dtend', event_time + duration)

                # 添加提醒
                alarm = Alarm()
                alarm.add('trigger', timedelta(minutes=-5))  # 提前5分钟提醒
                alarm.add('action', 'DISPLAY')
                alarm.add('description', f"【{event_time.strftime('%Y-%m-%d')} 上午任务提醒】{paths[i][0]} 课程学习")
                event.add_component(alarm)

                self.calendar.add_component(event)
                print(f"Added calendar event: {title}")
                
            except Exception as e:
                print(f"Error generating calendar events: {e}")
                continue

            # 每个事件间隔一天，如果周末跳过
            if event_time.weekday() == 4:  # 周五之后是周末，跳到下周一
                start_time += timedelta(days=2)
            else:
                start_time += timedelta(days=1)

        # 保存到 .ics 文件
        with open(output_file, 'wb') as f:
            f.write(self.calendar.to_ical())
        print(f"iCalendar 事件已生成并保存为 {output_file}")

# 使用示例
if __name__ == "__main__":
    # 创建 Notion 客户端实例
    notion_client = Client(auth=os.environ.get("NOTION_API_KEY"))
    # 初始化 NotionCalendarManager 实例
    manager = NotionCalendarManager(notion_client)
    # 示例页面 ID（需替换为实际页面 ID）
    root_page_id = "58d69660f4e34637be707a96a651f130"
    # 获取页面层次结构
    page_hierarchy = manager.get_page_hierarchy(root_page_id)
    # 保存页面信息为 JSON 文件
    manager.save_page_info(page_hierarchy, "得到课程_page_info.json")
    # 解析页面信息，获取所有路径
    paths = manager.parse_page_info(page_hierarchy)
    # 生成并保存日历事件
    manager.generate_calendar_events(paths, "ics_files/得到课程学习.ics")