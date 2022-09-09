# mai bot 使用指南

此 README 提供了最低程度的 mai bot 教程与支持。

## Step 1. 安装 Python

请自行前往 https://www.python.org/ 下载 Python 3 版本（> 3.7）并将其添加到环境变量（在安装过程中勾选 Add to system PATH）。在 Linux 系统上，可能需要其他方法安装 Python 3，请自行查找。

## Step 2. 运行项目

建议使用 git 对此项目进行版本管理。您也可以直接在本界面下载代码的压缩包进行运行。

在运行代码之前，您需要从[此链接](https://www.diving-fish.com/maibot/static.zip)下载资源文件并解压到`src`文件夹中。在此之后，输入
```
pip install -r requirements.txt
```
安装依赖，之后运行
```
python bot.py
```
运行项目。如果输出如下所示的内容，代表运行成功：
```
08-02 11:26:48 [INFO] nonebot | NoneBot is initializing...
08-02 11:26:48 [INFO] nonebot | Current Env: prod
08-02 11:26:49 [INFO] nonebot | Succeeded to import "maimaidx"
08-02 11:26:49 [INFO] nonebot | Succeeded to import "public"
08-02 11:26:49 [INFO] nonebot | Running NoneBot...
08-02 11:26:49 [INFO] uvicorn | Started server process [5268]
08-02 11:26:49 [INFO] uvicorn | Waiting for application startup.
08-02 11:26:49 [INFO] uvicorn | Application startup complete.
08-02 11:26:49 [INFO] uvicorn | Uvicorn running on http://127.0.0.1:10219 (Press CTRL+C to quit)
```

## Step 3. 连接 CQ-HTTP

前往 https://github.com/Mrs4s/go-cqhttp > Releases，下载适合自己操作系统的可执行文件。
go-cqhttp 在初次启动时会询问代理方式，选择反向 websocket 代理即可。
之后设置反向 ws 地址、上报方式：
```yml
message:
  post-format: array
  
servers:
  - ws-reverse:
      universal: ws://127.0.0.1:10219/cqhttp/ws
```
然后设置您的 QQ 号和密码。您也可以不设置密码，选择扫码登陆的方式。

登陆成功后，后台应该会发送一条类似的信息：
```
08-02 11:50:51 [INFO] nonebot | WebSocket Connection from CQHTTP Bot 114514 Accepted!
```
至此，您可以和对应的 QQ 号聊天并使用 mai bot 的所有功能了。

## FAQ

不是 Windows 系统该怎么办？
> 请自行查阅其他系统上的 Python 安装方式。cqhttp提供了其他系统的可执行文件，您也可以自行配置 golang module 环境进行编译。

配置 nonebot 或 cq-http 过程中出错？
> 请查阅 https://github.com/nonebot/nonebot2 以及 https://github.com/Mrs4s/go-cqhttp 中的文档。

部分消息发不出来？
> 被风控了。解决方式：换号或者让这个号保持登陆状态和一定的聊天频率，持续一段时间。

## 说明

本 bot 提供了如下功能：

命令 | 功能
------ | ------
qvb40|查看qq号绑定账号b40(不可账号查询)
qvb50|查看qq号绑定账号b40(不可账号查询)，有bug，仅供参考
<定级>分数列表|[页数]查看qq绑定账号该定级下的分数从高到低排序，每页最多显示25条，每3分钟只能查询一次
 ->|例：14分数列表 2
今日舞萌|查看今天的舞萌运势
XXXmaimaiXXX什么|随机一首歌
 ->|例：今天maimai什么
随个[dx/标准][绿黄红紫白]<难度或定数>|随机一首指定条件的乐曲，新增支持具体定数语句
 ->|例：随个紫14
艺术家查歌<曲师名称>|查询符合曲师条件的乐曲
 ->|例：艺术家查歌uk
谱师查歌<谱师名称>|查询符合谱师条件的乐曲（仅支持红谱以上）
 ->|例：谱师查歌100号
bpm查歌<歌曲bpm/歌曲bpm下限>|[歌曲bpm上限] 查询符合bpm条件的乐曲，上限120条
 ->|例：bpm查歌100 200
查歌<乐曲标题的一部分>|查询符合条件的乐曲
 ->|例：查歌pan
[绿黄红紫白]id<歌曲编号>|查询乐曲信息或谱面信息
 ->|例：紫id834
<歌曲别名>是什么歌|查询乐曲别名对应的乐曲
 ->|例：我是什么歌
定数查歌 <定数>|查询定数对应的乐曲
 ->|例：定数查歌 14.2
定数查歌 <定数下限> <定数上限> |查询定数上下限内对应的乐曲
 ->|例：定数查歌 14.1 14.6
分数线|<难度+歌曲id> <分数线> 详情请输入“分数线 帮助”查看
随机成绩|查询随机一条成绩，10分钟只能查询一次
查询成绩|[绿黄红紫白]id<歌曲编号>  查询乐曲成绩，10分钟只能查询一次
 ->|例：查询成绩 白id834

## License

MIT

您可以自由使用本项目的代码用于商业或非商业的用途，但必须附带 MIT 授权协议。
