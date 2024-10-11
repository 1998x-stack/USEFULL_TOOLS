import json
import re
from typing import Dict

def extract_notion_links(file_path: str) -> Dict[str, str]:
    event_data = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        current_date = None
        notion_link = None
        description_line = ""
        for line in file:
            stripped_line = line.strip()
            if stripped_line.startswith("DTSTART:"):
                current_date = stripped_line.split("DTSTART:")[1][:8]  # 提取日期部分 YYYYMMDD
            elif stripped_line.startswith("DESCRIPTION:"):
                description_line = stripped_line  # 开始记录 DESCRIPTION 行
            elif description_line and not stripped_line.startswith("END:VEVENT") and not stripped_line.startswith("BEGIN:VALARM"):
                # 合并 DESCRIPTION 行和下一行
                description_line += stripped_line
                matches = re.findall(r'https://www\.notion\.so/\d{4}-\d{2}-\d{2}-[a-fA-F0-9]+$', description_line)
                if matches:
                    notion_link = matches[0]
            elif stripped_line == "END:VEVENT" and current_date and notion_link:
                event_data[current_date] = notion_link
                current_date = None
                notion_link = None
                description_line = ""  # 处理完一个事件后重置描述行
    
    return event_data

import datetime
import icalendar
from notion_client import Client

def generate_and_update_ics(event_data, notion_token, output_filename='updated_events.ics'):
    notion = Client(auth=notion_token)
    
    def extract_page_id(notion_link):
        # Extract the last part of the URL as the page ID
        return notion_link.split("-")[-1]

    def add_todo_to_page(page_id):
        # Add afternoon TODOs
        afternoon_todos = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "下午TODO（最重要的三件事）"}}]
                }
            }
        ] + [
            {
                "object": "block",
                "type": "to_do",
                "to_do": {"rich_text": [{"text": {"content": f"TODO 下午 {i}"}}]}
            } for i in range(1, 4)
        ]

        # Add evening TODOs
        evening_todos = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "晚上TODO（最重要的三件事）"}}]
                }
            }
        ] + [
            {
                "object": "block",
                "type": "to_do",
                "to_do": {"rich_text": [{"text": {"content": f"TODO 晚上 {i}"}}]}
            } for i in range(1, 4)
        ]

        # Add the blocks to the Notion page
        notion.blocks.children.append(page_id, children=afternoon_todos + evening_todos)

    def create_ics_event(cal, date, time, notion_link, event_type):
        event_start = datetime.datetime.combine(date, time)
        event_end = event_start + datetime.timedelta(minutes=15)

        if event_type == 'afternoon':
            title = f"【{date.strftime('%Y-%m-%d')} 下午任务提醒】完成今天最重要的三件事"
            description = (
                f"今天下午，你需要完成以下最重要的三件事。请务必访问你的Notion页面进行任务管理和进度跟踪：\n"
                f"👉 [点击这里访问Notion页面]({notion_link})"
            )
        else:
            title = f"【{date.strftime('%Y-%m-%d')} 晚上任务提醒】总结与计划"
            description = (
                f"晚上是反思和规划的时间。请访问你的Notion页面完成今天的总结并制定明天的计划：\n"
                f"👉 [点击这里访问Notion页面]({notion_link})"
            )

        event = icalendar.Event()
        event.add('summary', title)
        event.add('dtstart', event_start)
        event.add('dtend', event_end)
        event.add('description', description)

        alarm = icalendar.Alarm()
        alarm.add('trigger', datetime.timedelta(minutes=-5))
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f"请及时处理：{title}")

        event.add_component(alarm)
        cal.add_component(event)
    
    def create_vtodo_event(cal, date, title, description):
        vtodo = icalendar.Todo()
        vtodo.add('summary', title)
        vtodo.add('due', date)
        vtodo.add('description', description)
        cal.add_component(vtodo)

    # Create the iCalendar
    cal = icalendar.Calendar()

    for date_str, notion_link in event_data.items():
        page_id = extract_page_id(notion_link)
        add_todo_to_page(page_id)

        # Convert date string to a date object
        date = datetime.datetime.strptime(date_str, '%Y%m%d').date()

        # Create 1:05 PM event
        create_ics_event(cal, date, datetime.time(13, 5), notion_link, 'afternoon')

        # Create 8:30 PM event
        create_ics_event(cal, date, datetime.time(20, 30), notion_link, 'evening')

        # Create VTODO events
        create_vtodo_event(cal, date, f"下午TODO（最重要的三件事）", f"查看Notion页面并完成下午的任务：{notion_link}")
        create_vtodo_event(cal, date, f"晚上TODO（最重要的三件事）", f"查看Notion页面并完成晚上的任务：{notion_link}")

        print(f"Events created for {date_str} with Notion link: {notion_link}")
        
    # Save the .ics file
    with open(output_filename, 'wb') as f:
        f.write(cal.to_ical())
    print(f"Calendar saved to {output_filename}")

if __name__ == '__main__':
    ics_file_path = 'workday_reminders_with_alarms.ics'
    event_data = extract_notion_links(ics_file_path)
    generate_and_update_ics(event_data, os.environ.get("NOTION_API_KEY"), 'todo_reminders.ics')