import datetime,time,base64,hmac,hashlib
chars=unicode
bytes=bytes
integer=(int,long)
def intchars(src):
	if isinstance(src,(chars,bytes)):
		return intbytes(base64.b64decode(chars(src)+u"="*{3:1,2:2,1:3,0:0}[len(src)%4]))
	if isinstance(src,integer):
		return chars(base64.b64encode(intbytes(src))).replace(u"=",u"")
def intbytes(src):
	if isinstance(src,bytes):
		dest=0
		for i in src:
			dest=(dest<<8)+ord(i)
		return dest
	if isinstance(src,integer):
		dest=""
		while src:
			dest,src=chr(src&0xff)+dest,src>>8
		return dest

def datauri(src):
	if src:
		if isinstance(src,chars):
			header, encoded = src.split(",", 1)
			return base64.b64decode(encoded)
		else:
			return u"data:application/octet-stream;base64,"+base64.b64encode(src)

def unixtime(t=None):
	t = t or datetime.datetime.now()
	if isinstance(t, int):
		return datetime.datetime.fromtimestamp(t)
	else:
		return int(time.mktime(t.timetuple()))

class nonedict():
	def __init__(self, params):
		self.params=params
	def __getattr__(self,key):
		return self.params.get(key,None)

if __name__ == '__main__':
	print(nonedict({"a":2}).a)