from icalendar import Calendar, Event, Alarm
from datetime import datetime, timedelta
import random

# Your list of quotes (you can add Chinese quotes if needed)
quotes = [
    "知之为知之，不知为不知，是知也。",
    "人无远虑，必有近忧。",
    "吾日三省吾身：为人谋而不忠乎？与朋友交而不信乎？传不习乎？",
    "学而不思则罔，思而不学则殆。",
    "三人行，必有我师焉；择其善者而从之，其不善者而改之。",
    "君子喻于义，小人喻于利。",
    "己所不欲，勿施于人。",
    "敏而好学，不耻下问。",
    "志不强者智不达。",
    "天行健，君子以自强不息。",
    "苟日新，日日新，又日新。",
    "有志者，事竟成。",
    "海纳百川，有容乃大；壁立千仞，无欲则刚。",
    "不飞则已，一飞冲天；不鸣则已，一鸣惊人。",
    "大丈夫处世，当扫除天下，安事一室乎！",
    "君子和而不同，小人同而不和。",
    "一寸光阴一寸金，寸金难买寸光阴。",
    "纸上得来终觉浅，绝知此事要躬行。",
    "山不厌高，海不厌深。",
    "宁为玉碎，不为瓦全。",
    "路遥知马力，日久见人心。",
    "行百里者半九十。",
    "尺有所短，寸有所长。",
    "君子坦荡荡，小人长戚戚。",
    "鞠躬尽瘁，死而后已。",
    "士为知己者死，女为悦己者容。",
    "不积跬步，无以至千里；不积小流，无以成江海。",
    "兼听则明，偏信则暗。",
    "玉不琢，不成器；人不学，不知道。",
    "千里之行，始于足下。",
    "知己知彼，百战不殆。",
    "见贤思齐焉，见不贤而内自省也。",
    "生于忧患，死于安乐。",
    "工欲善其事，必先利其器。",
    "得道者多助，失道者寡助。",
    "苟利国家生死以，岂因祸福避趋之。",
    "有志者事竟成，破釜沉舟，百二秦关终属楚。",
    "风声雨声读书声，声声入耳；家事国事天下事，事事关心。",
    "富贵不能淫，贫贱不能移，威武不能屈，此之谓大丈夫。",
    "不以规矩，不能成方圆。",
    "名不正，则言不顺；言不顺，则事不成。",
    "人非圣贤，孰能无过？过而能改，善莫大焉。",
    "莫等闲，白了少年头，空悲切。",
    "大直若屈，大巧若拙，大辩若讷。",
    "天将降大任于斯人也，必先苦其心志，劳其筋骨，饿其体肤。",
    "老骥伏枥，志在千里；烈士暮年，壮心不已。",
    "静以修身，俭以养德。",
    "知无不言，言无不尽。",
    "多行不义必自毙。",
    "学而时习之，不亦说乎？",
    "君子爱财，取之有道。",
    "物以类聚，人以群分。",
    "以德报怨，何以报德？",
    "小不忍，则乱大谋。",
    "勿以恶小而为之，勿以善小而不为。",
    "大道至简，知易行难。",
    "成事不说，遂事不谏。",
    "先天下之忧而忧，后天下之乐而乐。",
    "见义不为，无勇也。",
    "得人心者得天下。",
    "时光易逝，岁月如梭。",
    "事以密成，语以泄败。",
    "敬人者，人恒敬之；助人者，人恒助之。",
    "凡事预则立，不预则废。",
    "岁寒，然后知松柏之后凋也。",
    "穷则变，变则通，通则久。",
    "人生得意须尽欢，莫使金樽空对月。",
    "醉翁之意不在酒，在乎山水之间也。",
    "世事洞明皆学问，人情练达即文章。",
    "临渊羡鱼，不如退而结网。",
    "君子不器。",
    "一夫当关，万夫莫开。",
    "宁静致远。",
    "居安思危，思则有备，有备无患。",
    "好风凭借力，送我上青云。",
    "勇者不惧，智者不惑，仁者不忧。",
    "言必信，行必果。",
    "天下兴亡，匹夫有责。",
    "天涯何处无芳草。",
    "有容乃大，无欲则刚。",
    "得之我幸，失之我命。",
    "善有善报，恶有恶报。",
    "不积跬步，无以至千里。",
    "清风明月本无价，近水远山皆有情。",
    "淡泊明志，宁静致远。",
    "一言既出，驷马难追。",
    "人而无信，不知其可也。",
    "静以修身，俭以养德。",
    "人无完人，金无足赤。",
    "知行合一。",
    "小人之交甘若醴，君子之交淡若水。",
    "不识庐山真面目，只缘身在此山中。",
    "前事不忘，后事之师。",
    "生于忧患，死于安乐。",
    "江山易改，本性难移。",
    "人无远虑，必有近忧。",
    "己所不欲，勿施于人。",
    "宁为玉碎，不为瓦全。",
    "千里之行，始于足下。",
    "宁可玉碎，不能瓦全。"
]


quotes_example = [
    "🌟 成功的唯一途径是热爱你的工作。- 史蒂夫·乔布斯",
    "💪 成功不是终点，失败也不是终结：重要的是继续前进的勇气。- 温斯顿·丘吉尔",
    "🎯 从你所在的地方开始，利用你拥有的，做你能做的。- 亚瑟·阿什",
    "🚀 未来属于那些相信自己梦想之美的人。- 埃莉诺·罗斯福",
    "🌱 无论多慢，只要不停下来，就没有关系。- 孔子",
    "🔥 别看时钟；做它在做的事。继续前进。- 萨姆·莱文森",
    "🌈 预测未来的最佳方式是创造未来。- 彼得·德鲁克",
    "🌍 实现明天的唯一限制是我们今天的疑虑。- 富兰克林·D·罗斯福",
    "✨ 你的时间有限，不要浪费在过别人的生活上。- 史蒂夫·乔布斯",
    "🎓 教育是最强有力的武器，你可以用它来改变世界。- 纳尔逊·曼德拉"
]
emojis = ["🌟", "💪", "🎯", "🚀", "🌱", "🔥", "🌈", "🌍", "✨", "🎓", ]
quotes = [f"{random.choice(emojis)} {quote}" for quote in quotes]
all_quotes = quotes + quotes_example



# Create Calendar object
cal = Calendar()
cal.add('prodid', '-//每日励志提醒//example.com//')
cal.add('version', '2.0')

# Set the start date for the reminders
start_date = datetime(2024, 9, 1, 6, 15, 0)

# Number of days you want the reminder to run (2 years)
num_days = 365 * 2

for i in range(num_days):
    # Create a new event
    event = Event()
    event.add('uid', f'quote-reminder-{i}@example.com')
    event.add('dtstamp', datetime.now())
    event.add('dtstart', start_date + timedelta(days=i))
    event.add('dtend', start_date + timedelta(days=i, minutes=15))
    event.add('summary', '🌟 每日励志提升 🌟')

    # Pick 3 random quotes
    daily_quotes = random.sample(quotes, 3)
    description = "✨ 这里是今天给你带来灵感和能量的三句话:\n\n" + "\n\n".join(daily_quotes) + "\n\n🚀 让我们好好利用今天吧！"
    event.add('description', description)

    # Add an alarm to trigger at the start of the event
    alarm = Alarm()
    alarm.add('action', 'DISPLAY')
    alarm.add('description', '你的每日励志语录来了！🌟')
    alarm.add('trigger', timedelta(minutes=0))

    event.add_component(alarm)
    cal.add_component(event)

# Save the calendar to a file
with open('daily_quotes_reminders.ics', 'wb') as f:
    f.write(cal.to_ical())

print("iCalendar 文件 'daily_quotes_reminders.ics' 已成功创建。")