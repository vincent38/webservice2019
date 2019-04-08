# -*- coding: utf-8 -*-
from google.appengine.ext.webapp import template
import json as JSON

register = template.create_template_register()


@register.filter
def setlist(value):
	if hasattr(value, "__iter__"):
		return list(set(value))
	return []


@register.filter
def dateformat(value, format=u"%Y-%m-%d"):
	return value and value.strftime(format)


@register.filter
def dateRFC1123format(value):
	week = u"Mon Tue Wed Thu Fri Sat Sun".split()
	week = week[value.weekday()]
	month = u"Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
	month = month[value.month - 1]
	return value and value.strftime(u"{}, %d {} %Y %H:%M:%S GMT").format(week, month)


@register.filter
def vue(value):
	# vueの制御文は無害な形に変換
	value = value.replace(u"{{", u"｛｛").replace(u"}}", u"｝｝")
	return value


@register.filter
def json(value):
	return JSON.dumps(value)