import pickle
import random
import time
import owner
import server
from typing import Dict, Set, Tuple

def gen_dataset(w_num:int, fid_num:int):
    '''
    (弃用)
    生成数据集，数据集的形式为文件。
    首先生成w_num个倒排索引，每个关键字对应的fid数为fid_num。
    然后将倒排索引转换为文件的形式。
    input:
        w_num - 关键字数
        fid_num - 每个关键字对应的文件数
    output:
        dataset - 数据集。Dict类型。key为文件id，字符串类型。value为文件中的关键字集合，集合中元素为字符串类型。
    '''

    # 数据集
    dataset=dict()

    for w in range(1,w_num+1):
        # 生成fid_num个随机的文件id，且取值范围为[1,10*fid_num]
        # fid_list=[random.randint(1, 1+10*fid_num) for _ in range(fid_num)]
        fid_list=random.sample(range(1, 1+10*fid_num), fid_num)

        # 将这些(w, fid)加入数据集
        for fid in fid_list:
            # 若该文件还不存在，增加k-v pair
            if str(fid) not in dataset:
                dataset[str(fid)]=set()
            # 将w加入fid对应的集合中
            dataset[str(fid)].add(str(w))
    
    return dataset



def test_setup(file_name, web3, contract):
    '''
    测试setup性能
    input:
        file_name: 数据集的文件名，相对路径
    '''

    dataset = None
    with open (file_name, 'rb') as f: #打开文件
        dataset = pickle.load(f)
    

    # t1 - index construction time
    # t2 - ADS generation time
    # t3 - transaction time
    k1,k2,index1,index2,ST,gas, t1, t2, t3=owner.setup(dataset,web3,contract)

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

    # setup 
    k1,k2,index1,index2,ST,gas, _, _, _=owner.setup(dataset,web3,contract)

    for q_num in range(2,12,2):
        
        # 查询条件Q
        Q=set()
        for i in range(1, q_num+1):
            Q.add('w'+str(i))

        # search
        # 限制查询的w为w1
        w = None
        while w != 'w1':
            w, t_w,P_Q,c=owner.search(Q,ST,k1)
        
        result, t_find_result, t_gen_vo=server.search(t_w,P_Q,c,index1,index2)
        flag, R, t_verify = owner.verify(w,P_Q,result, web3,contract,k2)
        print("find result:", t_find_result)
        print("generate VO:", t_gen_vo)
        print("verify:", t_verify)
        print(flag)
        print(len(R))