# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: SQL.py
@time: 2018/11/4 21:14
@describe: 程序中使用的SQL语句
"""
SEARCH_SQL = '''
            select  movie.title,video_url.m3u8_url,  video_images.issue_time,movie.movie_url, video_images.big_images_path, movie.image_path, movie.movie_object_id from movie ,video_url, video_images
            where movie.title like '%{}%' and movie.movie_object_id = video_url.video_object_id
            and video_images.video_object_id=movie.movie_object_id
            group by movie.movie_object_id order by video_images.issue_time DESC;
            '''

UPDATE_START_PAGE = '''
                    UPDATE `52av`.`select_rule` t SET t.`css_selector` = '{}' WHERE t.`id` = 7
                    '''

UPDATE_END_PAGE = '''
                    UPDATE `52av`.`select_rule` t SET t.`css_selector` = '{}' WHERE t.`id` = 8
                    '''

GET_PAGE_MESSAGE = "select item_name,css_selector from select_rule where type = 5;"

GET_DOWNLOAD_MOVIE = '''
            select  movie.movie_object_id ,movie.title,video_url.m3u8_url,  video_images.issue_time,movie_download.state, video_images.big_images_path 
            from movie ,video_url, video_images, movie_download
            where movie.movie_object_id = video_url.video_object_id
            and video_images.video_object_id=movie.movie_object_id and movie_download.video_object_id = movie.movie_object_id 
            group by movie.movie_object_id order by movie_download.id ASC ;

'''

UPDATE_DOWLOAD_MESSAGE = '''
    UPDATE movie_download SET movie_download.state = '{}' where movie_download.video_object_id = '{}'
    '''

INSET_DOWLOAD_MESSAGE = '''
INSERT INTO `52av`.`movie_download` (`video_object_id`, `state`) VALUES (\'{}\', \'{}\')
'''

DELETE_DOWNLOAD_MESSAGE = '''
                    DELETE FROM `52av`.`movie_download` WHERE `video_object_id` = \'{}\'
                    '''

UPDATE_DOWNLOAD_LARGE = '''
                    UPDATE `52av`.`movie_download` t SET t.`large` = \'{}\' WHERE t.`video_object_id` = \'{}\'
'''

GET_DOWNLOAD_MOVIE_FROM_ID = '''
        SELECT state FROM `52av`.`movie_download` where video_object_id = \'{}\'
'''

if __name__ == '__main__':
    pass