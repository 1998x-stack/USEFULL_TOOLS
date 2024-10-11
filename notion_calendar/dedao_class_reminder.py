import json
from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta


with open('data/得到课程_page_info.json', 'r') as f:
    json_data = json.load(f)
def parse_page_info(page_info, parent_path):
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
            paths.extend(parse_page_info(child, current_path))

    with open("data/薛兆丰的经济学课_page_info.json", "w") as f:
        json.dump(paths, f, indent=4)
    return paths

paths = parse_page_info(json_data['children'][0], None)
calendar = Calendar()
event_time = datetime(2024, 8, 22, 8, 15)  # 假设从今天开始生成日历事件
duration = timedelta(minutes=30)  # 每个事件持续半小时

i = 0

while i + 2 < len(paths):  # 每三个路径为一组
# for i in range(0, len(paths), 3):  # 每三个路径为一组
    # if i + 2 >= len(paths):  # 如果剩余不足三个路径，跳出循环
    #     break
    if event_time.weekday() >= 5:  # 如果是周末，跳过
        event_time += timedelta(days=1)
        continue
    
    # 创建事件的详细信息
    title = f"【{event_time.strftime('%Y-%m-%d')} 上午任务提醒】薛兆丰的经济学课"
    descriptions = [
        f"任务1: 《{'》《'.join(paths[i][::2])}》 -> 访问 Notion 页面: [点击访问]({paths[i][-1]})",
        f"任务2: 《{'》《'.join(paths[i+1][::2])}》 -> 访问 Notion 页面: [点击访问]({paths[i+1][-1]})",
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
    alarm.add('description', "Event Reminder")
    event.add_component(alarm)

    calendar.add_component(event)
    
    i += 3
    event_time += timedelta(days=1)  # 日期加一天


# 保存到 .ics 文件
output_file = 'ics_files/0-宁向东管理学课程.ics'
with open(output_file, 'wb') as f:
    f.write(calendar.to_ical())
print(f"iCalendar 事件已生成并保存为 {output_file}")