import redis
import json


class RedisQueue(object):
    """封装redis，支持list和str型"""

    def __init__(self, name):
        # redis的默认参数为：host='localhost', port=6379, db=0， 其中db为定义redis database的数量
        self.pool = redis.ConnectionPool(host='192.168.2.229', port=8092)
        self.__db = redis.Redis(connection_pool=self.pool)
        self.key = '%s' % name

    def qsize(self):
        return self.__db.llen(self.key)  # 返回队列里面list内元素的数量

    def put(self, item):
        self.__db.rpush(self.key, item)  # 添加新元素到list队列最右方

    def get_wait(self, timeout=None):
        # 返回队列第一个元素，如果为空则等待至有元素被加入队列（超时时间阈值为timeout，如果为None则一直等待）
        item = self.__db.blpop(self.key, timeout=timeout)
        # if item:
        #     item = item[1]  # 返回值为一个tuple
        return item

    def get_nowait(self):
        # 直接返回队列第一个元素，如果队列为空返回的是None
        item = self.__db.lpop(self.key)
        return item

    def set(self, value):  # 添加新元素到字符串队列
        return self.__db.set(self.key, value)

    def get_str_nowait(self):  # 返回字符串队列中数据
        return self.__db.get(self.key)


if __name__=="__main__":
    tlist=[x for x in 'abcdadsasfasfas']
    data={"Name":"HaoHang"}
    R=RedisQueue("mydict")
    R.set(tlist)
