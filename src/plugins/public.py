import json
import random
import re

from PIL import Image
from nonebot import on_command, on_message, on_notice, require, get_driver, on_regex
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Message, Event, Bot
from src.libraries.image import *
from random import randint

from src.libraries.maimai_best_40 import generate_all, computeRa
from src.libraries.maimaidx_music import get_cover_len4_id

ALL_VERSION = ['maimai', 'maimai PLUS', 'maimai GreeN', 'maimai GreeN PLUS', 'maimai ORANGE',
               'maimai ORANGE PLUS', 'maimai PiNK', 'maimai PiNK PLUS', 'maimai MURASAKi',
               'maimai MURASAKi PLUS', 'MiLK PLUS', 'maimai MiLK', 'maimai FiNALE',
               'maimai でらっくす PLUS', 'maimai でらっくす', 'maimai でらっくす Splash', 'maimai でらっくす Splash PLUS']
FILE_PATH = "file:///F:/maibot/bot/mai-bot-main/src/static/mai/cover/musicid.png"


def song_txt(music, nickname):
    rate = ['d', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 's+', 'ss', 'ss+', 'sss', 'sss+']
    # ri = rate[music.scoreId]
    fc = ["", "fc", "fcp", "ap", "app"]
    fc_ori = ["没fc", "FC", "FC+", "AP", "AP+"]
    diff = ['绿', '黄', '红', '紫', '白']
    fi = music['fc']
    # if "" == str(fi):
    #     fi = "没fc"
    ra = computeRa(float(music['ds']), float(music['achievements']))
    return Message([
        {
            "type": "text",
            "data": {
                "text": f"这是{nickname}的{music['id']}.{music['title']}的成绩嗷：\n"
            }
        },
        {
            "type": "image",
            "data": {
                "file": f"https://www.diving-fish.com/covers/{get_cover_len4_id(music['id'])}.png"
            }
        },
        {
            "type": "text",
            "data": {
                "text": f"\n定级:{diff[music['level_index']]}{music['ds']}  完成度:{music['achievements']}%  分数:{ra} 评级: {fc_ori[fc.index(str(fi))]}"
            }
        }
    ])


help = on_command('help')


@help.handle()
async def _(bot: Bot, event: Event, state: T_State):
    help_str = '''可用命令如下：
qvb40 查看qq号绑定账号b40(不可账号查询)
qvb50 查看qq号绑定账号b40(不可账号查询)，有bug，仅供参考
<定级>分数列表 [页数]查看qq绑定账号该定级下的分数从高到低排序，每页最多显示25条，每3分钟只能查询一次
        例：14分数列表 2
今日舞萌 查看今天的舞萌运势
XXXmaimaiXXX什么 随机一首歌
        例：今天maimai什么
随个[dx/标准][绿黄红紫白]<难度或定数> 随机一首指定条件的乐曲，新增支持具体定数语句
        例：随个紫14
艺术家查歌<曲师名称> 查询符合曲师条件的乐曲
        例：艺术家查歌uk
谱师查歌<谱师名称> 查询符合谱师条件的乐曲（仅支持红谱以上）
        例：谱师查歌100号
bpm查歌<歌曲bpm/歌曲bpm下限> [歌曲bpm上限] 查询符合bpm条件的乐曲，上限120条
        例：bpm查歌100 200
查歌<乐曲标题的一部分> 查询符合条件的乐曲
        例：查歌pan
[绿黄红紫白]id<歌曲编号> 查询乐曲信息或谱面信息
        例：紫id834
<歌曲别名>是什么歌 查询乐曲别名对应的乐曲
        例：我是什么歌
定数查歌 <定数>  查询定数对应的乐曲
        例：定数查歌 14.2
定数查歌 <定数下限> <定数上限>
        例：定数查歌 14.1 14.6
分数线 <难度+歌曲id> <分数线> 详情请输入“分数线 帮助”查看
随机成绩  查询随机一条成绩，10分钟只能查询一次
查询成绩 [绿黄红紫白]id<歌曲编号>  查询乐曲成绩，10分钟只能查询一次
        例：查询成绩 白id834'''
    await help.send(Message([{
        "type": "image",
        "data": {
            "file": f"base64://{str(image_to_base64(text_to_image(help_str)), encoding='utf-8')}"
        }
    }]))


async def _group_poke(bot: Bot, event: Event, state: dict) -> bool:
    value = (event.notice_type == "notify" and event.sub_type == "poke" and event.target_id == int(bot.self_id))
    return value


poke_list = ['呜呜不要再戳啦', '有考虑过去玩cytus吗', '还戳还戳，戳了几百次还戳', '戳什么啊能不能爪巴', '怎么会有人天天闲着戳人呢',
             '才...才不喜欢被戳呢', '再戳烟你', '你再戳，我就把你的成绩发出来', '嫩喜欢戳怎么不去理论里fd', '别戳了别戳了爬爬爬']
poke = on_notice(rule=_group_poke, priority=10, block=True)


@poke.handle()
async def _(bot: Bot, event: Event, state: T_State):
    nickname = ''
    if event.__getattribute__('group_id') is None:
        # 私聊
        nickname = "你"
        event.__delattr__('group_id')
    else:
        # 群聊，获取昵称
        for u in await bot.get_group_member_list(group_id=int(event.group_id), self_id=2629842177):
            # print(u){'age': 0, 'area': '', 'card': '今天开始不做鸽子', 'card_changeable': False, 'group_id': 946264039,
            # 'join_time': 1632666105, 'last_sent_time': 1637505482, 'level': '1', 'nickname': '星間 小夜曲',
            # 'role': 'admin', 'sex': 'unknown', 'shut_up_timestamp': 0, 'title': '', 'title_expire_time': 0,
            # 'unfriendly': False, 'user_id': 153731415}
            if str(u['user_id']) == str(event.sender_id):
                if u['card'] == "":
                    nickname = u['nickname']
                else:
                    nickname = u['card']
        with open('src/plugins/poke.json', 'r', encoding='utf-8') as f:
            item = json.load(f)
            pokelist = []
            isPoke = False
            for i in range(len(item)):
                id = item[i]['id']
                nick = item[i]['nickname']
                gid = item[i]['gid']
                count = int(item[i]['count'])
                # if str(id) == str(event.sender_id):
                if str(id) == str(event.sender_id):
                    # 若曾经戳过
                    count = count + 1
                    isPoke = True
                pokelist.append({'id': id, 'nickname': nick, 'gid': gid, 'count': count})
            if not isPoke:
                # 没戳过，新增
                # poke_temp = {'id': event.sender_id, 'nickname': nickname, 'gid': group_id, 'count': 1}
                poke_temp = {'id': event.sender_id, 'nickname': nickname, 'gid': event.group_id, 'count': 1}
                pokelist.append(poke_temp)
        with open('src/plugins/poke.json', 'w', encoding='utf-8') as f2:
            print(pokelist[0])
            json.dump(pokelist, f2, ensure_ascii=False)
    # await poke.send(Message([{
    #     "type": "poke",
    #     "data": {
    #         "qq": f"{event.sender_id}"
    #     }
    # }]))
    res = random.randint(0, len(poke_list)*10 - 1)
    # res = 7
    if res >= 10:
        return
    if "1909886526" == str(event.sender_id).strip() or "1069660505" == str(event.sender_id).strip():
        if res < 4:
            res = 7
    if "1309900106" == str(event.sender_id).strip():
        if res < 2:
            res = 7
    if "794191505" == str(event.sender_id).strip():
        res = 7
    await poke.send(poke_list[res])
    # print(event.sender_id)
    # print("794191505" == str(event.sender_id).strip())

    if res == 7:
        # 随机发一张成绩图
        # if "1909886526" == str(event.sender_id).strip():
        #     qq = {'username': 'zeenay',
        #           'version': ALL_VERSION}
        # else:
        qq = {'qq': str(event.sender_id),
              'version': ALL_VERSION}
        img, t_list, success = await generate_all(qq)
        if success == 400:
            await poke.send("没有你账号咋发成绩嗷")
            return
        elif success == 403:
            await poke.send("你不让别人查我咋发a")
            return
        elif success == 500:
            print("服务器出错了")
            return
        data = t_list
        print(data[1])
        if len(data) == 0:
            await poke.send("暂时没有成绩")
            return
        index = random.randint(0, len(data) - 1)  # 获取随机成绩索引
        chart = data[index]
        # print(str(event.get_nickname).split('nickname=')[1].split('\'')[1])
        # print(event.nickname)
        # print(event.get_event_description)
        # nickname = str(event.get_nickname).split('nickname=')[1].split('\'')[1]
        # print(chart)
        msg = song_txt(chart, nickname)
        await poke.send(msg)


count_poke = on_command("统计戳一戳")


@count_poke.handle()
async def _(bot: Bot, event: Event, state: T_State):
    arg = str(event.get_message()).strip()
    nickname = "test"
    # if arg == "":
    #     # group_id = event.group_id
    #     group_id = event.group_id
    # else:
    #     group_id = arg
    msg = "你群戳一戳统计如下：\n"
    with open('src/plugins/poke.json', 'r', encoding='utf-8') as f:
        item = json.load(f)
        pokelist = []
        for i in range(len(item)):
            id = item[i]['id']
            nickname = item[i]['nickname']
            gid = item[i]['gid']
            count = int(item[i]['count'])
            # if str(id) == str(event.sender_id):
            pokelist.append({'id': id, 'nickname': nickname, 'gid': gid, 'count': count})
    pokelist.sort(key=lambda i: int(i['count']), reverse=True)
    times = 0
    for j in pokelist:
        # print(event.group_id)
        if str(event.group_id) != str(j['gid']):
            continue
        msg += f'''昵称：{j['nickname']} 一共戳了{j['count']}次'''
        times = times + 1
        if times == 3:
            break
        msg += "\n"
    if msg == "你群戳一戳统计如下：\n":
        msg = "你群没人戳过我嗷"
    await count_poke.send(msg)
# test = on_command("testpoke")
#
#
# @test.handle()
# async def _(bot: Bot, event: Event, state: T_State):
#     # 随机发一张成绩图
#     qq = {'qq': str(event.get_user_id())}
#     img, t_list, success = await generate(qq)
#     data = t_list.data
#     index = random.randint(0, len(data) - 1)  # 获取随机成绩索引
#     chart = data[index]
#     # print(str(event.get_nickname).split('nickname='))
#     # print(str(event.get_nickname).split('nickname=')[1].split('\'')[1])
#     # print(event.nickname)
#     # nickname = event.sender.nickname
#     # print(chart)
#     msg = song_txt(chart)
#     await test.send(msg)
