import math
from sympy import factorint
import sys 
import mpire
import mpire
import os
os.environ["OMP_NUM_THREADS"] = "1"
import time
import multiprocessing 
from mpire import WorkerPool
from pprint import pprint
import itertools
num_cores =max(multiprocessing.cpu_count()//2,1)
import shutil
import random
from multiprocessing import Manager

sys.set_int_max_str_digits(10**9)

def transform(arr):
    rv = []
    for i in range(len(arr)-1):
        if arr[i] != "":
            rv.append(arr[i]+arr[i+1][0])
            arr[i+1] = arr[i+1][1:]
    rv.append(arr[-1])
    rv = [r for r in rv if r!='']
    n = len(rv)
    if n==1:
        x = rv[n-1]
        rv = split_chunks_again(x)
    rv = [r for r in rv if r!='']
    
    return rv

def split_chunks_again(string):
    
    chunks = []
    rv_str = ""
    for i in range(len(string)):
        if int(i)%2 == 0 and int(string[i]) != 0:
            chunks.append(rv_str)
            rv_str = string[i] 
            
        else:
            rv_str += string[i]
    chunks.append(rv_str)
    chunks = [int(c) for c in chunks if c != ""]
    return chunks

def split_chunks(string):
    chunks = []
    rv_str = ""
    for i in range(len(string)):
        if int(string[i])%2 == 0 and int(string[i]) != 0:
            chunks.append(rv_str)
            rv_str = string[i] 
            
        else:
            rv_str += string[i]
    chunks.append(rv_str)
    chunks = transform(chunks)
    chunks = [int(c) for c in chunks if c != ""]
    return chunks


def smart_factor(n):
    chunks = split_chunks(str(n))
    for c in chunks:
        g = math.gcd(n, c)
        if g>1 and g<n:
            my_dict = {g:1,n//g:1}
            return my_dict
    return {n:1}

def smart_factor_for_parallel_chunks(n,chunks):
    for c in chunks:
        g = math.gcd(n, c)
        if g>1 and g<n:
            my_dict = {g:1,n//g:1}
            return my_dict
    return {n:1}


def smart_parallel_factor(n,c):
    chunks = split_chunks(str(n))
    for c in chunks:
        g = math.gcd(n, c)
        if g>1 and g<n:
            my_dict = {g:1,n//g:1}
            return my_dict
    return {n:1}



def parallel_factor(n):
    c = split_chunks(str(n))
    results = [{"n" : int(x), "c" : c} for x in split_chunks(str(n))]
    with WorkerPool(n_jobs=num_cores,daemon=False) as pool:
        results = pool.map(smart_parallel_factor, results, progress_bar=False)
    return results


    
def parallel_temp_dict_factor(item, shared_dict):
    factors = factorint(item["item"])
    
    for f, exp in factors.items():
        if f in shared_dict:
            shared_dict[f] += exp
        else:
            shared_dict[f] = exp
    
def parallel_for_loop_factor(n):
    results = parallel_factor(n)
    chunks = []
    for my_dict in results:
        chunks.extend(my_dict.keys())

    temp_dict = smart_factor_for_parallel_chunks(n,chunks)
    items = [{"item": k} for k in list(temp_dict.keys())]
    with Manager() as manager:
        shared_dict = manager.dict()  # 🧠 shared memory

        with WorkerPool(n_jobs=num_cores, daemon=False) as pool:
            pool.map(
                parallel_temp_dict_factor,
                [(item, shared_dict) for item in items],
                progress_bar=False
            )

        # Convert back to normal dict
        final = dict(shared_dict)
    return final
  

def for_loop_factor(n):
    temp_dict = smart_factor(n)
    rv = {}
    for k,v in temp_dict.items():
        factors = factorint(k)
        for f, exp in factors.items():
            if f in rv:
                rv[f] += exp
            else:
                rv[f] = exp
    return rv
    

# if __name__ == "__main__":
    # string = "4"
    # print(string)
    # out = parallel_for_loop_factor(int(string))
    # print(f"Factors of {string} using for loop: {out}")

    # string = "2"*200
    # print(len(string))
    # fast_out = parallel_for_loop_factor(int(string))
    # print(f"Factors of {string} using parallel for loop: {fast_out}")

    # length = 100
    # string = ""
    # for i in range(1, length+1):
    #     string += str(random.randint(1,9))
    # n=len(string)
    # if int(string[n-1])%2==1:
    #     string = string[:-1] + "2"
    # print(string)
    # print(len(string))
    # fast_out = parallel_for_loop_factor(int(string))
    # print(f"Factors of {string} using parallel for loop: {fast_out}")

    '''
    length = 100
    string = ""
    for i in range(1, length+1):
        string += str(9)
    n=len(string)
    if int(string[n-1])%2==1:
        string = string[:-1] + "2"
    print(string)
    print(len(string))
    fast_out = parallel_for_loop_factor(int(string))
    print(f"Factors of {string} using parallel for loop: {fast_out}")
    '''
