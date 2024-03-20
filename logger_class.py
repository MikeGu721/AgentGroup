import json
from datetime import datetime
import os.path
from config import *

class Logger:
    def __init__(self, log_dir, user_name='gzh', max_log_number_in_each_file=10000):
        '''
        初始化日志类
        Input:
            log_dir: str, 日志存放地址
            user_name: str, 用户名
            max_log_number_in_each_file: 每个文件存多少条日志
        Output:
            None
        '''
        self.log_count = 0
        self.log_dir = log_dir
        self.gpt_log_dir = os.path.join(log_dir, 'gpt_logs')
        self.glm_log_dir = os.path.join(log_dir, 'glm_logs')
        self.hunyuan_log_dir = os.path.join(log_dir, 'hunyuan_logs')
        for dirr in [self.gpt_log_dir, self.glm_log_dir,self.hunyuan_log_dir]:
            if not os.path.exists(dirr):
                os.makedirs(dirr)
        self.user_name = user_name
        if not os.path.exists(log_dir): os.makedirs(log_dir)
        self.max_log_number_in_each_file = max_log_number_in_each_file
        self.log_index = max_log_number_in_each_file + 10
        self.check_log_index()
    def read_save_file(self, save_file,to_new_file:bool):
        '''
        读取已有的log_file，并判断是否要写入新的文件
        '''
        if to_new_file:
            if not os.path.exists(save_file):
                open(save_file, 'w',encoding='utf-8')
            self.log_count = len(open(save_file,encoding='utf-8').readlines())
            self.log_fw = open(save_file,'a',encoding='utf-8')
        else:
            if not os.path.exists(save_file):
                self.gprint('### Not Find Log File: %s'%(str(save_file)))
            else:
                self.log_count = len(open(save_file,encoding='utf-8').readlines())
                self.log_fw.write(open(save_file, encoding='utf-8').read())

    def get_uid(self, log_dir)->str:
        '''
        生成日志地址
        '''
        return str(datetime.now()).replace(' ','').replace('-','').replace(':','')

    def gprint(self, *args, **kwargs)->None:
        '''
        打印的同时，保存打印内容
        '''
        json_data = {"id":self.log_count,"time": str(datetime.now()), 'user':self.user_name, 'args': ' '.join([str(arg) for arg in args]), 'kwargs':json.dumps(kwargs, ensure_ascii=False)}
        self.log_count += 1
        if debug:
            print(json_data)
        self.log_fw.write(json.dumps(json_data, ensure_ascii=False)+'\n')
        self.log_index += 1
        self.check_log_index()

    def check_log_index(self)->None:
        '''
        日志太多时，将日志分开保存
        '''
        if self.log_index >= self.max_log_number_in_each_file:
            self.log_index = 0
            uid = self.get_uid(self.log_dir)
            self.log_file = os.path.join(self.log_dir, uid + '.json')
            if not self.log_file:
                self.log_fw = open(self.log_file, 'w', encoding='utf-8')
            else:
                self.log_fw = open(self.log_file, 'a', encoding='utf-8')


class Logger_v2:
    @classmethod
    async def create(cls, log_dir, sid):
        self = cls()
        self.sid = sid
        self.log_count = 0
        self.log_dir = log_dir
        if not os.path.exists(log_dir): os.makedirs(log_dir)
        self.log_file = os.path.join(self.log_dir, f"{sid}.json")
        self.log_fw = open(self.log_file, 'a', encoding='utf-8')
        print("current sid", sid)
        return self

    def gprint(self, *args, **kwargs)->None:
        json_data = {"sid": self.sid,
                     "id": self.log_count,
                     "time": str(datetime.now()),
                     "args": ' '.join([str(arg) for arg in args]), 
                     "kwargs": json.dumps(kwargs, ensure_ascii=False)}
        self.log_count += 1
        if debug:
            print(json_data)
        self.log_fw.write(json.dumps(json_data, ensure_ascii=False)+'\n')
        self.log_fw.flush()

    def close(self):
        self.log_fw.close()


if __name__ == '__main__':
    print(str(datetime.now()).replace(' ','').replace('-','').replace(':',''))
