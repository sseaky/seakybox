#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seaky
# @Date:   2021/4/2 16:46


def confirm(message='Are you sure?', choices='[y/n]', choice_true='y', message_false='Choice Fail!',
            strict_no=False, can_blank=True, skip=False):
    '''

    :param message: 提示消息
    :param choices: 提示选择
    :param choice_true: True的选择
    :param message_false: 确认失败的提示
    :param strict_no:
    :param can_blank:
    :param skip:
    :return:
    '''
    prompt = '{} {} '.format(message, choices)
    if skip:
        print(prompt)
        return True
    c = input(prompt).strip()
    if len(c) == 0 and not can_blank:
        return confirm(message=message, choices=choices, message_false=message_false, choice_true=choice_true,
                       strict_no=strict_no, can_blank=can_blank)
    if c.lower() == choice_true:
        return True
    else:
        if message_false:
            print(message_false)
        return False
