# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: video_api.py
@time: 2019/1/24 20:21
@describe: 
"""
import os

from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QSize, Qt
import MySQLdb
from tools.SQL import *
from tools.VideoConfigParser import VideoConfigParserClass
db_setting = VideoConfigParserClass().get_db_setting()
conn = MySQLdb.connect("localhost", db_setting[0], db_setting[1], db_setting[2], charset='utf8', use_unicode=True)


def search_video(search_word):
    """
    指定字符串查询影片
    :param search_word:
    :return:
    """
    cursor = conn.cursor()
    sql = SEARCH_SQL.format(search_word)
    cursor.execute(sql)
    movie_list = cursor.fetchall()
    cursor.close()
    return movie_list


def change_image_size(image_path, new_width, new_height):
    """
    改变图片比例
    :param scale: 图片比例
    :param image_path: 图片路径
    :return:
    """
    img = QImage(image_path)
    size = QSize(new_width, new_height)
    pix_image = QPixmap.fromImage(img.scaled(size, Qt.IgnoreAspectRatio))
    return pix_image


def get_download_video():
    """
    查询下载的影片
    :param search_word:
    :return:
    """
    cursor = conn.cursor()
    cursor.execute(GET_DOWNLOAD_MOVIE)
    movie_list = cursor.fetchall()
    cursor.close()
    return movie_list


def update_download_message(video_id, state):
    """
    更新下载信息
    :param video_id:
    :param state:
    :return:
    """
    cursor = conn.cursor()
    sql = UPDATE_DOWLOAD_MESSAGE.format(str(state), video_id)
    cursor.execute(sql)
    conn.commit()
    cursor.close()


def add_download_message(video_id, state=0):
    """
    添加下载信息
    :param video_id:
    :param state:
    :return:
    """
    cursor = conn.cursor()
    sql = INSET_DOWLOAD_MESSAGE.format(video_id, '0')
    try:
        cursor.execute(sql)
        conn.commit()
        return True
    except MySQLdb.IntegrityError as e:
        return False
    finally:
        cursor.close()


def delete_download_message(video_id):
    """
    删除下载信息
    :param video_id:
    :return:
    """
    cursor = conn.cursor()
    sql = DELETE_DOWNLOAD_MESSAGE.format(video_id)
    cursor.execute(sql)
    conn.commit()
    cursor.close()


def update_download_large(video_id, large):
    """
    更新下载影片的总片数
    :param video_id:
    :param large:
    :return:
    """
    cursor = conn.cursor()
    sql = UPDATE_DOWNLOAD_LARGE.format(str(large), video_id)
    cursor.execute(sql)
    conn.commit()
    cursor.close()


def init_env_environment(display=False):
    """
    初始化环境 创建 m3u8 output video 文件夹
    :return:
    """
    dirs = ['video']
    for path in dirs:
        if not (os.path.exists(path) and os.path.isdir(path)):
            os.mkdir(path)
    if os.path.exists('error.txt'):
        os.remove('error.txt')
    if display:
        print('[*] 环境初始化成功!')


def get_update_message():
    """
    获取更新页面信息
    :return:
    """
    cursor = conn.cursor()
    args_dic = dict()
    cursor.execute(GET_PAGE_MESSAGE)
    page_message = cursor.fetchall()
    for item in page_message:
        if item[0] == "start_page":
            args_dic["start"] = item[1]
        elif item[0] == 'end_page':
            args_dic["end"] = item[1]
    cursor.close()
    return args_dic


def save_update_message(args_dic):
    """
    保存更新页面信息
    :param args_dic:
    :return:
    """
    cursor = conn.cursor()
    cursor.execute(UPDATE_START_PAGE.format(args_dic["start"]))
    cursor.execute(UPDATE_END_PAGE.format(args_dic["end"]))
    cursor.connection.commit()
    cursor.close()


def get_movie_download_message(video_id):
    """
    获取影片下载信息
    :return:
    """
    cursor = conn.cursor()
    cmd = GET_DOWNLOAD_MOVIE_FROM_ID.format(video_id)
    cursor.execute(cmd)
    result = cursor.fetchone()
    cursor.close()
    if result is not None:
        return result[0]
    else:
        add_download_message(video_id, 0)
        return 0


if __name__ == '__main__':
    print(type(get_movie_download_message('ab858e8639d805fb8fdcfbc151de90d')))