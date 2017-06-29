#coding=utf-8
import os
import sys
import unittest
import time
import random

g_task_count = 16

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

def _futures_threadpool_framework2(func,iterable):
    ''' result is order of completion '''

    from concurrent.futures import ThreadPoolExecutor
    from concurrent.futures import as_completed
    with ThreadPoolExecutor(max_workers=g_task_count) as executor:
        futs = [executor.submit(func,i) for i in iterable]
        return [fut.result() for fut in as_completed(futs)]



def _thread_func_compare_concurrent_multiprocessing(arg):
    time.sleep(arg[u'value'])
    return arg


def format_iterable(l):
    return [ u'{}:{}'.format(v[u'index'],v[u'value'])  for v in l ]

class MyTestCase(unittest.TestCase):

    def test_compare_concurrent_multiprocessing(self):
        iterable = [random.randint(0,7) for _ in range(g_task_count)]
        iterable = [{u'index':i, u'value':v} for i,v in enumerate(iterable)]

        print(u'data {}'.format(format_iterable(iterable)))

        t= time.clock()
        r1 = _futures_threadpool_framework(_thread_func_compare_concurrent_multiprocessing
                                          , iterable)
        t1 = time.clock()-t

        print(u'result of futures_threadpool {} {}'.format(t1,format_iterable(r1)))

        t = time.clock()
        r2 = _multiprocessing_threadpool_framework(_thread_func_compare_concurrent_multiprocessing
                                                   , iterable)
        t2 = time.clock()-t

        print(u'result of multiprocess threadpool {} {}'.format(t2,format_iterable(r2)))

        t = time.clock()
        r3 = _futures_threadpool_framework2(_thread_func_compare_concurrent_multiprocessing
                                                   , iterable)
        t3 = time.clock() - t

        print(u'result of futures_threadpool2  {} {}'.format(t3, format_iterable(r3)))


        self.assertEqual(int(t1),int(t2))
        self.assertEqual(int(t1),max((v[u'value'] for v in iterable)))

        self.assertEqual(r1,r2)
        self.assertEqual(r1,iterable)






if __name__ == '__main__':
    unittest.main()