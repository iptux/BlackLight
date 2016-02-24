#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# weibo_cn.py
# simulate logins to weibo.cn
#
# Author: Alex.wang
# Create: 2016-02-29 16:32


import gzip
import urllib
import urllib2
import urlparse
import cPickle
import logging
from bs4 import BeautifulSoup
from cookielib import CookieJar
from cStringIO import StringIO
from ConfigParser import ConfigParser


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'


class WeiboWap(object):
	CONFIG = 'weibo_wap.conf'
	SECTION = 'weibo'
	COOKIE = 'cookie'
	HEADERS = {
		'Accept': '*/*',
		'Accept-Encoding': 'gzip',
		'User-Agent': USER_AGENT,
	}

	BASE = 'https://weibo.cn/'
	LOGIN = 'https://login.weibo.cn/login/'
	PHOTO = 'photo.weibo.com'

	def __init__(self):
		self._init_conf()
		self.cookie = CookieJar()
		self._load_cookie()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))

	def _init_conf(self):
		self.conf = ConfigParser()
		self.conf.add_section(self.COOKIE)
		self.conf.add_section(self.SECTION)
		self.conf.set(self.SECTION, 'user', '')
		self.conf.set(self.SECTION, 'pass', '')
		self.conf.set(self.SECTION, 'login', 'false')
		self.conf.read(self.CONFIG)

	def _load_cookie(self):
		for name, value in self.conf.items(self.COOKIE):
			self.cookie.set_cookie(cPickle.loads(value.decode('base64')))

	def save_cookie(self):
		if not self.conf.has_section(self.COOKIE):
			self.conf.add_section(self.COOKIE)
		for c in self.cookie:
			self.conf.set(self.COOKIE, '%s_%s' % (c.name, c.domain), cPickle.dumps(c, cPickle.HIGHEST_PROTOCOL).encode('base64'))
		self.save()

	def save(self):
		with open(self.CONFIG, 'w+') as fp:
			self.conf.write(fp)

	def isLogin(self):
		return self.conf.getboolean(self.SECTION, 'login')

	def setLogin(self, value):
		self.conf.set(self.SECTION, 'login', 'true' if value else 'false')
		self.save()

	def _request(self, url, query = None, data = None, headers = None, timeout = 30):
		url = '{0}{1}'.format(url, '?' + urllib.urlencode(query) if query else '')
		logging.debug('request url: %s', url)
		if not headers:
			headers = self.HEADERS
		else:
			for k,v in cls.HEADERS.items():
				headers.setdefault(k, v)
		req = urllib2.Request(url, urllib.urlencode(data) if data else None, headers)
		f = self.opener.open(req, timeout = timeout)
		data = f.read()
		if 'gzip' == f.info().getheader('Content-Encoding'):
			data = gzip.GzipFile(fileobj = StringIO(data)).read()
		self.save_cookie()
		return data

	def _get_captcha(self, url):
		gif = 'weibo_wap.gif'
		with open(gif, 'w+') as fp:
			img = self._request(url)
			fp.write(img)

		# do it on demand
		import Tkinter
		import tkSimpleDialog
		class CaptchaDialog(tkSimpleDialog.Dialog):
			def __init__(self, master, title, image):
				self.image = image
				tkSimpleDialog.Dialog.__init__(self, master, title)
			def body(self, master):
				img = Tkinter.PhotoImage(file = self.image)
				label = Tkinter.Label(master, image = img)
				label.image = img
				label.pack()
				self.captcha = Tkinter.StringVar(master, '')
				text = Tkinter.Entry(master, textvariable = self.captcha).pack()
			def apply(self):
				self.result = self.captcha.get()

		return CaptchaDialog(Tkinter.Tk(), 'Captcha Challenge', 'weibo_wap.gif').result

	def _login(self, user, passwd):
		if not user or not passwd:
			return False
		page = self._request(self.LOGIN)
		soup = BeautifulSoup(page)
		form = soup.find('form')
		data = {}
		for node in form.find_all('input'):
			key = node['name']
			data[key] = node.get('value', passwd if key.startswith('password') else '').encode('utf8')
		img = form.find('img')
		data['code'] = self._get_captcha(img['src'])
		if not data['code']:
			return False
		data['remember'] = 'on'
		data['mobile'] = user
		html = self._request(urlparse.urljoin(self.LOGIN, form['action']), data = data)
		return html.find(u'退出'.encode('utf8')) >= 0

	def login(self):
		if not self.isLogin():
			v = self._login(self.conf.get(self.SECTION, 'user'), self.conf.get(self.SECTION, 'pass'))
			logging.info('login result: %s', v)
			self.setLogin(v)
		return self.isLogin()

	def getPic(self, url):
		u = urlparse.urlparse(url)
		if not self.PHOTO == u.netloc:
			return None
		try:
			logging.info('try to get pic: url=%s', url)
			html = self._request(url)
			soup = BeautifulSoup(html)
			img = soup.find('img')
			if img['src'].find('sinaimg.cn') < 0:
				return None
			return img['src'].replace('bmiddle', 'large')
		except Exception as e:
			logging.exception('failed to getPic: %s', url)
			return None


if __name__ == '__main__':
	w = WeiboWap()
	print w.login()

