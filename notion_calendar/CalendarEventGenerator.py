import datetime
import icalendar, json
from typing import Dict, List

class CalendarEventGenerator:
    def __init__(self, problems_urls: Dict[str, List[str]], start_date: datetime.datetime) -> None:
        """
        初始化生成器。

        Args:
            problems_urls (Dict[str, List[str]]): 存储每个难度级别的问题 URL 的字典。
            start_date (datetime.datetime): 日历事件的起始日期时间。
        """
        self.problems_urls = problems_urls
        self.start_date = start_date

    def create_calendar_for_problems(self, filename: str) -> None:
        """
        为每个问题生成日历事件，并保存为 .ics 文件。

        Args:
            filename (str): 要保存的 .ics 文件名。
        """
        calendar = icalendar.Calendar()
        current_date = self.start_date

        max_length = max(len(self.problems_urls.get('easy', [])),
                         len(self.problems_urls.get('medium', [])),
                         len(self.problems_urls.get('hard', [])))

        for i in range(max_length):
            for difficulty in ['easy', 'medium', 'hard']:
                url_list = self.problems_urls.get(difficulty, [])
                if i < len(url_list):
                    event = self._create_calendar_event(url_list[i], difficulty, current_date)
                    calendar.add_component(event)
            
            current_date += datetime.timedelta(days=1)

        with open(filename, 'wb') as file:
            file.write(calendar.to_ical())

    def _create_calendar_event(self, url: str, difficulty: str, event_date: datetime.datetime) -> icalendar.Event:
        """
        创建单个问题的日历事件。

        Args:
            url (str): 问题的 URL。
            difficulty (str): 问题的难度级别。
            event_date (datetime.datetime): 事件的日期时间。

        Returns:
            icalendar.Event: 创建的日历事件。
        """
        event_start = event_date
        event_end = event_start + datetime.timedelta(hours=1)

        event = icalendar.Event()
        event.add('summary', f'{difficulty.capitalize()} Problem Reminder')
        event.add('dtstart', event_start)
        event.add('dtend', event_end)
        event.add('description', f"Visit the problem URL: {url}")

        alarm = icalendar.Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f'{difficulty.capitalize()} Problem Reminder')
        alarm.add('trigger', datetime.timedelta(minutes=-30))

        event.add_component(alarm)
        return event


def main():
    with open('data/notion_problems.json', 'r') as file:
        problems_urls = json.load(file)
    # 事件起始日期和时间
    start_date = datetime.datetime(2024, 8, 20, 20, 30)
    # 实例化生成器并生成日历文件
    generator = CalendarEventGenerator(problems_urls, start_date)
    generator.create_calendar_for_problems("ics_files/problems_schedule.ics")
    print("日历文件已生成：ics_files/problems_schedule.ics")

if __name__ == "__main__":
    main()
