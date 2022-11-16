#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seaky
# @Date:   2022/6/26 9:48

from ..func.parser import ArgParseClass
from ..func.base import MyClass
from ..func.log import make_logger
from ..data.redis_func import RedisC
import socket
import time
import traceback
import random
from base64 import b64encode


class TokenArgClass(ArgParseClass):
    def __init__(self, group='Token'):
        super().__init__(group=group)
        self.add_base()

    def add_mark(self, group='Mark'):
        self.add('--work_id', type=str, default=1, help='work id', group=group)
        self.add('--tag', default=socket.gethostname(), type=str, group=group)
        self.add('--program', type=str, default='Token', help='program name', group=group)
        self.add("--start", default=0, type=int, group=group)
        self.add('--offset', default=10000, type=int, group=group)
        self.add('--end', default=10000, type=int, group=group)

    def add_control(self, group='Control'):
        self.add('--test', action='store_true', help='执行test', group=group)
        self.add('--redis_save', action='store_true', help='redis_save', group=group)
        self.add('--include_running', action='store_true', help='执行running', group=group)
        self.add('--round', default=1, type=int, help='执行轮数', group=group)
        self.add('--repeat', action='store_true', help='忽略round，始终重复', group=group)

    def add_selenium(self, group='Selenium'):
        self.add('--selenium_mode', default='new', help='new/remote/profile', group=group)
        self.add('--timeout', default=10, help='Selenium超时时间', group=group)


class RunWithRedis(MyClass):
    def __init__(self, RedisConfig, redis_save=False,
                 program='RunWithRedis', tag=socket.gethostname(), work_id='test', log=None,
                 turn=0, repeat=False,
                 debug=False, verbose=False, *args, **kwargs):
        '''
        :param RedisConfig:
        :param redis_save: 保存redis状态
        :param program:     '{}_{}_{}'.format(self.program, wallet_id, wallet_public)
        :param tag:     用于标记日志
        :param work_id: 用于标记日志
        :param log:     自定义log
        :param turn:    第几轮
        :param repeat:  忽略redis中的turn, 重复运行
        :param debug:
        :param verbose:
        :param args:
        :param kwargs:
        '''
        if not log:
            log = make_logger(filename='{}_{}_{}'.format(program, tag, work_id),
                              log_dir='log\\{}'.format(program),
                              write=True, multi_process=False, debug=debug)
        super().__init__(log=log, debug=debug, verbose=verbose, *args, **kwargs)
        log.info('开始任务 {}, round {}, repeat {}'.format(program, turn, repeat))
        self.redis_save = redis_save
        self.program = program
        self.round = turn
        self.repeat = repeat
        self.verbose = verbose
        # self.redis = redis.StrictRedis(*redis_server.split(':'), db=0)
        self.redis = RedisC(log=log, **RedisConfig)
        if not repeat:
            self.cache[self.program] = self.redis.get_prefix(
                prefix='{}_'.format(self.program), ret_dict=True, key_with_prefix=True, unjson=True)
        else:
            self.cache[self.program] = {}
        # self.get_wallets()

    def get_wallets(self, sns=False):
        self.get_erc20()
        if sns:
            sns_dict = self.redis.get_prefix(prefix='sns_', key_with_prefix=False, ret_dict=True, unjson=True)
            sns_list = sorted([v for k, v in sns_dict.items()], key=lambda v: v['id'])
            self.log.info('load {} sns account'.format(len(sns_list)))
            sns_col = ['name', 'gmail', 'twitter', 'handle', 'discord']
            for i, x in enumerate(self.cache['wallets']):
                if i < len(sns_list):
                    x.update({k: sns_list[i][k] for k in sns_col})
                else:
                    start = random.randint(4, 8)
                    name = b64encode(x['public'].encode('utf8')).decode('utf8').lower()[start:start + random.randint(6, 10)]
                    x.update({
                        'name': name,
                        'gmail': '{}@gmail.com'.format(name),
                        'twitter': name,
                        'handle': '@{}'.format(name),
                        'discord': '{}@{}'.format(name, random.randint(1001, 9999)),
                    })



    def get_erc20(self):
        erc20_dict = self.redis.get_prefix(prefix='erc20_', key_with_prefix=False, ret_dict=True, unjson=True)
        self.cache['wallets'] = sorted([v for k, v in erc20_dict.items()], key=lambda v: v['id'])
        self.log.info('load {} erc20 wallets'.format(len(self.cache['wallets'])))
        return True


    def create_redis_key(self, wallet_id, wallet_public):
        return '{}_{}_{}'.format(self.program, wallet_id, wallet_public)

    def load_redis_value(self, wallet_id, wallet_public):
        rk = self.create_redis_key(wallet_id, wallet_public)
        d = None if self.repeat else self.redis.get(rk)
        if d is None:
            d = {'id': wallet_id, 'public': wallet_public}
            d.update({'running': 0, 'failed': 0, 'exp': '', 'last_run': time.time(), 'round': []})
        return d

    def calc_end(self, start, end, offset):
        return min(end, start + offset, len(self.cache['wallets']))

    def run(self, start=0, end=100000, offset=100000, include_running=False, task=None, **kwargs):
        def is_running(record, interval=600):
            if include_running:
                return False
            if record['running'] == 1:
                if time.time() - record.get('last_run', 0) < interval:
                    return True
            return False

        end = self.calc_end(start=start, end=end, offset=offset)
        self.log.info('项目 {} Round {}, 执行 [{}, {})'.format(self.program, self.round, start, end))
        flag_lookup_history = True
        for i in range(start, end, 1):
            wallet = self.cache['wallets'][i]
            wallet_id = wallet['id']
            wallet_public = wallet['public']
            rk = self.create_redis_key(wallet_id, wallet_public)
            # 加快首次查询历史
            if flag_lookup_history:
                if rk in self.cache[self.program] and \
                        (self.round in self.cache[self.program][rk]['round'] or
                         is_running(self.cache[self.program][rk])):
                    continue
                else:
                    flag_lookup_history = False
            d = self.load_redis_value(wallet_id, wallet_public)
            if self.round in d['round'] or is_running(d):
                continue
            d['running'] = 1
            d['last_run'] = time.time()
            if self.redis_save:
                self.redis.set(rk, d)
            try:
                self.log.debug('开始执行第 {} 个任务 {}'.format(i, rk))
                _task = task if task else self.task
                result = self.task(i)
                if result:
                    self.log.debug('执行第 {} 个任务成功'.format(i))
                    d['round'].append(self.round)
            except Exception as e:
                self.log.error(traceback.format_exc())
                self.log.error('执行第 {} 个任务失败'.format(i))
                d.update({'failed': d['failed'] + 1, 'exp': traceback.format_exc()})
            finally:
                d['running'] = 0
                if self.redis_save:
                    self.redis.set(rk, d)

    def task(self, i=-1):
        wallet = self.cache['wallets'][i]
        return True

    def tally(self):
        done = 0
        keys = self.redis.keys('{}-*'.format(self.program))
        results = self.redis.pipe_get(keys=keys, ret_dict=True, unjson=True)
        for k, v in results.items():
            if self.round in v['round']:
                done += 1
        print('total {}, done {}'.format(len(keys), done))
