# -encoding:utf-8
from template.appengine import *
from template.unit import *
from datetime import datetime
def hello(request):
	return tempres("index.html", {
		"title":"平成最後のウェブサービス",
		"messagelist":unit.query().order(+unit.born).fetch()
	})
def post(request):
	args=requestargs(request)
	if args["type"]=="message.post":
		unit(name=args["name"],text=args["text"]).put()
	return passres("/")

app = wsgiapp([('/', hello),('/post', post)])