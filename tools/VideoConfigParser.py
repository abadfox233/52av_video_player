# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: VideoConfigParser.py
@time: 2019/3/1 9:25
@describe: 播放器 配置解析模块
"""

import configparser
import os


class VideoConfigParserClass:
    """
        播放器 配置解析处理模块

    """
    mConfigParser = None

    def __init__(self, config_file_path: str = './video_config.init'):
        self.config_file_path = config_file_path
        self.mConfigParser = configparser.ConfigParser()
        self.__init_config_file__()

    def __init_config_file__(self):
        if not os.path.isfile(self.config_file_path):
            self.__create_config_file__()
        self.mConfigParser.read(self.config_file_path, encoding='utf-8')

    def __create_config_file__(self):
        """
        初次创建配置文件
        :return: void
        """
        self.mConfigParser.read(self.config_file_path, encoding="utf-8")
        if not self.mConfigParser.has_section("db"):
            self.mConfigParser.add_section("db")
            self.mConfigParser.set('db', 'db_user', '52av')
            self.mConfigParser.set('db', 'db_password', '52av')
            self.mConfigParser.set('db', 'db_database', '52av')
        if not self.mConfigParser.has_section("setting"):
            self.mConfigParser.add_section("setting")
            self.mConfigParser.set('setting', 'start_image_path',
                                   'E:\\mycs\\python\\scrapyproject\\project_av\\project_av\\images\\')
            self.mConfigParser.set('setting', 'download_m3u8_proxy', 'False')
            self.mConfigParser.set('setting', 'proxy_ip', '127.0.0.1')
            self.mConfigParser.set('setting', 'proxy_port', '1080')
            self.mConfigParser.set('setting', 'tuo_pan', 'False')
            self.mConfigParser.set('setting', 'show_tuo_pan', 'True')
        if not self.mConfigParser.has_section("aria2c"):
            self.mConfigParser.add_section("aria2c")
            self.mConfigParser.set('aria2c', 'max_download', '70')
            self.mConfigParser.set('aria2c', 'max_connect', '16')
            self.mConfigParser.set('aria2c', 'proxy', 'False')
            self.mConfigParser.set('aria2c', 'proxy_ip', '127.0.0.1')
            self.mConfigParser.set('aria2c', 'proxy_port', '1080')
        if not self.mConfigParser.has_section("update"):
            self.mConfigParser.add_section("update")
            self.mConfigParser.set('update', 'start_page', '0')
            self.mConfigParser.set('update', 'end_page', '5')
        self.save_config()

    def save_all_options(self, options_list):
        """
        一次性保存所有配置
        :param options_list:
        :return:
        """
        sections = ['db', 'db', 'db',
                    'setting', 'setting', 'setting', 'setting',
                    'aria2c', 'aria2c', 'aria2c', 'aria2c', 'aria2c',
                    'update', 'update']
        options = ['db_user', 'db_password', 'db_database',
                   'start_image_path', 'download_m3u8_proxy', 'proxy_ip', 'proxy_port',
                   'max_download', 'max_connect', 'proxy', 'proxy_ip', 'proxy_port',
                   'start_page', 'end_page'
                   ]
        for i in range(len(sections)):
            self.mConfigParser.set(sections[i], options[i], str(options_list[i]))
        self.save_config()

    def save_config(self):
        self.mConfigParser.write(open(self.config_file_path, 'w'))

    def get_db_setting(self) -> tuple:
        """
        default setting
            db_user = 52av
            db_password = 52av
            db_database = 52av
        :return:
        """
        try:
            db_user = self.mConfigParser.get('db', 'db_user')
            db_password = self.mConfigParser.get('db', 'db_password')
            db_database = self.mConfigParser.get('db', 'db_database')
            return db_user, db_password, db_database
        except configparser.NoOptionError:
            return '52av', '52av', '52av'

    def get_start_image_path(self) -> str:
        """
        default setting
            start_image_path = E:\mycs\python\scrapyproject\project_av\project_av\images\
        :return:
        """
        default_path = 'E:\\mycs\\python\\scrapyproject\\project_av\\project_av\\images\\'
        try:
            return self.mConfigParser.get('setting', 'start_image_path')
        except configparser.NoOptionError:
            return default_path

    @staticmethod
    def static_get_image_path() -> str:
        return VideoConfigParserClass().get_start_image_path()

    def get_m3u8_download_setting(self) -> tuple:
        """
        default setting
            download_m3u8_proxy = False
            proxy_ip = 127.0.0.1
            proxy_port = 1080
        :return:
        """
        try:
            is_proxy = self.mConfigParser.getboolean('setting', 'download_m3u8_proxy')
            proxy_ip = self.mConfigParser.get('setting', 'proxy_ip')
            proxy_port = self.mConfigParser.get('setting', 'proxy_port')
            return is_proxy, proxy_ip, proxy_port
        except configparser.NoOptionError:
            return False, '127.0.0.1', '1080'

    def get_aria2c_setting(self) -> tuple:
        """
        default setting
            max_download = 70
            max_connect = 16
            proxy = False
            proxy_ip = 127.0.0.1
            proxy_port = 1080
        :return:
        """
        try:
            max_download = self.mConfigParser.getint('aria2c', 'max_download')
            max_connect = self.mConfigParser.getint('aria2c', 'max_connect')
            proxy = self.mConfigParser.getboolean('aria2c', 'proxy')
            proxy_ip = self.mConfigParser.get('aria2c', 'proxy_ip')
            proxy_port = self.mConfigParser.get('aria2c', 'proxy_port')
            return max_download, max_connect, proxy, proxy_ip, proxy_port
        except configparser.NoOptionError:
            return 70, 16, False, '127.0.0.1', '1080'

    def get_update_setting(self) -> tuple:
        """
        default setting
            start_page = 0
            end_page = 5
        :return:
        """
        try:
            start = self.mConfigParser.getint('update', 'start_page')
            end = self.mConfigParser.getint('update', 'end_page')
            return start, end
        except configparser.NoOptionError:
            return 0, 5

    def get_tuo_pan_setting(self):
        """
        default setting
            tuo_pan = False
            show_tuo_pan = True
        :return:
        """
        try:
            tuo_pan = self.mConfigParser.getboolean('setting', 'tuo_pan')
            show_tuo_pan = self.mConfigParser.getboolean('setting', 'show_tuo_pan')
            return tuo_pan, show_tuo_pan
        except configparser.NoOptionError:
            return False, True

    def set_tuo_pan_setting(self, is_tuo_pan: bool = False, show_tuo_pan: bool = True) -> None:
        self.mConfigParser.set('setting', 'tuo_pan', str(is_tuo_pan))
        self.mConfigParser.set('setting', 'show_tuo_pan', str(show_tuo_pan))
        self.save_config()


if __name__ == '__main__':
    m = VideoConfigParserClass()
    m.set_tuo_pan_setting(True, True)
    print(m.get_tuo_pan_setting())