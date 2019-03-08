### 52av_video_player

this project is base on [52avSpider](https://github.com/abadfox233/52avSpider)

use the Mysql and Pyqt5  

----

### request
* python3
* PyQt5
* [vlc](https://github.com/oaubert/python-vlc)
* [m3u8](https://github.com/globocom/m3u8)
* [requests](https://github.com/kennethreitz/requests)
* Mysqldb
* you should install vlc player or have libvlc.dll
   > you should edit you libvlc.dll on ./other_widget/video_page.py
   >> `os.environ['PATH'] += ';' + r'D:\VLC'`
* aria2c 
    > you should add the aria2c dir to system PATH
---

### Firstly

> you should have some data on Mysql
>
> you can config you sql setting on ./tools/video_api.py
>
> if you don't hava video data you can import you sql_data form the project [52avSpider](https://github.com/abadfox233/52avSpider)

> 

### Something 
* about the platform
>this project can just run on widows
>if you want run this project on other platform you can edit the file ./other_widget/video_page.py

* about the video 
>the video is store in ./video
>if you want to edit the video store dir you can edit the file ./tools/download_m3u8.py
>>`base_dir = './video/'`

* the config file is the video_config.init
> the initial setting is this
```
[db]
db_user = 52av
db_password = 52av
db_database = 52av

[setting]
start_image_path = E:\mycs\python\scrapyproject\project_av\project_av\images\
download_m3u8_proxy = False
proxy_ip = 127.0.0.1
proxy_port = 1080
tuo_pan = False
show_tuo_pan = True

[aria2c]
max_download = 70
max_connect = 16
proxy = False
proxy_ip = 127.0.0.1
proxy_port = 1080

[update]
start_page = 0
end_page = 5

```

* about the [52avSpider](https://github.com/abadfox233/52avSpider)

> you must edit the 52avSpider dir on ./tools/VideoUpdate.py
>>`spider_path = r'E:\mycs\python\scrapyproject\project_av\project_av'`

----

### Quickly Start

`python home.py`