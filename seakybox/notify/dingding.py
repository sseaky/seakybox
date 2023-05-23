#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seaky
# @Date:   2022/12/4 14:45

import time
import hmac
import hashlib
import base64
import urllib.parse
import requests


class Dingding:
    def __init__(self, token, secret, api='https://oapi.dingtalk.com/robot/send'):
        self.token = token
        self.secret = secret
        self.api = api

    def sign(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        params = {
            'access_token': self.token,
            'timestamp': timestamp,
            'sign': sign
        }
        print(params)
        return params

    def text(self, content, atMobiles=None, atUserIds=None, isAtAll=False):
        data = {
            'msgtype': 'text',
            'text': {'content': content}
        }
        if atMobiles or atUserIds or isAtAll:
            data['at'] = {}
            if atMobiles:
                data['at']['atMobiles'] = atMobiles.split(',')
            if atUserIds:
                data['at']['atUserIds'] = atUserIds.split(',')
            if isAtAll:
                data['at']['isAtAll'] = True
        params = self.sign()
        resp = requests.post(self.api, params=params, json=data)
        return resp


if __name__ == '__main__':
    DINGDING_TOKEN = ''
    DINGDING_SECRET = ''
    dd = Dingding(token=DINGDING_TOKEN, secret=DINGDING_SECRET)
    dd.text(content='test', isAtAll=True)
