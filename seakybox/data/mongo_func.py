#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Seaky
# @Date:   2022/10/28 15:15


import pymongo
import traceback
import urllib.parse
from ..func.time import datetime_to_string


class MongoDBUtil:
    """
    MongoDB工具类
    """

    def __init__(self, ip, db_name, port='27017', username=None, password=None):
        """构造函数"""
        if username:
            self.client = pymongo.MongoClient(
                'mongodb://{}:{}@{}:{}'.format(username, urllib.parse.quote(password), ip, port))
        else:
            self.client = pymongo.MongoClient("mongodb://" + ip + ":" + port)
        self.database = self.client[db_name]

    def __del__(self):
        """析构函数"""
        # print("__del__")
        self.client.close()

    def close(self):
        self.client.close()

    def create_database(self, db_name):
        """创建数据库"""
        return self.client.get_database(db_name)

    def drop_database(self, db_name):
        """删除数据库"""
        return self.client.drop_database(db_name)

    def select_database(self, db_name):
        """使用数据库"""
        self.database = self.client[db_name]
        return self.database

    def get_database(self, db_name):
        """使用数据库"""
        # return self.client[db_name]
        return self.client.get_database(db_name)

    def list_database_names(self):
        """获取所有数据库列表"""
        return self.client.list_database_names()

    def create_collection(self, collect_name):
        """创建集合"""
        collect = self.database.get_collection(collect_name)
        if (collect is not None):
            print("collection %s already exists" % collect_name)
            return collect
        return self.database.create_collection(collect_name)

    def drop_collection(self, collect_name):
        """获取所有集合名称"""
        return self.database.drop_collection(collect_name)

    def get_collection(self, collect_name):
        """获取集合"""
        return self.database.get_collection(collect_name)

    def list_collection_names(self):
        """获取所有集合名称"""
        return self.database.list_collection_names()

    def insert(self, collect_name, documents):
        """插入单条或多条数据"""
        return self.database.get_collection(collect_name).insert(documents)

    def insert_one(self, collect_name, document):
        """插入一条数据"""
        return self.database.get_collection(collect_name).insert_one(document)

    def insert_many(self, collect_name, documents):
        """插入多条数据"""
        return self.database.get_collection(collect_name).insert_many(documents)

    def delete_one(self, collect_name, filter, collation=None, hint=None, session=None):
        """删除一条记录"""
        return self.database.get_collection(collect_name).delete_one(filter, collation, hint, session)

    def delete_many(self, collect_name, filter, collation=None, hint=None, session=None):
        """删除所有记录"""
        return self.database.get_collection(collect_name).delete_many(filter, collation, hint, session)

    def find_one_and_delete(self, collect_name, filter, projection=None, sort=None, hint=None, session=None, **kwargs):
        """查询并删除一条记录"""
        return self.database.get_collection(collect_name).find_one_and_delete(filter, projection, sort, hint, session,
                                                                              **kwargs)

    def count_documents(self, collect_name, filter, session=None, **kwargs):
        """查询文档数目"""
        return self.database.get_collection(collect_name).count_documents(filter, session, **kwargs)

    def find_one(self, collect_name, filter=None, *args, **kwargs):
        """查询一条记录"""
        return self.database.get_collection(collect_name).find_one(filter, *args, **kwargs)

    def find(self, collect_name, *args, **kwargs):
        """查询所有记录"""
        return self.database.get_collection(collect_name).find(*args, **kwargs)

    def update(self, collect_name, spec, document, upsert=False, manipulate=False,
               multi=False, check_keys=True, **kwargs):
        """更新所有记录"""
        return self.database.get_collection(collect_name).update(spec, document,
                                                                 upsert, manipulate, multi, check_keys, **kwargs)

    def update_one(self, collect_name, filter, update, upsert=False, bypass_document_validation=False,
                   collation=None, array_filters=None, hint=None, session=None):
        """更新一条记录"""
        return self.database.get_collection(collect_name).update_one(filter, update,
                                                                     upsert, bypass_document_validation, collation,
                                                                     array_filters, hint, session)

    def update_many(self, collect_name, filter, update, upsert=False, array_filters=None,
                    bypass_document_validation=False, collation=None, hint=None, session=None):
        """更新所有记录"""
        return self.database.get_collection(collect_name).update_many(filter, update,
                                                                      upsert, array_filters, bypass_document_validation,
                                                                      collation, hint, session)

    def find_one_and_update(self, collect_name, filter, update, projection=None, sort=None, upsert=False,
                            return_document=False, array_filters=None, hint=None, session=None, **kwargs):
        """查询并更新一条记录"""
        return self.database.get_collection(collect_name).find_one_and_update(filter, update, projection,
                                                                              sort, upsert, return_document,
                                                                              array_filters, hint, session, **kwargs)

    # custom
    def find_all(self, collect_name, dict_key=None, *args, **kwargs):
        obj = self.find(collect_name=collect_name, *args, **kwargs)
        if dict_key:
            dic = {x[dict_key]: x for x in obj}
            print('find {} documents'.format(len(dic)))
            return dic
        else:
            lst = [x for x in obj]
            print('find {} documents'.format(len(lst)))
            return lst

    def check_and_lock_it(self, process, collect_name, filter=None, address=None, skip_lock=False, expect=1,
                          *args, **kwargs):
        if not filter:
            filter = {'address': address}
        item = self.find_one(collect_name=collect_name, filter=filter, *args, **kwargs)
        lock_col = '{}_lock'.format(process)
        if item.get(process) == expect:
            if item.get(lock_col) == 1:
                update = {'$set': {lock_col: 0}}
                self.update_one(collect_name=collect_name, filter=filter, update=update)
            return False
        if item.get(lock_col) == 1:
            return skip_lock or False
        else:
            update = {'$set': {lock_col: 1}}
            self.update_one(collect_name=collect_name, filter=filter, update=update)
            return True

    def unlock_it(self, process, collect_name, filter=None, address=None, result=None, exp=None, *args, **kwargs):
        if result is True:
            result = 1
        elif result is False:
            result = 0
        if not filter:
            filter = {'address': address}
        item = self.find_one(collect_name=collect_name, filter=filter, *args, **kwargs)
        lock_col = '{}_lock'.format(process)
        d = {}
        if item.get(lock_col) == 1:
            d[lock_col] = 0
            if result is not None:
                d[process] = result
            d['{}_exp'.format(process)] = exp
        update = {'$set': d}
        self.update_one(collect_name=collect_name, filter=filter, update=update)
        return True

    def resort_id(self, collect_name, key='i'):
        lst = self.find_all(collect_name=collect_name)
        for i, x in enumerate(lst):
            j = i + 1
            if x.get(key) != j:
                print('fixing {} ...'.format(j))
                filter = {'_id': x['id']}
                update = {'$set': {key: j}}
                r = self.update_one(collect_name=collect_name, filter=filter, update=update)

    def run_with_lock(self, collect_name, filter, process, func, i=None, skip_lock=False, stop_when_fail=False):
        if self.check_and_lock_it(collect_name=collect_name, process=process, filter=filter, skip_lock=skip_lock):
            print('  {} {}{} {}'.format(datetime_to_string(), str(i) + ' ' if i else '', process, filter))
            exp = None
            result = None
            try:
                result = func[0](**func[1])
                print('    result: {}'.format(result))
            except Exception as e:
                exp = traceback.format_exc()
                print(exp)
                result = 0
            finally:
                self.unlock_it(collect_name=collect_name, process=process, filter=filter, result=result, exp=exp)
                if stop_when_fail and not result:
                    return -1
                return result

# class MongoC(MongoDBUtil):
#     def __init__(self, *args, **kwargs):
#         super(MongoC, self).__init__(*args, **kwargs)

# def update_by_key(self, collect_name, document, filter=None, check_uniq=False, load_all_first=False):
#     if check_uniq:
#         n = self.count_documents(collect_name=collect_name, filter=filter)
#         if n > 1:
#             raise 'result with filter {} applying on {} is more than {}'.format(filter, collect_name, 1)
#     documents = [x for x in self.find(collect_name=collect_name, filter=filter)]
#     self.database.test.update_one({'x': 1}, {'$inc': {'x': 3}})


if __name__ == "__main__":
    print("------------------start-------------------------")
    MONGO_CFG = {'ip': 'f.pyth0n.vip', 'port': '53187', 'username': 'admin',
                 'password': urllib.parse.quote('mongo1qaz@WSX')}
    mongoUtil = MongoDBUtil(db_name='xl01', **MONGO_CFG)
    """数据库操作"""
    # stat = mongoUtil.create_database(db_name="xl01")
    # stat = mongoUtil.drop_database(db_name="xl01")
    stat = mongoUtil.list_database_names()
    stat = mongoUtil.get_database(db_name="xl01")
    """集合操作"""
    stat = mongoUtil.create_collection(collect_name="xl_collect_01")
    # stat = mongoUtil.drop_collection(collect_name="xl_collect_01")
    stat = mongoUtil.get_collection(collect_name="xl_collect_01")
    stat = mongoUtil.list_collection_names()
    """文档操作：增加"""
    document = {"name": "hao123", "type": "搜索引擎", "url": "http://www.hao123.com/"}
    stat = mongoUtil.insert_one(collect_name="xl_collect_01", document=document)
    # documents = [{'x': i} for i in range(2)]
    documents = [{"name": "hao123", "type": "搜索引擎"} for i in range(2)]
    # stat = mongoUtil.insert(collect_name="xl_collect_01", documents=documents)
    stat = mongoUtil.insert_many(collect_name="xl_collect_01", documents=documents)
    """文档操作：查询"""
    stat = mongoUtil.find_one(collect_name="xl_collect_01")
    print(type(stat), stat)
    rows = mongoUtil.find(collect_name="xl_collect_01")
    # for row in rows:
    #     print(row)
    filter = {'name': 'hao123'}
    # filter = {'x': 1}
    count = mongoUtil.count_documents(collect_name="xl_collect_01", filter=filter)
    print(type(stat), count)
    """文档操作：删除"""
    stat = mongoUtil.delete_one(collect_name="xl_collect_01", filter=filter)
    stat = mongoUtil.find_one_and_delete(collect_name="xl_collect_01", filter=filter)
    # stat = mongoUtil.delete_many(collect_name="xl_collect_01", filter=filter)
    print(type(stat), stat)
    """文档操作：修改"""
    spec = {"url": "http://www.baidu.com/"}
    # spec = {"url": "http://www.hao123.com/"}
    # stat = mongoUtil.update(collect_name="xl_collect_01", spec=spec, document=document)
    # print(type(stat), stat)
    update = {"$set": spec}
    stat = mongoUtil.update_one(collect_name="xl_collect_01", filter=filter, update=update)
    print(type(stat), stat.modified_count, stat)
    stat = mongoUtil.update_many(collect_name="xl_collect_01", filter=filter, update=update)
    print(type(stat), stat.modified_count, stat)
    stat = mongoUtil.find_one_and_update(collect_name="xl_collect_01", filter=filter, update=update)
    print(type(stat), stat)
    print("-------------------end--------------------------")
