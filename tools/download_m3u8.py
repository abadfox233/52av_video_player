# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: download_m3u8.py
@time: 2019/2/4 15:31
@describe: 
"""
import re
from urllib.parse import urljoin
import os

import requests
import m3u8
import subprocess
from tools.VideoConfigParser import VideoConfigParserClass

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
}

# http 实例
# session = requests.Session()
# proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}
# session.proxies = proxies

base_dir = './video/'


def create_download_message(url, title, video_id):
    config = VideoConfigParserClass().get_m3u8_download_setting()
    dir_path = base_dir + str(video_id)
    url_path = base_dir + str(video_id)+'/url.txt'
    log_path = base_dir + str(video_id)+'/log.txt'
    if os.path.isfile(log_path):
        os.remove(log_path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    try:
        if config[0]:
            proxies = {'http': 'socks5://%s:%s' % (config[1], config[2]), 'https': 'socks5://%s:%s' % (config[1], config[2])}
            result = requests.get(url, proxies=proxies)
        else:
            result = requests.get(url)
        flag = True
        if result.status_code == 200:
            files = m3u8.loads(result.text).files
            with open(url_path, 'w') as url_file:
                for file in files:
                    if not judge_is_downloaded(file, dir_path):
                        url_file.write(urljoin(url, file) + '\n')
                        flag = False

            create_result = {
                'result': True,
                'file_length': len(files),
                'dir_path': os.path.abspath(dir_path),
                'url_path': os.path.abspath(url_path),
                'log_path': os.path.abspath(log_path),
                'finish': flag
            }
            return create_result
        else:
            return {"result": False, 'code': result.status_code}
    except Exception:
        return {"result": False}


def start_download(download_message):
    config = VideoConfigParserClass().get_aria2c_setting()
    if config[2]:
        cmd_str = 'aria2c -d {} -i {} -j {} -x {} -c true -l  {} --log-level=notice --all-proxy=http://%s:%s' \
                  % (config[3], config[4])
    else:
        cmd_str = 'aria2c -d {} -i {} -j {} -x {} -c true -l  {} --log-level=notice '
    cmd_str = cmd_str.format(download_message['dir_path'], download_message['url_path'], str(config[0]), str(config[1]),
                             download_message['log_path'],
                             )

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    dev_null = open(os.devnull, 'w')
    download_process = subprocess.Popen(cmd_str, stdin=dev_null, stdout=dev_null, stderr=dev_null, startupinfo=si)

    return download_process


def judge_is_downloaded(file_name, dir_path):
    if os.path.isfile('%s/%s' % (dir_path, file_name)):
        if os.path.isfile('%s/%s.aria2' % (dir_path, file_name)):
            return False
        else:
            return True
    else:
        return False


def join_temp_file(url, num, name, video_object_id):
    """
    合并文件
    :param url 下载地址
    :param num: 文件最大数
    :param name:  文件名
    :param video_object_id 数字签名
    :return:
    """
    pattern = re.compile('.*/(.*)\.m3u8')
    start_url = pattern.findall(url)[0]
    temp_file_list = ['./video/' + video_object_id + "/" + file for file in os.listdir('./video/' + video_object_id + "/" ) if re.match(start_url+'\d+\.ts', file)]
    video_path = './video/' + video_object_id + "/" + name + '.ts'
    result_file = open(video_path, 'wb')
    for i in range(num+1):
        file = './video/' + video_object_id + "/" + start_url+str(i) + '.ts'
        if file in temp_file_list and os.path.isfile(''+file):
            with open(file, 'rb') as f:
                while True:
                    block = f.read(10240)
                    if block:
                        result_file.write(block)
                    else:
                        break
    result_file.close()

    for i in range(num+1):
        file = './video/' + video_object_id + "/" + start_url+str(i) + '.ts'
        if file in temp_file_list and os.path.isfile(file):
            try:
                os.remove(file)
            except:
                pass
    video_path = os.path.abspath(video_path)
    return video_path


if __name__ == '__main__':
    pass
    # p = subprocess.Popen('aria2c -i url.txt -j 30 -x 16 -c true -l log.txt --log-level=notice', stdout=0, stderr=0)
    # time.sleep(5)
    #
    #
    #
    # p.terminate()
    # download_message = create_download_message('https://test.yocoolnet.com/files/mp4/l/V/0/lV0A9.m3u8',
    #                         '人妻鮑魚圖鑑',
    #                         3)
    # download_process = start_download(download_message)
    # while True:
    #     if download_process.poll() is None:
    #         time.sleep(5)
    #         print(type(download_process.poll()))
    #     else:
    #         break
    # # while download_process.returncode == None:
    # #     time.sleep(5)
    # #     print(download_process.returncode)
    # # print(download_process.returncode)
    # #     # download_process.terminate()