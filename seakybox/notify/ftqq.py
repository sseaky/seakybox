#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seaky
# @Date:   2022/11/3 15:33

import requests


def send(key, title, desp=None, short=None, channel=9):
    '''
    title: 消息标题，必填。最大长度为 32 。
    desp: 消息内容，选填。支持 Markdown语法 ，最大长度为 32KB ,消息卡片截取前 30 显示。
    short: 消息卡片内容，选填。最大长度64。如果不指定，将自动从desp中截取生成。
    channel: 动态指定本次推送使用的消息通道，选填。如不指定，则使用网站上的消息通道页面设置的通道。支持最多两个通道，多个通道值用竖线|隔开。比如，同时发送服务号和企业微信应用消息通道，则使用 9|66 。通道对应的值如下：
    方糖服务号=9
    企业微信应用消息=66
    Bark iOS=8
    企业微信群机器人=1
    钉钉群机器人=2
    飞书群机器人=3
    测试号=0
    自定义=88
    PushDeer=18
    官方Android版·β=98
    '''
    url = 'https://sctapi.ftqq.com/{}.send'.format(key)
    json = {
        'title': title,
        'desp': desp,
        'short': short,
        'channel': channel
    }
    json1 = {k: v for k, v in json.items() if v is not None}
    resp = requests.post(url=url, json=json1)

    # 查询
    # d = resp.json()
    # url1 = 'https://sctapi.ftqq.com/push?id={pushid}&readkey={readkey}'.format(**d['data'])

    return resp
