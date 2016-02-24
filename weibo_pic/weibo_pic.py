#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# weibo_pic.py
# get read comment pic URL for weibo. wsgi module
#
# Author: Alex.wang
# Create: 2016-02-20 22:40


import logging
import urlparse
from weibo_wap import WeiboWap


logging.basicConfig(format = '%(asctime)-15s %(message)s', level = logging.INFO, filename = '/tmp/weibo_pic.log')

weibo = WeiboWap()
if not weibo.isLogin():
	quit()

def application(env, start_response):
	global weibo
	param = env['wsgi.input'].read()
	logging.info('get param: %s', param)
	data = urlparse.parse_qs(param)
	if 'url' in data:
		pic = weibo.getPic(data['url'][0])
		if pic:
			start_response('200 OK', [('Content-Type', 'text/plain')])
			return pic
	start_response('404 Not Found', [('Content-Type', 'text/plain')])
	return '404 Not Found'

