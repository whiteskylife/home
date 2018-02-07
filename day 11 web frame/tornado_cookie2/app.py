#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web

# 把session封装为一个类，开发时无需关注生成字符串、设置cookie等细节，直接设置session的key和value即可，注意：代码中cookie的key是写死的

container = {}
# container = {
#     '第一个人的随机字符串': {},
#     '第二个人的随机字符串': {'k1': 111, 'parents': '你'},
# }


class Session:
    def __init__(self, handler):
        """
        :param handler: 传进来的IndexHandler对象，具有了set_cookie方法
        """
        self.handler = handler
        self.random_str = None

    def __generate_random_str(self):
        # 生成加密串,方法只能在类里面调用
        import hashlib
        import time
        obj = hashlib.md5()
        obj.update(bytes(str(time.time()), encoding='utf-8'))
        random_str = obj.hexdigest()  # 根据时间生成随机字符串
        return random_str

    def set_value(self, key, value):
        """
        :param key: 定义session用户信息的key
        :param value: 定义session用户信息的value
        :return:
        """
        # 在container中加入随机字符串
        # 定义session属于各自用户数据
        # 在客户端中写入随机字符串
        # 创建随机字符串之前，应该判断请求的用户是否第一次请求、第一次登录，是否已有随机字符串
        if not self.random_str:
            random_str = self.handler.get_cookie("___kakaka___")
            if not random_str:
                random_str = self.__generate_random_str()
                # self.handler.set_cookie("___kakaka___", random_str)  # 不存在随机字符串时，认为不存在cookie，此处需设置cookie；
                # 如存在random_str，则认为存在cookie，if条件下面无需再次设置cookie。cookie的key定义要统一记准，值为random_str
                container[random_str] = {}  # 创建专属于自己的session数据空间为一个空字典
            else:
                # 客户端有随机字符串
                if random_str in container.keys():
                    pass
                else:                           # 此种情况发生在服务器端重启时，浏览器端有random_str,服务器端没有，则重新生成random_str
                    random_str = self.__generate_random_str()
                    container[random_str] = {}
            self.random_str = random_str
        container[self.random_str][key] = value
        self.handler.set_cookie("___kakaka___", self.random_str)
        # 生产开发中，如果没有定义cookie超时时间，此处不需设置cookie，如果设置了cookie超时时间，到了时间之前再次访问时，应该重新写一次cookie，相当于延长一下超时时间，否则原来的cookie到了超时时间则过期

    def get_value(self, key):
        """
        :param key:传入session用户信息的key
        :return: 返回session用户信息的value
        """
        # 获取客户端的随机字符串
        # 从container中获取专属于我的数据
        random_str = self.handler.get_cookie("___kakaka___", None)
        if not random_str:      # 没有随机字符串表示没有登录
            return None
        # 客户端有random_str：
        user_info_dict = container.get(random_str, None)
        if not user_info_dict:          # 服务器端没有random_str对应的值（服务器端可能重启过），返回空
            return None
        value = user_info_dict.get(key, None)
        return value


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        if self.get_argument('u', None) in ['whisky', 'alex']:     # 设置u值默认为None，否则访问不带u参数会报400错误
            s = Session(self)
            s.set_value('is_login', True)   # 初始化创建session的key和value
            s.set_value('name', self.get_argument('u', None))
            print(container)
        else:
            self.write('请用正确的用户名登录')


class ManagerHandler(tornado.web.RequestHandler):
    def get(self):
        s = Session(self)
        val = s.get_value('is_login')
        if val:
            self.write(s.get_value('name'))
        else:
            self.write('失败')

settings = {
    'template_path': 'views',
    'static_path': 'statics'
}

application = tornado.web.Application([
    (r"/index", IndexHandler),
    (r"/manager", ManagerHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()


# 登录测试：http://127.0.0.1:8000/index?u=whisky


