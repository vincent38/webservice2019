# -encoding:utf-8
import template.request as request
from template.appengine import *
import copy, hashlib

register_template()
request.httpfunc = httpfunc
# preset
maxfilesize = 512 * 1024

@statefunction
def statemain(s):
	def hash(hash):
		return hashlib.sha224("233ch.net" + str(hash)).hexdigest()[:6]
	def sendvalidation(email):
		code = hash(email)
		sendmail(to=email, subject="【233ch.net】your validation code is {0}".format(code), body="validation code:{0}\n\nThanks for using the site".format(code))
	account=unit.get_by_short(s.account)
	category = """anime アニメ 动漫;study 勉強 学习;comic 漫画 漫画;game ゲーム 游戏;university 大学 大学;music 音楽 音乐;computer パソコン 电脑;news ニュース 新闻;chat 雑談 聊天;work 仕事 工作"""
	category = {name: {"name": name, "namejp": namejp, "namech": namech} for name, namejp, namech in (i.split() for i in category.split(";"))}
	if s.action == "mal":
		sendvalidation(s.email)
	if s.action == "cok":
		m = unit.query(unit.area == "account", unit.ukey == s.email, unit.usec == s.password).get()
		if not m:
			return 400
		else:
			account=m
	if s.action == "new":
		if hash(s.email) != s.code:
			return 400
		else:
			m = unit.query(unit.area == "account", unit.ukey == s.email).get() or unit()
			m.populate(area="account", ukey=s.email, usec=s.password, name=s.name)
			m.put()
			account=m
	if s.action == "out":
		account=None
	if s.action == "set":
		if not account:
			return 400
		else:
			account.storequery(s).put()
	return {
		"account":account and account.format(),
		"language":"ch",
		"category":category,
	}
@statefunction
def statechannel(s):
	channel=unit.get_by_short(s.channel)
	message=unit.get_by_short(s.message)
	account=unit.get_by_short(s.account)
	if s.action == "new":
		if account:
			channel = unit()
			channel.storequery(s)
			channel.populate(area="channel", kusr=account.key)
			channel.put()
			channel.storeindex().put()
		else:
			return 401
	if s.action == "del":
		if not account:
			return 401
		elif not (channel and account.key == channel.kusr):
			return 402
		else:
			channel.key.delete()
			return 200
	if s.action == "set":
		if not account:
			return 401
		elif not (channel and account.key == channel.kusr):
			return 402
		else:
			channel.storequery(s).put()
	if s.action == "messagenew":
		if not (account and channel):
			return 401
		else:
			message = unit(area="message", kusr=account.key, kart=channel.key)
			message.storequery(s)
			message.populate(area="message", kusr=account.key, kart=channel.key)
			message.put()
			channel.storeindex().put()
			return 200
	if s.action == "messagedel":
		if not account:
			return 401
		elif not message and account.key == message.kusr:
			return 402
		else:
			message.key.delete()
			channel.storeindex().put()
			return 200
	if s.action == "messageset":
		if not account:
			return 401
		elif not message and account.key == message.kusr:
			return 402
		else:
			message.storequery(s).put()
			return 200
	if not s.action:
		if channel:
			channel.countview=(channel.countview or 0) + 1
			channel.put()
	return {
		"channel":channel and channel.format(musr=1),
		"messagelist":channel and [i.format(musr=1) for i in unit.query(unit.area == "message", unit.kart == channel.key).order(+unit.born).fetch(10000)]
	}

@statefunction
def statetranslation(s):
	def translate(text, target):
		q={"q": text,"target": target,"format": "text","key": "AIzaSyCXiPjrIvSkxVUydLlfZIjm6QEiwA9dxLU"}
		r = request.post("https://translation.googleapis.com/language/translate/v2", q, datatype="json")
		return "".join(i["translatedText"] for i in r["data"]["translations"])
	return {
		"jp": translate(s.q, "ja"),
		"ch": translate(s.q, "zh-CN")
	}
@statefunction
def stateranking(s):
	orderlist={"new":-unit.born,"old":+unit.born,"pop":-unit.rate}
	size=5
	page=int(s.page or 0)
	order=s.order if s.order in orderlist.keys() else orderlist.keys()[0]
	channellist = unit.query(unit.area == "channel").order(orderlist[order]).fetch(size,offset=size*page)
	return {
		"order":order,
		"page":page,
		"channellist":[i.format(musr=1) for i in channellist]
	}
@statefunction
def statesitemap(s):
	return {"list":[i.format() for i in unit.query(unit.area == "channel").order(-unit.born).fetch(10000)]}

class unit(unit):
	def format(self,**kwargs):
		r={
			"key":unit.short(self),
			"image":util.datauri(self.smallblob),
			"name":self.name,
			"category":self.cate,
			"kusr":unit.short(self.kusr),
			"kart":unit.short(self.kart),
			"kitm":unit.short(self.kitm),
			"born":util.unixtime(self.born),
			"borntext":self.born.strftime('%Y-%m-%d %H:%M:%S'),
			"last":util.unixtime(self.time),
			"countview":self.countview or 0,
			"countreply":self.countreply or 0,
			"rate":self.rate or 0,
		}
		r.update(self.detail or {})
		if kwargs.get("musr",0):
			temp=self.kusr and self.kusr.get()
			r["musr"] = temp and temp.format()
		return r

	def storequery(s, self):
		s.populate(name=self.name, smallblob=util.datauri(self.image), cate=self.category)
		if self.kusr:
			s.kusr = unit.get_by_short(self.kusr, True)
		if self.kart:
			s.kart = unit.get_by_short(self.kart, True)
		if self.kitm:
			s.kitm = unit.get_by_short(self.kitm, True)
		if len(s.smallblob or []) > maxfilesize:
			s.smallblob = ""
		s.detail = s.detail or {}
		s.detail.update({"namejp": self.namejp, "namech": self.namech, "textjp": self.textjp, "textch": self.textch})
		return s

	def storeindex(self):
		now = datetime.datetime.now()
		message = unit.query(unit.area == "message", unit.kart == self.key).order(-unit.born).fetch()
		# 新着
		self.born = self.born
		self.countreply = len(message)
		self.time = (message and message[0].born) or self.born
		self.rate = sum(x.born > now - datetime.timedelta(days=1) for x in message)
		return self

	def getgramtext(self):
		x = lambda k: (self.detail and self.detail.get(k, "")) or ""
		return x("namejp") + x("namech") + x("textjp") + x("textch")


class work(workhandler):

	def work(s):
		if s.root("/translate"):
			s.write_json(statetranslation(**s.params))
		if s.root("/sitemap.xml"):
			s.write_temp("sitemap.xml",statesitemap(),contenttype="application/xml")
		if s.root("/"):
			s.write_temp("home.html",{
				"statemain": statemain(**s.params),
				"staterankingnew": stateranking(order="new"),
				"staterankingpop": stateranking(order="pop")
			})
		if s.root(lambda x:x.find("/channel/")>=0):
			s.write_temp("page.html",{
				"statemain": statemain(**s.params),
				"statechannel": statechannel(channel=s.path.split("/")[-1],**s.params),
				"staterankingnew": stateranking(order="new"),
				"staterankingpop": stateranking(order="pop")
			})
		if s.root("/main"):
			r=statemain(**s.params)
			s.setcookie("account",r.get("account",None) and r["account"]["key"])
			s.write_json(r)
		if s.root("/channel"):
			s.write_json(statechannel(**s.params))

app = work.app()
