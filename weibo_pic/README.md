Weibo Picture URL Resolver
------

#### Dependency

* [BeautifulSoup][] to parse HTML.
* [Tkinter][] to show captcha.

#### Login

* Fill *weibo_wap.conf* with weibo account info. (see *weibo_wap.conf.sample* as a sample)
* Run `python weibo_wap.py` and input captcha to login.
* Cookies will be stored in *weibo_wap.conf*.

#### Deploy

Run *weibo_pic.py* as a [WSGI][] app. (*weibo_pic.ini* for sample [uWSGI][] config)

#### Resolve

`curl --data-urlencode 'url=http://photo.weibo.com/h5/comment/compic_id/XXXX' http://www.example.com/some/path`

[BeautifulSoup]: http://www.crummy.com/software/BeautifulSoup/
[Tkinter]: https://wiki.python.org/moin/TkInter
[WSGI]: https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[uWSGI]: https://github.com/unbit/uwsgi
