import pickle
import random
import time
import ICC20
from typing import Dict, Set, Tuple, List

def transform(dataset:Dict[str, Set[int]]):
    '''
    将从文件中读取的数据集进行转换，将id从int类型转换为str类型，并以列表形式存储。同时，每个list加入一个nonce，
    从而适应ICC20的接口
    '''
    for w, id_set in dataset.items():
        id_list:List[str] = []
        # 先加入一个nonce
        nonce=random.randint(-100000000000,10000000000)
        nonce=str(nonce).zfill(16)
        id_list.append(nonce)

        for id in id_set:
           id_list.append(str(id).zfill(16))
        dataset[w] = id_list


def test_setup(file_name, web3, contract):
    '''
    测试setup性能
    input:
        file_name: 数据集的文件名，相对路径。倒排索引形式，w为str类型，id为int类型。需要将id转换为str类型
    '''

    dataset = None
    with open (file_name, 'rb') as f: #打开文件
        dataset = pickle.load(f)
    transform(dataset)
    print("transform finished")

    server_index, blockchain_index, client_index, t1, t2, t3, gas = ICC20.Build_index(dataset, web3, contract)

    print("index construction time:", t1)
    print("ADS generation time:", t2)
    print("transaction time:", t3)
    print("Gas Used:", gas)


def test_search(file_name:str, q_num:int, web3, contract):
    '''
    测试搜索性能
    input:
        file_name - 数据集的文件名，相对路径
        q_num - join query的关键字数量
    '''

    dataset = None
    with open (file_name, 'rb') as f: #打开文件
        dataset = pickle.load(f)
    transform(dataset)
    print("transform finished")
    
    # setup
    server_index, blockchain_index, client_index, t1, t2, t3, gas = ICC20.Build_index(dataset, web3, contract)

    # 查询条件Q
    Q=set()
    for i in range(1, q_num+1):
        Q.add('w'+str(i))

    
    t_find_result = 0
    t_verify = 0

    for w in Q:
        # search
        Toekn_S_Addr, Toekn_S_Enc, Token_block, start_file_addr=ICC20.user_search_keyword_mutiple(client_index, w)
        list_search_file_ID=[]
        t1_s = time.time()
        results=ICC20.Server_search(Toekn_S_Addr,Toekn_S_Enc,start_file_addr,server_index,list_search_file_ID)
        t1_e = time.time()
        t_find_result = t_find_result+ t1_e-t1_s

        # verify
        t2_s = time.time()
        flag,gas=ICC20.verify(results,web3, contract, w)
        t2_e = time.time()
        t_verify = t_verify +t2_e - t2_s
        print(flag)
    


    print("find result:", t_find_result)
    # print("generate VO:", t_gen_vo)
    print("verify:", t_verify)





def test_update(update_dataset_name:str, web3, contract):
    '''
    用update_dataset_name中的数据进行setup即可模拟。
    '''

    test_setup(update_dataset_name, web3, contract)