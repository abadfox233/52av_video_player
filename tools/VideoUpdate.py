# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: VideoUpdate.py
@time: 2019/3/1 20:30
@describe:  更新进程
"""
from scrapy.cmdline import execute
import os
import sys


if __name__ == '__main__':
    spider_path = r'E:\mycs\python\scrapyproject\project_av\project_av'
    os.chdir(spider_path)
    sys.path.append(spider_path)
    execute(["scrapy", "crawl", "www_52av_tv"])