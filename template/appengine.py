# coding=utf-8
import os, json, re, urllib, datetime, time, types
import webapp2
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template, blobstore_handlers, RequestHandler
from google.appengine.api import app_identity, mail, memcache
from google.appengine.ext import blobstore, ndb, vendor
import util


class unit(ndb.Model):
	# 分類
	born = ndb.DateTimeProperty(auto_now_add=True)
	area = ndb.StringProperty()
	kusr = ndb.KeyProperty()
	kart = ndb.KeyProperty()
	kitm = ndb.KeyProperty()
	# 文章検索用
	cate = ndb.StringProperty()
	name = ndb.StringProperty()
	iden = ndb.StringProperty()
	addr = ndb.StringProperty()
	ukey = ndb.StringProperty()
	usec = ndb.StringProperty()
	# 文章
	text = ndb.TextProperty()
	desc = ndb.TextProperty()
	# 検索用
	gram = ndb.StringProperty(repeated=True)
	tags = ndb.StringProperty(repeated=True)
	# 数値
	time = ndb.DateTimeProperty()
	amount = ndb.IntegerProperty()
	countview = ndb.IntegerProperty()
	countlike = ndb.IntegerProperty()
	countreply = ndb.IntegerProperty()
	rate = ndb.FloatProperty()
	flag = ndb.BooleanProperty()
	# JSON
	service = ndb.JsonProperty()
	detail = ndb.JsonProperty()
	# ファイル
	smallblob = ndb.BlobProperty()
	largeblob = ndb.BlobProperty()
	smallfile = ndb.BlobKeyProperty()
	largefile = ndb.BlobKeyProperty()

	def format(s):
		return {}

	@classmethod
	def getgramfilter(cls, query):
		return [cls.gram == i for i in cls.getgram(query)]

	@classmethod
	def getgram(cls, x):
		return [x[i:i + 2] for i in range(0, len(x) - 1)]

	def getgramtext(self):
		return (self.name or "") + (self.text or "") + "".join(self.tags)

	@classmethod
	def get_by_short(cls, str, keys_only=False):
		if not str:
			return None
		try:
			if hasattr(str, "__iter__"):
				key = [ndb.Key(cls, util.intchars(i)) for i in str]
				return key if keys_only else ndb.get_multi(key)
			else:
				key = ndb.Key(cls, util.intchars(str))
				return key if keys_only else key.get()
		except:
			pass

	@classmethod
	def short(cls, some):
		if isinstance(some, ndb.Model):
			some = some.key
		if isinstance(some, ndb.Key):
			return util.intchars(int(some.id()))

	@classmethod
	def delete_multi(cls, keys):
		ndb.delete_multi(keys)

	@classmethod
	def get_multi(cls, keys):
		return ndb.get_multi(keys)

	@classmethod
	def put_multi(cls, keys):
		ndb.put_multi(keys)

	@classmethod
	def _pre_delete_hook(c, k):
		self = k.get()
		blobstore.delete([self.smallfile, self.largefile])
		ndb.delete_multi(c.query(ndb.OR(c.kusr == self.key, c.kart == self.key, c.kitm == self.key)).fetch(keys_only=True))

	def _pre_put_hook(self):
		self.gram = self.__class__.getgram(self.getgramtext())


class workhandler(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
	@classmethod
	def app(cls):
		return webapp2.WSGIApplication([('/blob/([^/]+)?', BlobHandler), ('/.*', cls), ])

	def bodyraw(self):
		return self.request.body

	def bodyjson(self):
		tmp = self.request.body
		if tmp[-1] == "=": tmp = tmp[:-1]
		return json.loads(urllib.unquote_plus(tmp))

	def getfile(self):
		return [i.key() for i in self.get_uploads()]

	def setcookie(self, k, v, **kwargs):
		kwargs = kwargs or {"day": 100}
		kwargs = (kwargs.get("hour", 0) + kwargs.get("day", 0) * 24) * 60 * 60
		self.setheader('Set-Cookie', '{0}={1}; path=/; max-age={2}'.format(k, v, kwargs))

	def setheader(self, k, v):
		self.response.out.headers.add(k, v)

	def redirect(self, address):
		if isinstance(address, unicode):
			address = address.encode("utf-8")
		RequestHandler.redirect(self, address)

	def response(s, a):
		if False:
			context = ndb.get_context()
			context.clear_cache()
			context.set_cache_policy(lambda key: False)
			context.set_memcache_policy(lambda key: False)
		if any(i.size == 0 for i in s.get_uploads()):
			blobstore.delete(i.key() for i in s.get_uploads())
		# 処理の階層化を防ぐ
		pass

	def post(s):
		s.response()

	def get(s):
		s.response()

	def root(s, path):
		check = False
		if isinstance(path, str):
			check = (s.request.path == path)
		if isinstance(path, types.FunctionType):
			check = path(s.request.path)
		if check:
			# 引数
			s.params = {"host": s.request.host_url, "path": s.request.path, "query": s.request.query_string}
			s.params.update(s.request.cookies)
			s.params.update(s.request.params)
			return True

	def write_json(self, data):
		def jsondefault(o):
			if isinstance(o, ndb.Model):
				r = o.to_dict()
				r["key"] = o.key
				return r
			if isinstance(o, ndb.Key):
				return {"id": o.id(), "kind": o.kind(), "urlsafe": o.urlsafe()}
			if isinstance(o, datetime.datetime):
				return {
					"unixtime": int(time.mktime(o.timetuple())),
					"input": o.strftime('%Y-%m-%dT%H:%M'),
					"date": o.strftime('%Y-%m-%d'),
					"minutes": o.strftime('%Y-%m-%d %H:%M'),
					"seconds": o.strftime('%Y-%m-%d %H:%M:%S'),
				}
			if isinstance(o, blobstore.BlobKey):
				return str(o)
			return None

		self.response.out.write(json.dumps(data, default=jsondefault, indent=4))

	def write_temp(self, temp, params, **kwargs):
		tmp = os.path.join(os.path.dirname(__file__), "../" + temp)
		if os.path.exists(tmp):
			self.response.out.write(template.render(tmp, params).replace(u"<<", u"{{").replace(u">>", u"}}"))
		if "contenttype" in kwargs:
			self.response.headers['Content-Type'] = kwargs["contenttype"]

	def write_blob(self, blob):
		self.response.headers.add_header('X-AppEngine-BlobKey', blob)
		if "Range" in self.request.headers:
			r = re.findall(r"\d+", self.request.headers['Range'])
			self.response.headers.add_header('X-AppEngine-BlobRange', "bytes={0}-{1}".format(int(r[0]), int(r[1]) if len(r) >= 2 else int(r[0]) + 1048576))

	def write(self, text):
		self.response.out.write(text)

	def __getattr__(s, k):
		return vars(s).get("params", {}).get(k, None)


class BlobHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, photo_key):
		self.send_blob(photo_key)


class nonedict():
	def __init__(self, params):
		self.params = params

	def __getattr__(self, key):
		return self.params.get(key, None)


def statefunction(func):
	def wrapper(**kwargs):
		r = func(nonedict(kwargs))
		if False:
			pass
		elif isinstance(r, int):
			r = {"status": r}
		elif isinstance(r, dict):
			r["status"] = 200
		return r
	return wrapper

try:
	vendor.add('lib')
except ValueError as e:
	pass


def sendmail(**data):
	data["sender"] = u"anything@{0}.appspotmail.com".format(app_identity.get_application_id())
	mail.send_mail(sender=data["sender"], to=data["to"], subject=data["subject"], body=data["body"])


def getuploadurl(nexturl, maxbytes=None):
	return blobstore.create_upload_url(nexturl, max_bytes_per_blob=maxbytes)


def httpfunc(r):
	r = urlfetch.fetch(url=r["url"], payload=r["data"], method=urlfetch.POST if r["method"] == "POST" else urlfetch.GET, headers=r["header"])
	return (r.status_code, r.content)


def register_template(module="template.filter"):
	return template.register_template_library(module)


try:
	import cloudstorage


	def uploadfile(data, name):
		bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
		gcs_file = cloudstorage.open("/{}/{}".format(bucket_name, name), 'w')
		gcs_file.write(data)
		gcs_file.close()
		key = blobstore.create_gs_key("/gs/{}/{}".format(bucket_name, name))
		key = blobstore.BlobKey(key)
		return key
except ImportError as e:
	pass
