import datetime
import httpx
from notion_client import Client
import icalendar
import time

class NotionPageManager:
    def __init__(self, notion_token: str, parent_page_id: str):
        self.notion = Client(auth=notion_token)
        self.parent_page_id = parent_page_id
        self.pages_data = []

    def retry_request(self, func, retries=3, delay=5, *args, **kwargs):
        """
        添加重试机制以应对可能的网络连接问题。
        """
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except httpx.ConnectError as e:
                print(f"Connection failed: {e}. Retrying {i+1}/{retries}...")
                time.sleep(delay)
        raise Exception("Failed to connect after several retries.")

    def create_page(self, parent_id: str, title: str, content: str) -> dict:
        """
        创建Notion页面并添加内容，内容以quote部分开始，随后是回顾总结表格和反思列表。
        """
        quote_blocks = [
            {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [{"type": "text", "text": {"content": section}}]
                }
            } for section in content
        ]

        children_blocks = quote_blocks + [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "昨日回顾总结"}}]
                }
            },
            {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 5,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"text": {"content": "优先级"}}],
                                    [{"text": {"content": "事情"}}],
                                    [{"text": {"content": "具体内容"}}],
                                    [{"text": {"content": "完成度"}}],
                                    [{"text": {"content": "说明"}}]
                                ]
                            }
                        }
                    ]
                }
            },
            # 添加三个编号列表项（反思1-3）
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": [{"text": {"content": "反思1"}}]}
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": [{"text": {"content": "反思2"}}]}
            },
            {
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": [{"text": {"content": "反思3"}}]}
            },
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": "今日计划安排"}}]
                }
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {"rich_text": [{"text": {"content": "TODO 1"}}]}
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {"rich_text": [{"text": {"content": "TODO 2"}}]}
            },
            {
                "object": "block",
                "type": "to_do",
                "to_do": {"rich_text": [{"text": {"content": "TODO 3"}}]}
            },
            {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 5,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": [
                        {
                            "object": "block",
                            "type": "table_row",
                            "table_row": {
                                "cells": [
                                    [{"text": {"content": "优先级"}}],
                                    [{"text": {"content": "事情"}}],
                                    [{"text": {"content": "具体内容"}}],
                                    [{"text": {"content": "完成度"}}],
                                    [{"text": {"content": "说明"}}]
                                ]
                            }
                        }
                    ]
                }
            }
        ]

        page = self.retry_request(
            self.notion.pages.create,
            parent={"page_id": parent_id},
            properties={
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            children=children_blocks
        )
        return {"id": page['id'], "url": page['url']}

    def create_monthly_and_daily_pages(self, start_date: datetime.date, end_date: datetime.date) -> None:
        """
        为每个月和每一天创建页面，并记录页面数据。
        """
        current_date = start_date
        while current_date <= end_date:
            month_start_date = current_date.replace(day=1)
            month_end_date = (month_start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            month_title = month_start_date.strftime("%Y-%m")

            month_page = self.create_page(self.parent_page_id, month_title, [])
            print(f"Created month page: {month_title} (URL: {month_page['url']})")

            day = month_start_date
            while day <= month_end_date:
                day_title = f"【{day.strftime('%Y-%m-%d')}】回顾总结&计划安排"
                content = [
                    "💡 `问`。当你听到了一个关于解决问题的好经验时，首先要尽可能地去了解跟这个经验有关的种种细节，越详细越好。我要求同学们写作业也是希望尽可能地把那些细节介绍得详细些哪些？因"
                    "为`细节`越多越详细，越有助于我们判断这个经验或者这个好做法的适用条件，看它是不是适合你现在所处的情况，所要解决的问题。所以，从今天开始，我以后选择留言都会按照一个标准，就是要有细节，有分析，有做法。这是第一个字——“问”。",
                    "💡 `想`。问了以后，要思考的就是“想”。想的目的，就是要在你的头脑中，尽可能地提炼出某一个做法，或者`经验的核心特征`，找到隐藏在这个特征背后的逻辑。比如某一个人说炒某个菜好吃，他要能用几步特征来概括出他做这个菜与众不同的地方。所以你在学习他人经验的时候，要注意试着用几句话，几个词来概括出别人经验的样貌。那这几句话或几个词就是别人做法的模板。",
                    "💡 `仿`。请记住，所有的经验学习都是从模仿开始的，而模仿的核心就是要基于前面你所总结出来他人的模板。很多模仿，最开始都是学不像的，因为毕竟还是是人家的东西，所以，要有足够的细心和耐心，注意修正，注意调整。",
                    "💡 `改`。因为你遇到的问题一定具有你的特殊性，所以，你一定要注意结合自己的情况来不断修改经验模板，在别人的模板上增加一些你自己认为必要的因素，减少一些不必要的因素，使得这个经验变成你的东西，对你解决问题有帮助。",
                    "💡 `善`。当你看到你通过模仿他人的东西，来解决你的问题，取得了效果之后，其实你就进入到了一个更高的境界——完善的境界。因为完善的目标就是形成一个新的更加简化的适合你自己使用的经验模板。"
                ]
                day_page = self.create_page(month_page['id'], day_title, content)
                print(f"  Created day page: {day_title} (URL: {day_page['url']})")

                # 记录每日页面的URL以便之后使用
                self.pages_data.append({"title": day_title, "url": day_page['url'], "date": day.strftime('%Y-%m-%d')})

                day += datetime.timedelta(days=1)

            current_date = month_end_date + datetime.timedelta(days=1)

    def create_calendar(self, start_date: datetime.date, end_date: datetime.date, filename: str) -> None:
        """
        为工作日创建日历事件，并在事件描述中添加Notion页面的URL。
        """
        cal = icalendar.Calendar()
        for page_data in self.pages_data:
            event_date = datetime.datetime.strptime(page_data["date"], '%Y-%m-%d').date()
            if event_date.weekday() < 5:  # 0 = Monday, 4 = Friday
                event = icalendar.Event()
                event_start = datetime.datetime.combine(event_date, datetime.time(9, 30))
                event_end = event_start + datetime.timedelta(minutes=15)

                event.add('summary', '工作日提醒(加油谢明，你永远是最棒的！)')
                event.add('dtstart', event_start)
                event.add('dtend', event_end)
                event.add('description', f"访问你的Notion页面: {page_data['url']}")

                cal.add_component(event)

        with open(filename, 'wb') as f:
            f.write(cal.to_ical())
        print(f"Calendar saved to {filename}")

    def run(self, start_date: str, end_date: str) -> None:
        """
        运行整个流程，创建页面并生成日历。
        """
        start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        self.create_monthly_and_daily_pages(start_date_obj, end_date_obj)
        self.create_calendar(start_date_obj, end_date_obj, 'workday_reminders.ics')
        print("Process completed. Data saved to 'workday_reminders.ics'.")


# Run the NotionPageManager
if __name__ == "__main__":
    manager = NotionPageManager(os.environ.get("NOTION_API_KEY"), "86c38d3267ee421a9a8f8985ebe32128")
    manager.run("2024-08-21", "2025-08-21")