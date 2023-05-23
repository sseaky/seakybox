#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seaky
# @Date:   2022/5/26 23:38

import random
import re
from decimal import Decimal


def show_digit(value, dot=None):
    '''
    1.2e-4 -> '0.00012'
    dot: 保留小数位数，如果value < 1，保留有效位数
    '''
    if value == 0:
        return 0
    minus = True if str(value)[0] == '-' else False
    if minus:
        value = -value
    i = 0
    while value <= 1:
        i += 1
        value *= 10

    # 补充0
    if i == 0:
        value_s = str(value)
    else:
        s = str(value).replace('.', '')
        value_s = '0.'
        for j in range(1, i):
            if j:
                value_s += '0'
        value_s += s
        value_s = re.sub('0+$', '', value_s)

    if isinstance(dot, int):
        if re.search('^0\.', value_s):
            # 0.00012345 -> 0.000123
            s2 = re.search('(^0\.0*)', value_s).group(1)
            value_s = s2 + value_s.replace(s2, '')[:dot]
        elif '.' in value_s:
            # 1.00123 -> 1.001
            _ = value_s.split('.')
            value_s = '.'.join([_[0], _[1][:dot]])

    if minus:
        value_s = '-' + value_s
    return value_s


def random_value(value, ratio_min=1, ratio_max=2, dot_min=1, dot_max=3):
    '''
    随机ratio，随机位数
    '''
    if value == 0:
        return value
    value = float(value)
    minus = True if str(value)[0] == '-' else False
    if minus:
        value = -value
    dot = random.randint(dot_min, dot_max)
    i = 0
    while value <= 1:
        i += 1
        value *= 10
    i += dot
    value *= 10 ** dot
    value = random.randint(int(ratio_min * value), int(ratio_max * value))
    value = float(value) / 10 ** i
    if minus:
        value = -value
    return show_digit(value, dot=dot)


def extract_number_from_str(s):
    p1 = '([\d,]+\.\d+)'
    p2 = '([\d,]+)'
    m1 = re.search(p1, s)
    if m1:
        return float(m1.group(1).replace(',', ''))
    m2 = re.search(p2, s)
    if m2:
        return int(m2.group(1).replace(',', ''))


def comma_digit(s, tp=int):
    '''用逗号分割数字'''
    if isinstance(s, int):
        return '{,}'.format_map(s)
    if str_is_number(s, tp, exp=True):
        return '{:,}'.format(int(s))
    return s


def str_is_number(s, tp=None, exp=True):
    '''

    :param s:
    :param tp: 指定int/float，None两者都行
    :param exp: 扩展，如果s是int/float，也可以返回true
    :return:
    '''
    if not isinstance(s, str):
        if exp and isinstance(s, int) and tp in (None, int):
            return True
        if exp and isinstance(s, float) and tp in (None, float):
            return True
        return False
    if tp == int:
        return re.match('^\-{,1}\d+\.{0,0}\d+$', s)
    elif tp == float:
        return re.match('^\-{,1}\d+\.{1,1}\d+$', s)
    else:
        return re.match('^\-{,1}\d+\.{,1}\d+$', s)


def unit_number(s, base=1000):
    '''
    iptables中可以使用-x参数
    :param s:
    :param base:
    :return:
    '''
    l = ['k', 'm', 'g', 't']
    if s.isdigit():
        return s
    else:
        for i, c in enumerate(l):
            if s[-1].lower() == c:
                return str(int(s[:-1]) * base ** (i + 1))


def qround(n, digit=2, retf=False):
    '''
    比round更高的精度
    :param n:
    :param digit:
    :param retf:
    :return:
    '''
    r = Decimal(n).quantize(Decimal('0.{}'.format('0' * digit)))
    if retf:
        r = float(r)
    return r
