#coding=utf-8

'''
ref https://segmentfault.com/a/1190000007495352
    
1. much cpu --- use multi process, not others
2. much io --- use multi process, not others
3. much net --- use multi thread first

what is different :
1. pure python code and python+c is different, in python+c thread pool is usefull


'''

from __future__ import print_function

import os
import requests
import time
from threading import Thread
from multiprocessing import Process
import unittest
import random
import inspect

g_task_count = 8
curpath = os.path.dirname(os.path.realpath(__file__))

def _work_much_cpu(*args,**kwargs):
    c = 0
    x = 1
    y = 1
    while c < 50000:
        c += 1
        x += x
        y += y


def _work_much_io(*args,**kwargs):
    while 1:
        # multi thread/process not same name
        pw = os.path.join(curpath,'test_{}.txt'.format(random.randint(0,100)))
        if not os.path.exists(pw):
            break

    with open(pw,'w') as fw:
        for _ in range(5000000):
            fw.write('testwrite\n')

    c = []
    with open(pw, 'r') as fr:
        c.extend(fr)
    os.remove(pw)


def _work_much_net(*args,**kwargs):
    def _f():
        url = 'https://tieba.baidu.com/'
        try:
            response = requests.get(url)
            c = response.content
            return {'content': c}
        except Exception as er:
            return {'error': er}

    for _ in range(3):
        _f()



def _threading_thread_framework(target,args):

    ts = []

    for _ in range(g_task_count):
        th = Thread(target=target,args=args)
        ts.append(th)
        th.start()

    is_all_thread_exit = False
    while not is_all_thread_exit:
        is_all_thread_exit = True
        for th in ts:
            if th.is_alive(): # join ?
                is_all_thread_exit = False


def _multiprocessing_process_framework(target, args):
    ts = []
    for _ in range(g_task_count):
        th = Process(target=target, args=args)
        ts.append(th)
        th.start()

    is_all_thread_exit = False
    while not is_all_thread_exit:
        is_all_thread_exit = True
        for th in ts:
            if th.is_alive():
                is_all_thread_exit = False


def _futures_threadpool_framework(func,iterable):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=g_task_count) as pool:
        r = pool.map(func,iterable)
        pool.shutdown(wait=True)
        return list(r)


def _multiprocessing_threadpool_framework(func, iterable):
    from multiprocessing.pool import ThreadPool
    pl = ThreadPool(processes=g_task_count)
    return pl.map(func,iterable)


class Profile(object):
    def __init__(self):
        self._test_method = inspect.stack()[1][3]

    def execute(self, func, *args, **kwargs):
        times = []
        for _ in range(kwargs.pop('execute_count',1)):
            t = time.clock()
            func(*args,**kwargs)
            times.append(time.clock()-t)

        import sys
        print('{} {} {}'.format(self._test_method, func.__name__, map(lambda e : '{:.3f}'.format(e),times)))
        sys.stdout.flush()




class MyTestCase(unittest.TestCase):

    def test_profile_line(self):
        t = Profile()

        for fn in (_work_much_cpu,_work_much_io,_work_much_net):
            f = lambda: [fn() for _ in range(g_task_count)]
            f.__name__ = fn.__name__
            t.execute(f)

        print('')
        print('')

    def test_threading_thread(self):
        t = Profile()

        for fn in (_work_much_cpu,_work_much_io,_work_much_net):
            t.execute(_threading_thread_framework,fn, ())
        print('')
        print('')

    def test_multiprocessing_process(self):
        t = Profile()

        for fn in (_work_much_cpu,_work_much_io,_work_much_net):
            t.execute(_multiprocessing_process_framework,fn, ())

        print('')
        print('')

    def test_concurrent_futures_threadpool(self):
        t = Profile()
        for fn in (_work_much_cpu,_work_much_io,_work_much_net):
            t.execute(_futures_threadpool_framework,fn, range(g_task_count))
        print('')
        print('')

    def test_multiprocessing_threadpool(self):
        t = Profile()
        for fn in (_work_much_cpu, _work_much_io, _work_much_net):
            t.execute(_multiprocessing_threadpool_framework, fn, range(g_task_count))

        print('')
        print('')


    def python_call_c_line(self):
        from functools import partial
        t = Profile()
        f = lambda *args,**kwargs :map(*args,**kwargs)
        f.__name__='python_call_c_map'
        t.execute(f,partial(_thread_func,_get_obj()),_get_data(),execute_count=1)

    def python_call_c_threadpool(self):
        ''' 提升效果显著 '''
        import io_in_out
        t = Profile()

        t.execute(io_in_out.io_thread_map_one_ins,execute_count=1
                  , thread_data=_get_data()
                  , ins_generator_func=_get_obj
                  , thread_func=_thread_func
                  , max_workers = g_task_count)

def _get_obj():
    '''
    only use by my self    
    '''
    # c instance
    pass

def _get_data():
    '''
    only use by my self    
    '''
    import io_in_out
    p=r'samples'
    p = io_in_out.io_in_arg(p)
    return io_in_out.io_iter_files_from_arg([p])

def _thread_func(obj,data):
    '''
    only use by my self    
    '''
    pass



if __name__ == '__main__':
    unittest.main()


'''
The old output

profile_line cpu [u'40.586', u'40.518', u'40.489']
profile_line io [u'33.595', u'33.665', u'34.732']
profile_line net [u'10.420', u'10.286', u'9.987']

profile_threading_thread cpu [u'46.130', u'42.408', u'42.596']
profile_threading_thread io [u'204.598', u'200.775', u'201.306']
profile_threading_thread net [u'1.159', u'1.161', u'1.174']

profile_multiprocessing_process cpu [u'11.869', u'12.523', u'11.826']
profile_multiprocessing_process io [u'10.708', u'10.632', u'10.578']
profile_multiprocessing_process net [u'1.601', u'1.666', u'1.576']

profile_futures_threadpool cpu [u'42.381', u'42.600', u'42.425']
profile_futures_threadpool io [u'185.027', u'181.874', u'181.583']
profile_futures_threadpool net [u'1.328', u'1.564', u'1.406']

profile_python_c_line io [u'6.413']

profile_python_c_threadpool io [u'1.962']
'''