"""Real product page or explicit workbench fixture, sharing native browser APIs.
Fixtures always load through the actual workbench; no application gate is bypassed.
"""
from urllib.parse import urlencode, urlsplit, parse_qsl, urlunsplit
class ProductBrowser:
    def __init__(self,page):
        self.host=page
        self.frame=None
        self.generation=0
        self.base_viewport=page.viewport_size
    def __getattr__(self,name):
        if name in {'context','keyboard','mouse','expect_download','on','close','bring_to_front'}:
            return getattr(self.host,name)
        return getattr(self.frame or self.host,name)
    def set_viewport_size(self,size):
        self.base_viewport=size
        return self.host.set_viewport_size(size)
    def goto(self,url,**kwargs):
        if self.frame and self.base_viewport:self.host.set_viewport_size(self.base_viewport)
        self.frame=None
        return self.host.goto(url,**kwargs)
    def reload(self,**kwargs):
        return self.frame.goto(self.frame.url,**kwargs) if self.frame else self.host.reload(**kwargs)
    def screenshot(self,**kwargs):
        if self.frame:
            kwargs.pop('full_page',None)
            return self.host.locator('#product-frame').screenshot(**kwargs)
        return self.host.screenshot(**kwargs)
    def open_product(self,base,route='home',scenario='default',theme='sunrise',reset=True,wait_until='networkidle'):
        if scenario=='default':
            self.goto(base+'/prototype/index.html?'+urlencode({'theme':theme,**({'reset':'1'} if reset else {})})+'#'+route,wait_until=wait_until)
        else:
            self.generation+=1
            self.goto(base+'/?fixture-check='+str(self.generation)+'#'+urlencode({'page':'home','route':route,'scene':scenario,'theme':theme,'width':str((self.base_viewport or {}).get('width',390)) if (self.base_viewport or {}).get('width') in [320,360,390,430] else '390'}),wait_until=wait_until)
            self.host.set_viewport_size({'width':1440,'height':1200})
            self.host.wait_for_function("document.querySelector('#runtime-status').textContent.includes('原型已连接')")
            self.host.locator('#preview-scale').select_option('actual')
            self.frame=self.host.locator('#product-frame').element_handle().content_frame()
            if reset:
                u=urlsplit(self.frame.url);q=dict(parse_qsl(u.query));q['reset']='1';q['theme']=theme
                self.frame.goto(urlunsplit((u.scheme,u.netloc,u.path,urlencode(q),route)),wait_until=wait_until)
            self.frame.wait_for_function('ProductContext.fixture===true')
            assert '非本人资料' in self.host.locator('#stage-caption').inner_text()
        self.wait_for_function('window.App&&App.snapshot')
        return self
