#!/usr/bin/env python
# -*- coding utf-8 -*-

# ftp客户端主程序

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import socket
import json
import hashlib
import copy


class Clinet:

    def __init__(self, sys_argv):
        self.USER_HOME = '%s/var/users' % BASE_DIR
        self.args = sys_argv
        self.argv_parse()
        self.response_code = {
            '200': 'pass user authentication',
            '201': 'wrong username or password',
            '300': 'ready to get file from server',
            '301': 'ready to send to server',
            '302': 'file does not exist on ftp server',
            '303': 'storage is full',
            '601': 'changed directory',
        }
        self.handle()

    def handle(self):
        self.connect(self.ftp_host, self.ftp_port)
        if self.auth():
            self.interactive()

    def argv_parse(self):
        """
        参数解析函数,取出参数中的IP地址和端口
        :return:
        """
        if len(self.args) < 5:   # args[0] 是程序自身
            self.help_msg()
            sys.exit()
        else:
            mandatory_fields = ['-p', '-s']
            for i in mandatory_fields:
                if i not in self.args:
                    self.help_msg()
                    sys.exit('')
            try:
                self.ftp_host = self.args[self.args.index['-s'] + 1]
                self.ftp_port = int(self.args[self.args.index['-p'] + 1])
            except (IndexError, ValueError):
                self.help_msg()
                sys.exit()

    def connect(self, host, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
        except socket.error as e:
            sys.exit('Failed to connect server: %s' % e)


    def help_msg(self):
        msg = """
        wrong input...
        format： python ftp.py -s ftp_server_ip -p ftp_server_port
        """
        print(msg)

    def instruction_msg(self):
        msg = """
            get remote ftp_file
            put local remote
            ls
            cd  path
        """
        print(msg)

    def interactive(self):
        pass

    def auth(self):
        retry_count = 0
        while retry_count < 3:
            username = input('pls enter your username: ')
            if len(username) == 0:
                continue
            password = input('pls enter your password: ')
            if len(password) == 0:
                continue
            md5 = hashlib.md5()
            md5.update(password.encode())
            auth_str = 'user_auth|%s' % (json.dumps({'username': username, 'password': md5.hexdigest()}))
            self.sock.send(auth_str.encode())
            server_response = self.sock.recv(1024).decode()
