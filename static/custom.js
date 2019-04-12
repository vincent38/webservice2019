function httpsend(url,param,onload){
	var xhr = new XMLHttpRequest()
	var formData = new FormData();
	for(var j in param){
		formData.append(j,param[j])
	}
	xhr.onload = (function(onload,self) {
        return function(e) {
			onload.call(self,xhr.response)
        };
    })(onload,this);
	xhr.open('POST', url, true)
	xhr.withCredentials = true;
	xhr.responseType = 'json';
	xhr.send(formData)
}
function closemodal(){
	$(".modal").modal('hide')
}
function update(state,source){
	for(key in source){
		state[key]=source[key]
	}
}
function httpupdate(state,path,data,func){
	httpsend.call(this,path,data,function (source) {
		update(state,source)
		if(func)func.call(this,source)
	})
}
Vue.component('categoryinput', {
	template: '#categoryinput-templateold',
	props: ["language","category","model"],
})
Vue.component('imageinput', {
	template: '#imageinput-templateold',
	props: ["language","model"],
	data: function () {
		return {uri:""}
	},
	methods: {
		change:function(e){
			this.language="ch"
			var file = e.target.files;
			file = file.length>0?file[0]:0
			if(file){
				var f1 = new FileReader() ;
				f1.onload=(function(self) {
		            return function(e) {
		                self.model.image=this.result
		            };
		        })(this);
				f1.readAsDataURL(file);
			}
		},
	},
})
Vue.component('translation', {
	template: '#translation-templateold',
	props: ["language","model","name"],
	data: function () {
		return {tx:"",txtmp:"",auto:"true",limit:200}
	},
	created: function(){
		setInterval(this.translate, 1000);
	},
	methods: {
		translate:function(){
			if((this.tx!=this.txtmp)&&this.auto){
				this.txtmp=this.tx
				httpsend.call(this,"/translate",{q:this.tx},function (text) {
					this.limit=this.limit
					if(this.name){
						this.model.namejp=text.jp
						this.model.namech=text.ch
					}else{
						this.model.textjp=text.jp
						this.model.textch=text.ch
					}
					this.$forceUpdate()
				})
			}
		},
	},
})
Vue.component('ranking', {
	template: '#ranking-templateold',
	props: ["language","category","state"],
	created: function(){
	    update(this,this.state)
	},
	data: function () {
		return {}
	},
	computed :{
		channelrank:function(){
			var key,mul;
			key,mul=this.order
			return this.channellist.slice().sort(function(a,b){
				return -(a[key]-b[key])
			});
		},
	},
	methods:{
		getcategory:function(channel){
			var cate=(channel.category in this.category)?this.category[channel.category]:this.category["chat"]
			return this.language=='jp'?cate.namejp:cate.namech
		}
	}
})

Vue.component('channel', {
	template: '#channel-templateold',
	props: ["language","category","state"],
	data: function () {
		return {
			model:{action:"new",channel:"",namejp:"",namech:"",textjp:"",textch:"",image:""}
		}
	},
	created: function(){
	    update(this,this.state)
	    console.log(this)
	},
	computed :{
	},
	methods:{
		messagenew:function(){
			this.model.channel=this.channel.key
			this.model.action="messagenew"
			httpupdate.call(this,this,"/channel",this.model,function(tmp){
				this.model.action=""
				this.model.image=""
				httpupdate.call(this,this,"/channel",this.model,function(tmp){
					this.$forceUpdate()
				})
			})
		},
		getcategory:function(channel){
			var cate=(channel.category in this.category)?this.category[channel.category]:this.category["chat"]
			return this.language=='jp'?cate.namejp:cate.namech
		}
	}
})
Vue.component('navbar', {
	template: '#navbar-templateold',
	props: ["language","account","category","status","state"],
	data: function () {
		return {
			model:{action:"new",idart:"",namejp:"",namech:"",textjp:"",textch:"",image:""},
			modelchannel:{action:"new",category:"chat",namejp:"",namech:"",textjp:"",textch:"",image:""}
		}
	},
	created: function(){
		update(this.model,this.account)
	},
	methods: {
		signin:function(){
			this.model.action="cok"
			httpupdate(this.state,"/main",this.model,function(source){
				if(source.status==200){closemodal()}
			})
		},
		signup:function(){
			this.model.action="new"
			httpupdate(this.state,"/main",this.model,function(source){
				if(source.status==200){closemodal()}
			})
		},
		signma:function(){
			this.model.action="mal"
			httpupdate(this.state,"/main",this.model)
		},
		signset:function(){
			this.model.action="set"
			httpupdate(this.state,"/main",this.model,function(source){
				if(source.status==200){closemodal()}
			})
		},
		signout:function(){
			this.model.action="out"
			httpupdate(this.state,"/main",this.model)
		},
		channelnew:function(){
			this.modelchannel.action="new"
			httpupdate({},"/channel",this.modelchannel,function(source){
				if(source.status==200){
					window.location.href = '/channel/'+source.channel.key;
				}
			})
		},
	}
})