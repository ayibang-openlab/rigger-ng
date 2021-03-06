#coding=utf-8
import logging,copy
import rg_conf
import utls.rg_sh ,utls.rg_io
from utls.rg_io import rg_logger

class run_context :
    def __init__(self):
        self.restores = []
    def keep(self) :
        self.restores.append(  copy.copy(self.__dict__))
    def rollback(self):
        self.__dict__=  copy.copy(self.restores.pop())

class controlable :
    sudo = False
    def _allow(self,context):
        pass
    def _before(self,context):
        pass
    def _after(self,context):
        pass
    def _start(self,context):
        pass
    def _stop(self,context):
        pass
    def _reload(self,context):
        pass
    def _config(self,context):
        pass
    def _data(self,context):
        pass
    def _check(self,context):
        pass
    def _clean(self,context):
        pass
    def _info(self,context):
        return ""


def control_call(res,fun,context,tag) :

    with utls.rg_io.scope_iotag(res.__class__.__name__ ,tag) :
        if res._allow(context) :
            with utls.rg_sh.scope_sudo(res.sudo) :
                    utls.rg_io.run_struct.push( res.__class__.__name__)
                    res._before(context)
                    fun(res,context)
                    res._after(context)
                    utls.rg_io.run_struct.pop()

class control_box(controlable):

    def __init__(self):
        self._res = []

    def items_call(self,fun,context,tag):
        if hasattr(self,"_res") :
            for r in self._res :
                control_call(r,fun,context,tag)

    def _start(self,context):
        fun = lambda x,y : x._start(y)
        self.items_call(fun,context,'_start')

    def _stop(self,context):
        fun = lambda x,y : x._stop(y)
        self.items_call(fun,context,'_stop')

    def _config(self,context):
        fun = lambda x,y : x._config(y)
        self.items_call(fun,context,'_config')

    def _data(self,context):
        fun = lambda x,y : x._data(y)
        self.items_call(fun,context,'_data')

    def _check(self,context):
        fun = lambda x,y : x._check(y)
        self.items_call(fun,context,'_check')

    def _reload(self,context):
        fun = lambda x,y : x._reload(y)
        self.items_call(fun,context,'_reload')

    def _clean(self,context):
        fun = lambda x,y : x._clean(y)
        self.items_call(fun,context,'_clean')

    def _info(self,context):
        fun = lambda x,y : x._info(y)
        self.items_call(fun,context,'_info')

    def _allow(self,context):
        return True
    def append(self,item):
        if not hasattr(self,'_res') :
            self._res = []
        self._res.append(item)
    def push(self,item):
        if not hasattr(self,'_res') :
            self._res = []
        self._res.insert(0,item)


    def _check_print(self,is_true,msg):
        print(msg)

    def _resname(self):
        tag = self.__class__.__name__
        return tag

class resource (controlable,rg_conf.base):
    allow_res   = "ALL"
    def _allow(self,context):
        allowd =  self.allow_res == "ALL"  or self.allow_res == self.clsname()
        if allowd:
            rg_logger.debug( "allowd resource %s ,current resouce is %s " %(self.allow_res,self._resname()))
        return  allowd

    def _check_print(self,is_true,msg):
        if is_true:
            print( "\t%-100.100s%-20.20s-[Y]" % (msg ,self._resname())  )
        else:
            print( "\t%-100.100s%-20.20s-[ ]" % (msg ,self._resname())  )
    def _resname(self):
        tag = self.__class__.__name__
        return tag
