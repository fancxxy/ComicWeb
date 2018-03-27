# ComicWeb
ComicWeb 是一个订阅漫画的网站，支持主流网站的漫画资源，项目仅供个人学习，请勿用于商业盈利。  
项目使用的主要框架和组件是flask+bootstrap+mysql，后端核心功能查看 [fancxxy/comicd](https://github.com/fancxxy/comicd)。

## 配置

``` shell
$ git clone git://github.com/fancxxy/ComicWeb.git
$ cd ComicWeb/

创建虚拟环境
$ python3 -m venv venv
$ source venv/bin/activate

安装依赖
$ pip install git+git://github.com/fancxxy/comicd.git
$ pip install -r ComicWeb/requirements.txt

设置环境变量，需手动修改数据库连接串 
$ export $(cat env.sh | grep -v ^# | xargs)

升级数据库
$ flask db init
$ flask db migrate -m "init"
$ flask db upgrade

直接运行
$ flask run --host 0.0.0.0 --port 5000

使用uWSGI，需要root权限
# cp uwsgi.service /etc/systemd/system/
# systemctl enable uwsgi
# systemctl start uwsgi
```

## 截图
![index](screenshots/index.png)

![comic](screenshots/comic.png)

![chapter](screenshots/chapter.png)

