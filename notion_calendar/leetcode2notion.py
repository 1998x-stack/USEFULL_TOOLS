import datetime
import json
import pandas as pd
from notion_client import Client
from typing import Dict, Any
import icalendar
import time

class NotionProblemPageManager:
    def __init__(self, notion_token: str, parent_page_id: str, retries: int = 3, delay: int = 2):
        """
        初始化NotionProblemPageManager类，设定Notion客户端和父页面ID。
        
        Args:
            notion_token (str): Notion API的授权令牌。
            parent_page_id (str): 父页面的ID。
            retries (int): 失败后重试的次数。
            delay (int): 每次重试之间的延迟时间（秒）。
        """
        self.notion = Client(auth=notion_token)
        self.parent_page_id = parent_page_id
        self.pages_urls = {"easy": [], "medium": [], "hard": []}
        self.retries = retries
        self.delay = delay

    def _retry(self, func, *args, **kwargs):
        """
        带有重试机制的通用函数执行方法。

        Args:
            func: 需要执行的函数。
            *args: 函数的定位参数。
            **kwargs: 函数的关键字参数。

        Returns:
            Any: 函数执行的返回值。
        """
        for attempt in range(self.retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error: {e}, retrying {attempt + 1}/{self.retries}...")
                time.sleep(self.delay)
        raise Exception(f"Failed after {self.retries} retries.")

    def _extract_title_from_url(self, url: str) -> str:
        """
        从URL中提取问题标题。

        Args:
            url (str): 问题的URL。

        Returns:
            str: 提取的标题。
        """
        return url.split('/')[-1].replace('-', ' ').title()

    def create_problem_pages(self, problems: pd.DataFrame, difficulty: str) -> None:
        """
        根据难度等级为每个问题创建页面，并保存页面URL到相应的列表中。

        Args:
            problems (pd.DataFrame): 包含问题信息的数据框。
            difficulty (str): 问题的难度等级（easy, medium, hard）。
        """
        difficulty_page = self._retry(self._create_page, self.parent_page_id, f"{difficulty.capitalize()} Problems")
        print(f"Created {difficulty} page: {difficulty_page['url']}")

        for _, problem in problems.iterrows():
            title = self._extract_title_from_url(problem['url'])
            problem_page = self._retry(self._create_page, difficulty_page['id'], title)
            print(f"  Created problem page: {title} (URL: {problem_page['url']})")
            self._retry(self._add_quote_to_page, problem_page['id'], problem)
            self.pages_urls[difficulty].append(problem_page['url'])

    def _create_page(self, parent_id: str, title: str) -> Dict[str, str]:
        """
        在指定父页面下创建新页面，并返回页面ID和URL。

        Args:
            parent_id (str): 父页面的ID。
            title (str): 新页面的标题。

        Returns:
            Dict[str, str]: 包含页面ID和URL的字典。
        """
        page = self.notion.pages.create(
            parent={"page_id": parent_id},
            properties={
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        )
        return {"id": page['id'], "url": page['url']}

    def _add_quote_to_page(self, page_id: str, problem: pd.Series) -> None:
        """
        添加问题细节作为引用到指定页面。

        Args:
            page_id (str): 页面ID。
            problem (pd.Series): 包含问题信息的系列。
        """        
        # Create a clickable link using Notion's rich text with href attribute
        link_text = {
            "type": "text",
            "text": {
                "content": "Problem Link",
                "link": {
                    "url": problem['url']
                }
            }
        }

        # Create a quote block with problem details
        initial_quote = {
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": f"People: {problem['people']}\nRate: {problem['rate']}"
                        }
                    }
                ]
            }
        }

        # Add content to the Notion page with a quote, clickable link, and code blocks
        self.notion.blocks.children.append(
            page_id,
            children=[
                initial_quote,  # Adding the quote block first
                {
                    "object": "block",
                    "type": "quote",
                    "quote": {
                        "rich_text": [
                            link_text
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "Python"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "language": "python",
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"# Title: {self._extract_title_from_url(problem['url'])}\n# URL: {problem['url']}"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": "C++"
                                }
                            }
                        ]
                    }
                },
                {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "language": "c++",
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": f"// Title: {self._extract_title_from_url(problem['url'])}\n// URL: {problem['url']}"
                                }
                            }
                        ]
                    }
                }
            ]
        )

    def create_calendar_for_each_problem(self, filename: str) -> None:
        """
        为每个难度等级的问题创建一个日历事件，并保存为.ics文件。

        Args:
            filename (str): 要创建的.ics文件的文件名。
        """
        cal = icalendar.Calendar()
        event_date = datetime.datetime.now().date()

        for difficulty, urls in self.pages_urls.items():
            for index, url in enumerate(urls):
                event = self._retry(self._create_calendar_event, url, difficulty, event_date, index)
                cal.add_component(event)

        with open(filename, 'wb') as f:
            f.write(cal.to_ical())

    def _create_calendar_event(self, url: str, difficulty: str, event_date: datetime.date, index: int) -> icalendar.Event:
        """
        为一个问题创建日历事件。

        Args:
            url (str): 问题页面的URL。
            difficulty (str): 问题的难度等级。
            event_date (datetime.date): 事件的日期。
            index (int): 用于事件的时间间隔索引。

        Returns:
            icalendar.Event: 创建的日历事件。
        """
        event_start = datetime.datetime.combine(event_date, datetime.time(20, 30))  # Event starts at 8:30 PM
        event_end = event_start + datetime.timedelta(hours=1)  # Event lasts 1 hour

        cal_event = icalendar.Event()
        cal_event.add('summary', f'Notion {difficulty.capitalize()} Problem Reminder')
        cal_event.add('dtstart', event_start)
        cal_event.add('dtend', event_end)
        cal_event.add('description', f"Visit your Notion page:\n{url}")

        alarm = icalendar.Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', 'Notion Problem Reminder')
        alarm.add('trigger', datetime.timedelta(minutes=-30))  # Trigger 30 minutes before the event

        cal_event.add_component(alarm)
        return cal_event

    def save_pages_urls_to_json(self, filename: str) -> None:
        """
        将页面的URL保存到本地JSON文件。

        Args:
            filename (str): 要创建的JSON文件的文件名。
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.pages_urls, f, ensure_ascii=False, indent=4)

    def run(self, problems_file: str) -> None:
        """
        运行流程：读取CSV文件，创建页面，保存页面URL，生成日历。

        Args:
            problems_file (str): 包含问题数据的CSV文件路径。
        """
        problems_df = pd.read_csv(problems_file)

        for difficulty in ['easy', 'medium', 'hard']:
            difficulty_df = problems_df[problems_df['type'] == difficulty]
            self.create_problem_pages(difficulty_df, difficulty)
        
        self.save_pages_urls_to_json('notion_problems.json')
        self.create_calendar_for_each_problem('notion_problem_reminders.ics')
        print("Process completed. Data saved to 'notion_problems.json' and 'notion_problem_reminders.ics'.")


# Example usage
if __name__ == "__main__":
    manager = NotionProblemPageManager(os.environ.get("NOTION_API_KEY"), "4e57a8498aa54cb7941f244767b133db")
    manager.run('leetcode_problems.csv')