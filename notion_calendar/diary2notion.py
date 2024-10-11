import datetime
import json
from notion_client import Client
from typing import Dict, List, Any
import icalendar

class NotionPageManager:
    def __init__(self, notion_token: str, parent_page_id: str):
        self.notion = Client(auth=notion_token)
        self.parent_page_id = parent_page_id
        self.pages_data = []

    def create_page(self, parent_id: str, title: str) -> Dict[str, str]:
        """
        Create a Notion page with the given title under the specified parent and return the page ID and URL.

        Args:
            parent_id (str): The ID of the parent page.
            title (str): The title of the new page.

        Returns:
            Dict[str, str]: A dictionary with the page ID and URL.
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

    def create_database(self, title: str) -> str:
        """
        Create a Notion database with the given title under the specified parent and return the database ID.

        Args:
            title (str): The title of the new database.

        Returns:
            str: The ID of the newly created database.
        """
        database = self.notion.databases.create(
            parent={"page_id": self.parent_page_id},
            title=[
                {
                    "type": "text",
                    "text": {
                        "content": title
                    }
                }
            ],
            properties={
                "Name": {"title": {}},
                "URL": {"url": {}},
                "Date": {"date": {}},
                "Week Number": {"number": {}}
            }
        )
        return database['id']

    def add_to_database(self, database_id: str, title: str, url: str, date: str, week_number: int) -> None:
        """
        Add an entry to the Notion database with the given details.

        Args:
            database_id (str): The ID of the database.
            title (str): The title of the entry.
            url (str): The URL of the page.
            date (str): The date associated with the entry.
            week_number (int): The week number in the month.
        """
        self.notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "URL": {
                    "url": url
                },
                "Date": {
                    "date": {
                        "start": date
                    }
                },
                "Week Number": {
                    "number": week_number
                }
            }
        )

    def get_week_number(self, date: datetime.date) -> int:
        """
        Calculate the week number of the given date in its month.

        Args:
            date (datetime.date): The date to calculate the week number for.

        Returns:
            int: The week number in the month.
        """
        first_day = date.replace(day=1)
        adjusted_day = date.day + first_day.weekday()
        return (adjusted_day - 1) // 7 + 1

    def create_calendar(self, events: List[Dict[str, str]], filename: str) -> None:
        """
        Create an .ics calendar file with events for each date.

        Args:
            events (List[Dict[str, str]]): A list of events with date and URL.
            filename (str): The name of the .ics file to be created.
        """
        cal = icalendar.Calendar()
        for event in events:
            cal_event = icalendar.Event()
            event_date = datetime.datetime.strptime(event["date"], '%Y-%m-%d').date()
            event_start = datetime.datetime.combine(event_date, datetime.time(23, 0))
            event_end = event_start + datetime.timedelta(hours=1)
            
            cal_event.add('summary', 'Notion Page Reminder')
            cal_event.add('dtstart', event_start)
            cal_event.add('dtend', event_end)
            cal_event.add('description', f"Reminder to visit your Notion page for {event_date.strftime('%Y-%m-%d')}:\n{event['url']}")
            
            alarm = icalendar.Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', 'Notion Page Reminder')
            alarm.add('trigger', datetime.timedelta(hours=-1))
            
            cal_event.add_component(alarm)
            cal.add_component(cal_event)

        with open(filename, 'wb') as f:
            f.write(cal.to_ical())

    def save_pages_to_json(self, filename: str) -> None:
        """
        Save the pages data to a local JSON file.

        Args:
            filename (str): The name of the JSON file to be created.
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.pages_data, f, ensure_ascii=False, indent=4)

    def create_monthly_and_daily_pages(self, start_date: datetime.date, end_date: datetime.date) -> None:
        """
        Create monthly and daily pages from the start date to the end date and collect all into a database.

        Args:
            start_date (datetime.date): The start date.
            end_date (datetime.date): The end date.
        """
        database_id = self.create_database("Monthly and Daily Pages Database")
        print(f"Created database: {database_id}")
        
        current_date = start_date
        while current_date <= end_date:
            month_start_date = current_date.replace(day=1)
            month_end_date = (month_start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            month_title = month_start_date.strftime("%Y-%m")
            
            month_page = self.create_page(self.parent_page_id, month_title)
            print(f"Created month page: {month_title} (URL: {month_page['url']})")
            
            self.add_to_database(database_id, month_title, month_page['url'], month_start_date.strftime('%Y-%m-%d'), 0)
            self.pages_data.append({"title": month_title, "url": month_page['url'], "date": month_start_date.strftime('%Y-%m-%d'), "week_number": 0})
            
            day = month_start_date
            while day <= month_end_date:
                week_number = self.get_week_number(day)
                day_of_week = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][day.weekday()]
                day_title = f"第{week_number}周 {day_of_week} {day.strftime('%Y-%m-%d')}"
                
                day_page = self.create_page(month_page['id'], day_title)
                print(f"  Created day page: {day_title} (URL: {day_page['url']})")
                
                self.add_to_database(database_id, day_title, day_page['url'], day.strftime('%Y-%m-%d'), week_number)
                self.pages_data.append({"title": day_title, "url": day_page['url'], "date": day.strftime('%Y-%m-%d'), "week_number": week_number})
                
                day += datetime.timedelta(days=1)
            
            current_date = month_end_date + datetime.timedelta(days=1)

    def run(self, start_date: str, end_date: str) -> None:
        """
        Run the process of creating pages, collecting data, saving to JSON, and creating a calendar.

        Args:
            start_date (str): The start date in 'YYYY-MM-DD' format.
            end_date (str): The end date in 'YYYY-MM-DD' format.
        """
        start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        self.create_monthly_and_daily_pages(start_date_obj, end_date_obj)
        self.save_pages_to_json('notion_pages.json')
        self.create_calendar(self.pages_data, 'notion_reminders.ics')
        print("Process completed. Data saved to 'notion_pages.json' and 'notion_reminders.ics'.")

# Run the NotionPageManager
if __name__ == "__main__":
    manager = NotionPageManager("your-integration-token", "your-parent-page-id")
    manager.run("2024-08-01", "2025-05-31")