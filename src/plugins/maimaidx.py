import time
from collections import defaultdict

from nonebot import on_command, on_regex
from nonebot.typing import T_State
from nonebot.adapters import Event, Bot
from nonebot.adapters.cqhttp import Message

from src.libraries.maimai_best_50 import generate50
from src.libraries.tool import hash
from src.libraries.maimaidx_music import *
from src.libraries.image import *
from src.libraries.maimai_best_40 import generate, diffs, combo, BestList, generate_all, computeRa
import re

global last, FILE_PATH
last = [{'qq': '', 'last_time': 0.0}]
FILE_PATH = "file:///F:/maibot/bot/mai-bot-main/src/static/mai/cover/musicid.png"

ALL_VERSION = ['maimai', 'maimai PLUS', 'maimai GreeN', 'maimai GreeN PLUS', 'maimai ORANGE',
               'maimai ORANGE PLUS', 'maimai PiNK', 'maimai PiNK PLUS', 'maimai MURASAKi',
               'maimai MURASAKi PLUS', 'MiLK PLUS', 'maimai MiLK', 'maimai FiNALE',
               'maimai でらっくす PLUS', 'maimai でらっくす', 'maimai でらっくす Splash', 'maimai でらっくす Splash PLUS']


def append_music(completed_music, current_music):
    completed_music.append({'id': current_music['id'], 'title': current_music['title'],
                            'achievements': current_music['achievements'], 'fc': current_music['fc'],
                            'level_index': current_music['level_index']})


def rand_song(music, nickname):
    # messages = []
    # for music in musics:
    diff = ['绿', '黄', '红', '紫', '白']
    fi = music['fc']
    fc = ["", "fc", "fcp", "ap", "app"]
    fc_ori = ["没fc", "FC", "FC+", "AP", "AP+"]
    # if "" == str(fi):
    #     fi = "没fc"
    ra = computeRa(float(music['ds']), float(music['achievements']))

    return Message([{
        "type": "text",
        "data": {
            "text": f"这是{nickname}的{music['id']}.{music['title']}的成绩嗷：\n"
        }
    }, {
        "type": "image",
        "data": {
            "file": f"https://www.diving-fish.com/covers/{get_cover_len4_id(music['id'])}.png"
        }
    }, {
        "type": "text",
        "data": {
            "text": f"\n定级:{diff[music['level_index']]}{music['ds']}  完成度:{music['achievements']}%  分数:{ra} 评级: {fc_ori[fc.index(str(fi))]} "
        }
    }])


# type 0-分数列表  1-随机成绩 2-查询成绩
async def timer(event: Event, msg, sec: int, querytype: int):
    global last
    index = -1
    for i in range(len(last)):
        if last[i]['qq'] == str(event.get_user_id()):
            index = i
            break
    if index == -1:
        # 未发送过
        last.append({'qq': str(event.get_user_id()), 'last_time': time.time()})
        return True
    else:
        # 发送过
        current_time = time.time()
        interval = current_time - float(last[index]['last_time'])
        # print("间隔为" + str(interval) + "秒")
        if "1909886526" == str(event.get_user_id()) or "794191505" == str(event.get_user_id()) \
                or "2138252153" == str(event.get_user_id()) or "2693862500" == str(event.get_user_id()):
            # if "794191505" != str(event.get_user_id()):
            last[index]['last_time'] = current_time
            return True
        if interval <= sec:
            if querytype == 0:
                # 分数列表
                if random.randint(0, 9) <= 1:
                    await query_score_by_dif.send("真的有那么急？给你减10秒吧，还有%d秒" % (sec - interval - 10))
                    last[index]['last_time'] = last[index]['last_time'] - 10
                    return False
                await query_score_by_dif.send(msg % (sec - interval + 20))
                last[index]['last_time'] = last[index]['last_time'] + 20
            elif querytype == 1:
                # 随机成绩
                if random.randint(0, 9) <= 1:
                    await get_rand_score.send("真的有那么急？给你减10秒吧，还有%d秒" % (sec - interval - 10))
                    last[index]['last_time'] = last[index]['last_time'] - 10
                    return False

                random_time = random.randint(20, 100)  # 随机20到100秒
                await get_rand_score.send(msg % (random_time, (sec - interval + random_time)))
                last[index]['last_time'] = last[index]['last_time'] + random_time
            elif querytype == 2:
                # 查询成绩
                if random.randint(0, 9) <= 1:
                    await get_score.send("真的有那么急？给你减10秒吧，还有%d秒" % (sec - interval - 10))
                    last[index]['last_time'] = last[index]['last_time'] - 10
                    return False
                await get_score.send(msg % (sec - interval + 20))
                last[index]['last_time'] = last[index]['last_time'] + 20

            return False
        else:
            last[index]['last_time'] = current_time
            return True


def song_txt(music: Music):
    return Message([
        {
            "type": "text",
            "data": {
                "text": f"{music['id']}. {music['title']}\n"
            }
        },
        {
            "type": "image",
            "data": {
                # "file": FILE_PATH.replace('musicid', music['id'])
                "file": f"https://www.diving-fish.com/covers/{get_cover_len4_id(music['id'])}.png"
            }
        },
        {
            "type": "text",
            "data": {
                "text": f"\n{'/'.join(music.level)}"
            }
        }
    ])


def inner_level_q(ds1, ds2=None):
    result_set = []
    diff_label = ['Bas', 'Adv', 'Exp', 'Mst', 'ReM']
    if ds2 is not None:
        music_data = total_list.filter(ds=(ds1, ds2))
    else:
        music_data = total_list.filter(ds=ds1)
    for music in sorted(music_data, key=lambda i: int(i['id'])):
        for i in music.diff:
            result_set.append((music['id'], music['title'], music['ds'][i], diff_label[i], music['level'][i]))
    return result_set


inner_level = on_command('inner_level ', aliases={'定数查歌 '})


@inner_level.handle()
async def _(bot: Bot, event: Event, state: T_State):
    argv = str(event.get_message()).strip().split(" ")
    if len(argv) > 2 or len(argv) == 0:
        await inner_level.finish("命令格式为\n定数查歌 <定数>\n定数查歌 <定数下限> <定数上限>")
        return
    if len(argv) == 1:
        result_set = inner_level_q(float(argv[0]))
        msg = f'''   定数{float(argv[0])}的歌曲有以下{len(result_set)}首   \n'''
    else:
        result_set = inner_level_q(float(argv[0]), float(argv[1]))
        msg = f'''   定数在{float(argv[0])}和{float(argv[1])}之间的歌曲有以下{len(result_set)}首   \n'''
    if 50 < len(result_set) < 120:
        for elem in result_set:
            msg += f'''    {elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})   \n  '''
        await query_score_by_dif.send(Message([{
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(text_to_image(msg)), encoding='utf-8')}"
            }
        }]))
        return
    if len(result_set) >= 120:
        await inner_level.finish(f"结果过多（{len(result_set)} 条），请缩小搜索范围。")
        return
    if len(result_set) == 0:
        await inner_level.send("你好牛哦，Sega都要专程邀请你去脸滚键盘（我才不说是定级呢")
        return
    s = ""
    for elem in result_set:
        s += f"{elem[0]}. {elem[1]} {elem[3]} {elem[4]}({elem[2]})\n"
    await inner_level.finish(s.strip())


spec_rand = on_regex(r"^随个(?:dx|sd|标准)?[绿黄红紫白]?[0-9]+\+?")


@spec_rand.handle()
async def _(bot: Bot, event: Event, state: T_State):
    level_labels = ['绿', '黄', '红', '紫', '白']
    regex = "随个((?:dx|sd|标准))?([绿黄红紫白]?)([0-9]+\.?[0-9]?\+?)"
    res = re.match(regex, str(event.get_message()).lower())
    try:
        if res.groups()[0] == "dx":
            tp = ["DX"]
        elif res.groups()[0] == "sd" or res.groups()[0] == "标准":
            tp = ["SD"]
        else:
            tp = ["SD", "DX"]
        level = res.groups()[2]
        isds = False
        if level.__contains__(".") and not level.__contains__("+"):  # 定数随歌形式
            isds = True
        elif not level.__contains__(".") and level.__contains__("+"):  # 等级随歌形式
            isds = False
        elif level.__contains__(".") and level.__contains__("+"):
            await spec_rand.send("你好好看看你写的语法")
            return
        else:
            isds = False
        if res.groups()[1] == "":
            if isds:  # 定数随歌形式
                music_data = total_list.filter(ds=float(level), type=tp)
            else:  # 等级随歌形式
                music_data = total_list.filter(level=level, type=tp)
        else:
            if isds:  # 定数随歌形式
                music_data = total_list.filter(ds=float(level), diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)
            else:  # 等级随歌形式
                music_data = total_list.filter(level=level, diff=['绿黄红紫白'.index(res.groups()[1])], type=tp)
        if level.endswith("15") or level.__contains__("15.0"):
            await spec_rand.send("喜欢打潘是吧，潘小鬼是吧，才不告诉你id是834呢")
            return
        if isds and float(level) > 15:
            await spec_rand.send("哪有这么高定数的歌啊，不如你自己写个谱，定多少你说的算")
            return
        if len(music_data) == 0:
            rand_result = "没有这样的歌嗷"
        else:
            rand_result = song_txt(music_data.random())
        await spec_rand.send(rand_result)
    except Exception as e:
        print(e)
        await spec_rand.finish("随歌都能随歪来？")


mr = on_regex(r".*maimai.*什么")


@mr.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await mr.finish(song_txt(total_list.random()))


search_music = on_regex(r"^查歌.+")


@search_music.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "查歌(.+)"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        await search_music_by_bpm.send("你歌名呢？好好看看语法奥")
        return
    res = total_list.filter(title_search=name)
    if len(res) == 0:
        await search_music.send("没有没有没有！")
    elif len(res) < 50:
        search_result = ""
        for music in sorted(res, key=lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await search_music.finish(Message([
            {"type": "text",
             "data": {
                 "text": search_result.strip()
             }}]))
    else:
        await search_music.send(f"结果太多了（{len(res)} 条），人家塞不下了")


# 根据bpm查歌
search_music_by_bpm = on_regex(r"^bpm查歌.+")


@search_music_by_bpm.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "bpm查歌(.+)"
    argv = str(event.get_message()).strip().split("查歌")[1].strip().split(" ")

    if len(argv) > 2 or len(argv) == 0:
        await inner_level.finish("命令格式为\nbpm查歌 <bpm>\nbpm查歌 <bpm下限> <bpm上限>")
        return
    res = ""
    if len(argv) == 1:
        res = total_list.filter(bpm=float(argv[0]))
    else:
        res = total_list.filter(bpm=(float(argv[0]), float(argv[1])))

    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        await search_music_by_bpm.send("你bpm呢？好好看看语法奥")
        return
    # res = total_list.filter(bpm=float(name))
    if len(res) == 0:
        await search_music_by_bpm.send("本bot不建议脸滚键盘哒")
    elif len(res) < 120:
        # print(res)
        les_split = sorted(res, key=lambda i: int(i['basic_info']['bpm']))
        search_result = ""
        if len(argv) == 1:
            search_result = "   bpm为" + name + "的歌曲共有以下" + str(len(les_split)) + "首：\n   "
        else:
            search_result = "   bpm在" + argv[0] + "和" + argv[1] + "之间的的歌曲共有以下" + str(len(les_split)) + "首：\n   "

        for k in range(0, len(les_split)):
            search_result += f"   {les_split[k]['id']}. {les_split[k]['title']}({les_split[k]['basic_info']['bpm']})   \n   "
        await search_music_by_bpm.send(Message([{
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(text_to_image(search_result)), encoding='utf-8')}"
            }
        }]))
    else:
        await search_music_by_bpm.finish(f"结果过多（{len(res)} 条），请缩小搜索范围。")
        return


# 根据artist查歌
search_music_by_artist = on_regex(r"^艺术家查歌.+")


@search_music_by_artist.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "艺术家查歌(.+)"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        await search_music_by_artist.send("你艺术家呢？难道你是艺术家？")
        return
    res = total_list.filter(artist=name)
    if len(res) == 0:
        await search_music_by_artist.send("没有！实在不行你来当曲师？")
    elif len(res) < 50:
        search_result = "艺术家包含" + name + "的歌曲共有以下" + str(len(res)) + "首：\n"
        for music in sorted(res, key=lambda i: int(i['id'])):
            search_result += f"{music['id']}. {music['title']}\n"
        await search_music_by_artist.finish(Message([
            {"type": "text",
             "data": {
                 "text": search_result.strip()
             }}]))
    else:
        les_split = sorted(res, key=lambda i: int(i['id']))
        search_result = "   艺术家包含" + name + "的歌曲共有以下" + str(len(les_split)) + "首：\n   "
        for k in range(0, len(les_split)):
            search_result += f"   {les_split[k]['id']}. {les_split[k]['title']}   \n   "
        await search_music_by_artist.send(Message([{
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(text_to_image(search_result)), encoding='utf-8')}"
            }
        }]))


# 根据谱师查歌
search_music_by_chart = on_regex(r"^谱师查歌.+")


@search_music_by_chart.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "谱师查歌(.+)"
    name = re.match(regex, str(event.get_message())).groups()[0].strip()
    if name == "":
        await search_music_by_chart.send("你谱师呢？难道你是谱师？")
        return
    res = total_list.filter(charter=name)
    if len(res) == 0:
        await search_music_by_chart.send("自己写谱吧，别为难我了")
    elif len(res) < 50:
        search_result = "谱师包含" + name + "的歌曲共有以下" + str(len(res)) + "首：\n"
        for music in sorted(res, key=lambda i: int(i['id'])):
            tt = "（"
            print(name.lower())
            print(music.charts[3])
            if name.lower() in music.charts[2].charter.lower():
                tt += "红"
            if name.lower() in music.charts[3].charter.lower():
                tt += "紫"
            if len(music.charts) == 5 and name.lower() in music.charts[4].charter.lower():
                tt += "白"
            tt += "）"
            # print(music.title)
            # print(music.title)
            search_result += f"{music['id']}.{music['title']}{tt}\n"
        await search_music_by_chart.finish(Message([
            {"type": "text",
             "data": {
                 "text": search_result.strip()
             }}]))
    else:
        les_split = sorted(res, key=lambda i: int(i['id']))
        search_result = "   谱师包含" + name + "的歌曲共有以下" + str(len(les_split)) + "首（包括红谱及以上）：\n   "
        # j = len(les_split)/2
        # print(les_split)
        for k in range(0, len(les_split)):
            tt = "（"
            # print(name.lower())
            # print(les_split[k].charts[3])
            if name.lower() in les_split[k].charts[2].charter.lower():
                tt += "红"
            if name.lower() in les_split[k].charts[3].charter.lower():
                tt += "紫"
            if len(les_split[k].charts) == 5 and name.lower() in les_split[k].charts[4].charter.lower():
                tt += "白"
            tt += "）"
            # print(music.title)
            # print(music.title)
            search_result += f"   {les_split[k]['id']}. {les_split[k]['title']}{tt}   \n   "
        await search_music_by_chart.send(Message([{
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(text_to_image(search_result)), encoding='utf-8')}"
            }
        }]))
        #
        # await search_music_by_chart.send(Message([
        #     {"type": "text",
        #      "data": {
        #          "text": search_result.strip()
        #      }}]))
        # search_result = "后"+str(int(len(les_split)-len(les_split)/2))+"条：\n"
        # for k in range(j, len(les_split)):
        #     search_result += f"{les_split[k]['id']}. {les_split[k]['title']}\n"
        # await search_music_by_chart.send(Message([
        #     {"type": "text",
        #      "data": {
        #          "text": search_result.strip()
        #      }}]))


# 找1
search1 = on_command("有1吗", aliases={'我是0', '有一吗'})


@search1.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await search1.send("你是0就有1捏，抬高抬高")


# 烟
kick_in_ass = on_command("烟我")


@kick_in_ass.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await kick_in_ass.send("屁股抬高点")


# 难度分数列表
query_score_by_dif = on_regex(r"^([0-9]+\+?)分数列表")


@query_score_by_dif.handle()
async def _(bot: Bot, event: Event, state: T_State):
    time_allow = await timer(event, "别急，喜欢急？给你再加10秒，还有%d秒", 180, 0)
    if not time_allow:
        return
    regex = "^([0-9]+\+?)"
    level = re.match(regex, str(event.get_message())).groups()[0]
    if level == "":
        await query_score_by_dif.finish("等级填错了你，再看看去")
        return
    # 空 账号 分页  / 空 账号  / 空  / 空 分页
    params = str(event.get_message()).strip().split("分数列表")[1].strip()
    username = ""
    page = 1
    pages = 1
    args = params.split(" ")
    arg1 = args[0]
    if arg1 == "":
        print("无参")
        # 通过qq号查询
        username = params
    elif len(arg1) == 1 and arg1.isdigit() and len(args) == 1:
        page = int(arg1)
        # 获取分页参数
        print("仅分页参数")
    else:
        if len(args) == 1:
            # 仅查账号
            print("仅账号参数")
            username = arg1
        elif len(args) == 2:
            # 账号加分页
            print("账号参数+分页参数")
            username = arg1
            page = int(args[1])
        else:
            print("参数有误")
            return
    if username == "":
        # if "1909886526" == str(event.get_user_id()).strip():
        #     payload = {'username': "zeenay",
        #                'version': ALL_VERSION}
        # else:
        payload = {'qq': str(event.get_user_id()),
                   'version': ALL_VERSION}
    else:
        payload = {'username': username,
                   'version': ALL_VERSION}
    img, t_list, success = await generate_all(payload)
    if success == 400:
        await query_score_by_dif.send("没找见这人的账号")
        return
    elif success == 403:
        await query_score_by_dif.send("人不让别人查我怎么查a")
        return
    elif success == 500:
        await query_score_by_dif.send("服务器出错了，和我没关系捏")
        return
    elif success == 423:
        if "1909886526" != str(event.get_user_id()) and "794191505" != str(event.get_user_id()) \
                and "2138252153" != str(event.get_user_id()):
            # if "794191505" != str(event.get_user_id()):
            return await query_score_by_dif.send("暂不可通过账号查询")

    data = t_list
    search_list = list()

    # msg = "你的lv."+level+"分数列表（从高至低，仅包含在b40内）:\n\n\n\n\n\n\n\n"
    msg = "你的lv." + level + "分数列表（从高至低，最多显示25条）:               Created by :QVbot\n"
    for i in range(len(data)):
        # print(data[i])
        if level.__eq__(data[i]['level']):
            # 若等级为该难度+
            search_list.append(data[i])
    if len(search_list) == 0:
        await query_score_by_dif.send("你的lv." + level + "暂时没找到呢")
        return
    else:
        search_list.sort(key=lambda j: float(j['achievements']), reverse=True)
        # print(data[i])
        # print(data[i].title + str(data[i].diff) + str(data[i].tp))
        # print(search_list)
        if len(search_list) % 25 == 0:
            pages = int(len(search_list) / 25)
        else:
            pages = int(len(search_list) / 25 + 1)
        if page > pages:
            print("越界！")
            await query_score_by_dif.send("你没有打过那么多歌，仅显示第一页")
            page = 1
        for i in range(25 * (page - 1), min(len(search_list), 25 * page)):
            ra = computeRa(float(search_list[i]['ds']), float(search_list[i]['achievements']))
            msg += f'''    {i + 1}.{search_list[i]['achievements']}% [{search_list[i]['type']}] {diffs[search_list[i]['level_index']]} {search_list[i]['title']}({search_list[i]['ds']}) 分数：{ra}\n   '''

    msg += f'''   页{page}，共{pages}页   '''
    await query_score_by_dif.send(Message([{
        "type": "image",
        "data": {
            "file": f"base64://{str(image_to_base64(text_to_image(msg)), encoding='utf-8')}"
        }
    }]))


query_chart = on_regex(r"^([绿黄红紫白]?)id([0-9]+)")


@query_chart.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "([绿黄红紫白]?)id([0-9]+)"
    groups = re.match(regex, str(event.get_message())).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    if groups[0] != "":
        try:
            level_index = level_labels.index(groups[0])
            level_name = ['Basic', 'Advanced', 'Expert', 'Master', 'Re: MASTER']
            name = groups[1]
            music = total_list.by_id(name)
            chart = music['charts'][level_index]
            ds = music['ds'][level_index]
            level = music['level'][level_index]
            file = f"https://www.diving-fish.com/covers/{get_cover_len4_id(music['id'])}.png"
            if len(chart['notes']) == 4:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
BREAK: {chart['notes'][3]}
谱师: {chart['charter']}'''
            else:
                msg = f'''{level_name[level_index]} {level}({ds})
TAP: {chart['notes'][0]}
HOLD: {chart['notes'][1]}
SLIDE: {chart['notes'][2]}
TOUCH: {chart['notes'][3]}
BREAK: {chart['notes'][4]}
谱师: {chart['charter']}'''
            await query_chart.send(Message([
                {
                    "type": "text",
                    "data": {
                        "text": f"{music['id']}. {music['title']}\n"
                    }
                },
                {
                    "type": "image",
                    "data": {
                        "file": f"{file}"
                    }
                },
                {
                    "type": "text",
                    "data": {
                        "text": msg
                    }
                }
            ]))
        except Exception:
            await query_chart.send("未找到该谱面")
    else:
        name = groups[1]
        music = total_list.by_id(name)
        try:
            file = f"https://www.diving-fish.com/covers/{get_cover_len4_id(music['id'])}.png"
            await query_chart.send(Message([
                {
                    "type": "text",
                    "data": {
                        "text": f"{music['id']}. {music['title']}\n"
                    }
                },
                {
                    "type": "image",
                    "data": {
                        "file": f"{file}"
                    }
                },
                {
                    "type": "text",
                    "data": {
                        "text": f"艺术家: {music['basic_info']['artist']}\n分类: {music['basic_info']['genre']}\nBPM: {music['basic_info']['bpm']}\n版本: {music['basic_info']['from']}\n难度: {'/'.join(music['level'])}"
                    }
                }
            ]))
        except Exception:
            await query_chart.send("未找到该乐曲")


wm_list = ['拼机', '推分', '越级', '下埋', '夜勤', '练底力', '练手法', '打旧框', '干饭', '抓绝赞', '收歌']

jrwm = on_command('今日舞萌', aliases={'今日mai'})


@jrwm.handle()
async def _(bot: Bot, event: Event, state: T_State):
    qq = int(event.get_user_id())
    h = hash(qq)
    rp = h % 100
    wm_value = []
    for i in range(11):
        wm_value.append(h & 3)
        h >>= 2
    s = f"今日人品值：{rp}\n"
    for i in range(11):
        if wm_value[i] == 3:
            s += f'宜 {wm_list[i]}\n'
        elif wm_value[i] == 0:
            s += f'忌 {wm_list[i]}\n'
    s += "QVbot提醒您：打机时不要大力拍打或滑动哦\n今日推荐歌曲："
    music = total_list[h % len(total_list)]
    await jrwm.finish(Message([
                                  {"type": "text", "data": {"text": s}}
                              ] + song_txt(music)))


music_aliases = defaultdict(list)
f = open('src/static/aliases.csv', 'r', encoding='utf-8')
tmp = f.readlines()
f.close()
for t in tmp:
    arr = t.strip().split('\t')
    for i in range(len(arr)):
        if arr[i] != "":
            music_aliases[arr[i].lower()].append(arr[0])

find_song = on_regex(".+是什么歌")


@find_song.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "(.+)是什么歌"
    name = re.match(regex, str(event.get_message())).groups()[0].strip().lower()
    if name not in music_aliases:
        await find_song.finish("未找到此歌曲 ")
        # DX 歌曲别名收集计划：https: // docs.qq.com / sheet / DQ0pvUHh6b1hjcGpl
        return
    result_set = music_aliases[name]
    if len(result_set) == 1:
        music = total_list.by_title(result_set[0])
        if music is None:
            await find_song.finish("你这首歌没有了qaq ")
        else:
            await find_song.finish(Message([{"type": "text", "data": {"text": "您要找的是不是"}}] + song_txt(music)))
    else:
        s = '\n'.join(result_set)
        await find_song.finish(f"您要找的可能是以下歌曲中的其中一首：\n{s}")


query_score = on_command('分数线')


@query_score.handle()
async def _(bot: Bot, event: Event, state: T_State):
    r = "([绿黄红紫白])(id)?([0-9]+)"
    argv = str(event.get_message()).strip().split(" ")
    if len(argv) == 1 and argv[0] == '帮助':
        s = '''此功能为查找某首歌分数线设计。
命令格式：分数线 <难度+歌曲id> <分数线>
例如：分数线 紫799 100
命令将返回分数线允许的 TAP GREAT 容错以及 BREAK 50落等价的 TAP GREAT 数。
以下为 TAP GREAT 的对应表：
GREAT/GOOD/MISS
TAP\t1/2.5/5
HOLD\t2/5/10
SLIDE\t3/7.5/15
TOUCH\t1/2.5/5
BREAK\t5/12.5/25(外加200落)'''
        await query_score.send(Message([{
            "type": "image",
            "data": {
                "file": f"base64://{str(image_to_base64(text_to_image(s)), encoding='utf-8')}"
            }
        }]))
    elif len(argv) == 2:
        try:
            grp = re.match(r, argv[0]).groups()
            level_labels = ['绿', '黄', '红', '紫', '白']
            level_labels2 = ['Basic', 'Advanced', 'Expert', 'Master', 'Re:MASTER']
            level_index = level_labels.index(grp[0])
            chart_id = grp[2]
            line = float(argv[1])
            music = total_list.by_id(chart_id)
            chart: Dict[Any] = music['charts'][level_index]
            tap = int(chart['notes'][0])
            slide = int(chart['notes'][2])
            hold = int(chart['notes'][1])
            touch = int(chart['notes'][3]) if len(chart['notes']) == 5 else 0
            brk = int(chart['notes'][-1])
            total_score = 500 * tap + slide * 1500 + hold * 1000 + touch * 500 + brk * 2500
            break_bonus = 0.01 / brk
            break_50_reduce = total_score * break_bonus / 4
            reduce = 101 - line
            if reduce <= 0 or reduce >= 101:
                raise ValueError
            await query_chart.send(f'''{music['title']} {level_labels2[level_index]}
分数线 {line}% 允许的最多 TAP GREAT 数量为 {(total_score * reduce / 10000):.2f}(每个-{10000 / total_score:.4f}%),
BREAK 50落(一共{brk}个)等价于 {(break_50_reduce / 100):.3f} 个 TAP GREAT(-{break_50_reduce / total_score * 100:.4f}%)''')
        except Exception:
            await query_chart.send("格式错误，输入“分数线 帮助”以查看帮助信息")


# 原b40方法
best_40_pic = on_command('b40')


@best_40_pic.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await best_40_pic.send("为防止冲突，请使用qvb40指令捏~")
    return
    # username = str(event.get_message()).strip()
    # if username == "":
    #     payload = {'qq': str(event.get_user_id())}
    # else:
    #     payload = {'username': username}
    # img, success = await generate(payload)
    # if success == 400:
    #     await best_40_pic.send("未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
    # elif success == 403:
    #     await best_40_pic.send("该用户禁止了其他人获取数据。")
    # else:
    #     await best_40_pic.send(Message([
    #         {
    #             "type": "image",
    #             "data": {
    #                 "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
    #             }
    #         }
    #     ]))


# 为防止重复，更改前缀
qvbest_40_pic = on_command("qvb40")


@qvbest_40_pic.handle()
async def _(bot: Bot, event: Event, state: T_State):
    username = str(event.get_message()).strip()
    if username == "":
        # if "1909886526" == str(event.get_user_id()).strip():
        #     payload = {'username': 'zeenay'}
        # else:
        payload = {'qq': str(event.get_user_id())}
    else:
        payload = {'username': username}
    img, t_list, success = await generate(payload)
    if success == 400:
        await qvbest_40_pic.send("鬼也玩舞萌了？")
    elif success == 403:
        await qvbest_40_pic.send("人不让别人查我怎么查a")
    elif success == 423:
        if "1909886526" != str(event.get_user_id()) and "794191505" != str(event.get_user_id()) \
                and "2138252153" != str(event.get_user_id()):
            # if "794191505" != str(event.get_user_id()):
            await qvbest_40_pic.send("暂不可通过账号查询")
        else:
            await qvbest_40_pic.send(Message([
                {
                    "type": "image",
                    "data": {
                        "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
                    }
                }
            ]))
    else:
        await qvbest_40_pic.send(Message([
            {
                "type": "image",
                "data": {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
                }
            }
        ]))


# 测试用方法
test_qq = on_command("查询qvb40")


@test_qq.handle()
async def _(bot: Bot, event: Event, state: T_State):
    if "1909886526" != str(event.get_user_id()) and "794191505" != str(event.get_user_id()) \
            and "2138252153" != str(event.get_user_id()):
        # if "794191505" != str(event.get_user_id()):
        return
    args = str(event.get_message()).strip().split(" ")
    print(args)
    username = ""
    if len(args) == 1 and args[0] != '':
        username = args[0]
    else:
        return
    payload = {'qq': str(username)}
    img, t_list, success = await generate(payload)
    if success == 400:
        await test_qq.send("鬼也玩舞萌了？")
    elif success == 403:
        await test_qq.send("人不让别人查我怎么查a")
    elif success == 423:
        if "1909886526" != str(event.get_user_id()) and "794191505" != str(event.get_user_id()) \
                and "2138252153" != str(event.get_user_id()):
            # if "794191505" != str(event.get_user_id()):
            await test_qq.send("暂不可通过账号查询")
        else:
            await test_qq.send(Message([
                {
                    "type": "image",
                    "data": {
                        "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
                    }
                }
            ]))
    else:
        await test_qq.send(Message([
            {
                "type": "image",
                "data": {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
                }
            }
        ]))


# 原b50方法
best_50_pic = on_command('b50')


@best_50_pic.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await best_50_pic.send("为防止冲突，请使用qvb50指令捏~")
    return


qvbest_50_pic = on_command("qvb50")


@qvbest_50_pic.handle()
async def _(bot: Bot, event: Event, state: T_State):
    username = str(event.get_message()).strip()
    if username == "":
        # if "1909886526" == str(event.get_user_id()).strip():
        #     payload = {'username': 'zeenay'}
        # else:
        payload = {'qq': str(event.get_user_id())}
    else:
        payload = {'username': username}
    img, t_list, success = await generate50(payload)
    if success == 400:
        await qvbest_50_pic.send("鬼也玩舞萌了？")
    elif success == 403:
        await qvbest_50_pic.send("人不让别人查我怎么查a")
    elif success == 423:
        if "1909886526" != str(event.get_user_id()) and "794191505" != str(event.get_user_id()) \
                and "2138252153" != str(event.get_user_id()):
            # if "794191505" != str(event.get_user_id()):
            await qvbest_50_pic.send("暂不可通过账号查询")
        else:
            await qvbest_50_pic.send(Message([
                {
                    "type": "image",
                    "data": {
                        "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
                    }
                }
            ]))
    else:
        await qvbest_50_pic.send(Message([
            {
                "type": "image",
                "data": {
                    "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
                }
            }
        ]))


# 暂废弃
qvtest = on_command("Abandoned test")


@qvtest.handle()
async def _(bot: Bot, event: Event, state: T_State):
    username = str(event.get_message()).strip()
    p = ""
    # if username == "":
    #     p = {'qq': str(event.get_user_id()),
    #          'version': ALL_VERSION}
    # else:
    #     p = {'username': username,
    #          'version': ALL_VERSION}
    # # print(p)
    if username == "":
        payload = {'qq': str(event.get_user_id())}
    else:
        payload = {'username': username}
    img, t_list, success = await generate(payload)
    if success == 400:
        await qvtest.send("没找到恁账号捏，请前往查分器网站绑定qq")
    elif success == 403:
        await qvtest.send("人不让别人查我怎么查a")
    elif success == 500:
        print("服务器出错了")
        # await qvtest.send("人不让别人查我怎么查a")
    else:
        print(t_list)
        pass
        # await qvtest.send(Message([
        #     {
        #         "type": "image",
        #         "data": {
        #             "file": f"base64://{str(image_to_base64(img), encoding='utf-8')}"
        #         }
        #     }
        # ]))


get_rand_score = on_command("随机成绩", aliases={'sjcj'})


@get_rand_score.handle()
async def _(bot: Bot, event: Event, state: T_State):
    time_allow = await timer(event, "别急，喜欢急？给你再加%d秒，还有%d秒", 600, 1)
    if not time_allow:
        return
    username = str(event.get_message()).strip()
    if username == "":
        # if "1909886526" == str(event.get_user_id()).strip():
        #     payload = {'username': "zeenay",
        #                'version': ALL_VERSION}
        # else:
        payload = {'qq': str(event.get_user_id()),
                   'version': ALL_VERSION}
    else:
        payload = {'username': username,
                   'version': ALL_VERSION}
    img, t_list, success = await generate_all(payload)
    if success == 400:
        await get_rand_score.send("没找到恁账号捏，请前往查分器网站绑定qq")
        return
    elif success == 403:
        await get_rand_score.send("人不让别人查我怎么查a")
        return
    elif success == 500:
        print("服务器出错了")
        # await get_score.send("人不让别人查我怎么查a")
        return
    elif success == 423:
        if "1909886526" != str(event.get_user_id()) and "794191505" != str(event.get_user_id()) \
                and "2138252153" != str(event.get_user_id()):
            # if "794191505" != str(event.get_user_id()):
            await get_rand_score.send("暂不可通过账号查询")
            return
    if len(t_list) == 0:
        await get_rand_score.send("暂无数据")
        return
    # musics = []
    # for i in range(1):
    music = t_list[random.randint(0, len(t_list) - 1)]
    nickname = ''
    if not event.get_event_description().__contains__("群"):
        nickname = "你"
        # await get_score.send("暂时只能在群内使用")
    else:
        for u in await bot.get_group_member_list(group_id=int(event.group_id), self_id=2629842177):
            # print(u){'age': 0, 'area': '', 'card': '今天开始不做鸽子', 'card_changeable': False, 'group_id': 946264039,
            # 'join_time': 1632666105, 'last_sent_time': 1637505482, 'level': '1', 'nickname': '星間 小夜曲',
            # 'role': 'admin', 'sex': 'unknown', 'shut_up_timestamp': 0, 'title': '', 'title_expire_time': 0,
            # 'unfriendly': False, 'user_id': 153731415}
            if str(u['user_id']) == str(event.get_user_id()):
                if u['card'] == "":
                    nickname = u['nickname']
                else:
                    nickname = u['card']
    msg = rand_song(music, nickname)
    await get_rand_score.send(msg)


get_score = on_regex(r"^查询成绩 ([绿黄红紫白])id([0-9]+)")


@get_score.handle()
async def _(bot: Bot, event: Event, state: T_State):
    regex = "([绿黄红紫白])id([0-9]+)"
    groups = re.search(regex, str(event.get_message())).groups()
    level_labels = ['绿', '黄', '红', '紫', '白']
    level = level_labels.index(groups[0])
    # print(level)
    if level < 0:
        await get_score.finish("输入参数有误")
        return
    id = groups[1]
    time_allow = await timer(event, "别急，喜欢急？给你再加20秒，还有%d秒", 600, 2)
    if not time_allow:
        return
    # if "1909886526" == str(event.get_user_id()).strip():
    #     payload = {'username': "zeenay",
    #                'version': ALL_VERSION}
    else:
        payload = {'qq': str(event.get_user_id()),
                   'version': ALL_VERSION}

    img, t_list, success = await generate_all(payload)
    if success == 400:
        await get_score.send("没找到恁账号捏，请前往查分器网站绑定qq")
        return
    elif success == 403:
        await get_score.send("人不让别人查我怎么查a")
        return
    elif success == 500:
        print("服务器出错了")
        # await get_score.send("人不让别人查我怎么查a")
        return
    elif success == 423:
        if "1909886526" != str(event.get_user_id()) and "794191505" != str(event.get_user_id()) \
                and "2138252153" != str(event.get_user_id()):
            # if "794191505" != str(event.get_user_id()):
            await get_score.send("暂不可通过账号查询")
            return
    if len(t_list) == 0:
        await get_score.send("暂无数据")
        return
    search_list = list()
    res = ""
    # "verlist": [{"achievements": 99.4629, "fc": "", "fs": "", "id": 71, "level": "11",
    # "level_index": 3,
    #              "title": "\u30de\u30c8\u30ea\u30e7\u30b7\u30ab", "type": "SD"}
    for music in t_list:
        if int(music['id']) == int(id):
            search_list.append(music)
    if len(search_list) == 0:
        await get_score.finish("没打过这歌")
        return
    # 有数据
    for music in search_list:
        if int(music['level_index']) == int(level):
            # 查询到
            res = music
    if res == "":
        await get_score.send("没打过这谱面")
        return
    nickname = ''
    if not event.get_event_description().__contains__("群"):
        nickname = "你"
        # await get_score.send("暂时只能在群内使用")
    else:
        for u in await bot.get_group_member_list(group_id=int(event.group_id), self_id=2629842177):
            # print(u){'age': 0, 'area': '', 'card': '今天开始不做鸽子', 'card_changeable': False, 'group_id': 946264039,
            # 'join_time': 1632666105, 'last_sent_time': 1637505482, 'level': '1', 'nickname': '星間 小夜曲',
            # 'role': 'admin', 'sex': 'unknown', 'shut_up_timestamp': 0, 'title': '', 'title_expire_time': 0,
            # 'unfriendly': False, 'user_id': 153731415}
            if str(u['user_id']) == str(event.get_user_id()):
                if u['card'] == "":
                    nickname = u['nickname']
                else:
                    nickname = u['card']
    msg = rand_song(res, nickname)
    await get_score.finish(msg)

# get_plate = on_regex(r"^([真超檄橙晓桃樱紫菫白雪辉熊华爽])([极将舞舞神])进度")
#
#
# @get_plate.handle()
# async def _(bot: Bot, event: Event, state: T_State):
#     regex = "([真超檄橙晓桃樱紫菫白雪辉熊华爽])([极将舞神])"
#     all_version = {
#         "maimai PLUS": "真", "maimai GreeN": "超", "maimai GreeN PLUS": "檄", "maimai ORANGE": "橙",
#         "maimai ORANGE PLUS": "晓", "maimai PiNK": "桃", "maimai PiNK PLUS": "樱", "maimai MURASAKi": "紫",
#         "maimai MURASAKi PLUS": "菫", "maimai MiLK": "白", "MiLK PLUS": "雪", "maimai FiNALE": "辉",
#         "maimai でらっくす": "熊", "maimai でらっくす PLUS": "华", "maimai でらっくす Splash": "爽"
#     }
#     groups = re.search(regex, str(event.get_message())).groups()
#     version = ""
#     plate = groups[1]
#     for v, p in all_version.items():
#         if str(groups[0]) == str(p):
#             version = v
#     if version == "":
#         await get_plate.finish('参数有误')
#         return
#     print(str(version) + str(plate))
#
#     version_list = total_list.filter(version=version)
#     # [{'id': '242', 'title': 'ナミダと流星', 'type': 'SD', 'ds': [5.0, 7.0, 9.8, 12.0], 'level': ['5', '7', '9+', '12'],
#     #   'cids': [576, 577, 578, 579], 'charts': [{'notes': [121, 11, 5, 2], 'charter': '-'},
#     #                                            {'notes': [279, 26, 13, 8], 'charter': '-'},
#     #                                            {'notes': [346, 43, 36, 4], 'charter': 'Revo@LC'},
#     #                                            {'notes': [312, 50, 150, 5], 'charter': 'mai-Star'}],
#     #   'basic_info': {'title': 'ナミダと流星', 'artist': '芳川よしの', 'genre': 'maimai', 'bpm': 190, 'release_date': '',
#     #                  'from': 'maimai ORANGE PLUS', 'is_new': False}}]
#     #                  fs = ["", "fs", "fsp", "fsd", "fsdp"][m["syncStatus"]]
#     # if "1909886526" == str(event.get_user_id()).strip():
#     #     payload = {'username': "zeenay",
#     #                'version': [version]}
#     # else:
#     payload = {'qq': str(event.get_user_id()),
#                'version': [version]}
#     img, t_list, success = await generate_all(payload)
#     if success == 400:
#         await get_plate.send("没找到恁账号捏，请前往查分器网站绑定qq")
#         return
#     elif success == 403:
#         await get_plate.send("人不让别人查我怎么查a")
#         return
#     elif success == 500:
#         print("服务器出错了")
#         # await get_score.send("人不让别人查我怎么查a")
#         return
#     elif success == 423:
#         if "1909886526" != str(event.get_user_id()) and "794191505" != str(event.get_user_id()):
#             await get_plate.send("暂不可通过账号查询")
#             return
#     if len(t_list) == 0:
#         await get_plate.send("暂无数据")
#         return
#     print(f'''版本共有{len(version_list)}首歌，你打过{len(t_list)}首''')
#     completed_music: List = list()
#     level_count = [0, 0]  # 表示紫谱歌/白谱歌数量
#     for current_music in t_list:
#         # 打过的歌曲
#         # "current_music": [{"achievements": 99.4629, "fc": "", "fs": "", "id": 71, "level": "11",
#         #     # "level_index": 3,
#         #     #              "title": "\u30de\u30c8\u30ea\u30e7\u30b7\u30ab", "type": "SD"}
#         for all_music in version_list:
#             # 所有歌曲
#             if int(all_music['id']) == int(current_music['id']):
#                 # 相同歌曲
#                 if str(plate) == "极" and str(current_music['fc']) != "":
#                     # 完成极要求，进行添加
#                     append_music(completed_music, current_music)
#
#                 if str(plate) == "将" and float(current_music['achievements']) >= 100:
#                     # 完成将要求，进行添加
#                     append_music(completed_music, current_music)
#
#                 if str(plate) == "舞" and (str(current_music['fs']) == "fsd" or str(current_music['fs']) == "fsdp"):
#                     # 完成舞舞要求，进行添加
#                     append_music(completed_music, current_music)
#
#                 if str(plate) == "神" and (str(current_music['fc']) == "ap" or str(current_music['fc']) == "app"):
#                     # 完成神要求，进行添加
#                     append_music(completed_music, current_music)
#     for all_music in version_list:
#         # 所有歌曲
#         level_count[len(all_music['ds']) - 4] = level_count[len(all_music['ds']) - 4] + 1
#     print(level_count)
#     current_count = [0, 0, 0, 0, 0]
#     for music in completed_music:
#         current_count[int(music['level_index'])] = current_count[int(music['level_index'])] + 1
#     print(current_count)
#     for i in range(len(current_count)):
#         current_count[i] = level_count[0] + level_count[1] - current_count[i]
#     msg = f'''你的{groups[0]}{plate}进度如下：
# 绿谱剩余{current_count[0]}首
# 黄谱剩余{current_count[1]}首
# 红谱剩余{current_count[2]}首
# 紫谱剩余{current_count[3]}首   '''
#     print(str(len(completed_music)))
#     await get_plate.finish(msg)
