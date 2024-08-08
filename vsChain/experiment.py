import hmac
import pickle
import random
import time
import owner
import server
from typing import Dict, Set, Tuple


def test_setup(file_name, web3, contract):
    '''
    测试setup性能
    input:
        file_name: 数据集的文件名，相对路径
    '''

    dataset = None
    with open (file_name, 'rb') as f: #打开文件
        dataset = pickle.load(f)

    client = owner.onwer(web3, contract)
    csp = server.server(web3, contract)
    CMAP, t1, t2, t3, gas = client.setup(dataset)
    csp.CMAP = CMAP

    print("index construction time:", t1)
    print("ADS generation time:", t2)
    print("transaction time:", t3)
    print("Gas Used:", gas)



def test_search1(file_name:str, q_num:int, web3, contract):
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
    client = owner.onwer(web3, contract)
    csp = server.server(web3, contract)
    CMAP, _, _, _, _ = client.setup(dataset)
    csp.CMAP = CMAP


    # 分别查询2/4/6/8/10个关键字
    for q_num in range(2,12,2):
        # 查询条件Q
        Q=set()
        for i in range(1, q_num+1):
            Q.add('w'+str(random.randint(1,999)))

        token = client.gen_token(Q)
        round_list, merkle_proof, t_find_result, t_gen_vo, _, _, _ = csp.search(token)
        _, _, t_verify = client.verify(round_list, merkle_proof)
        print("find result:", t_find_result)
        print("generate VO:", t_gen_vo)
        print("verify:", t_verify)



def test_search2(file_name:str, q_num:int, web3, contract):
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
    client = owner.onwer(web3, contract)
    csp = server.server(web3, contract)
    CMAP, _, _, _, _ = client.setup(dataset)
    csp.CMAP = CMAP

    # 查询条件Q
    Q=set()
    for i in range(1, q_num+1):
        Q.add('w'+str(i))

    token = client.gen_token(Q)
    round_list, merkle_proof, t_find_result, t_gen_vo, _, _, _ = csp.search(token)
    _, _, t_verify = client.verify(round_list, merkle_proof)
    print("find result:", t_find_result)
    print("generate VO:", t_gen_vo)
    print("verify:", t_verify)





def test_update(dataset_name:str, update_dataset_name:str, web3, contract):
    '''
    首先根据dataset_name构建数据库，然后将update_dataset_name中的数据add。
    之后，搜索所有add的关键字，测试服务器端的ADS generate time，transact time，gas
    '''

    dataset = None
    with open (dataset_name, 'rb') as f: #打开文件
        dataset = pickle.load(f)
    
    # setup
    client = owner.onwer(web3, contract)
    csp = server.server(web3, contract)
    CMAP, _, _, _, _ = client.setup(dataset)
    csp.CMAP = CMAP

    # update
    with open (update_dataset_name, 'rb') as f: #打开文件
        upd_dataset:Dict[str, Set[int]] = pickle.load(f)
    
    # gas花费
    gas = 0
    t_transact1 = 0

    t1_s = time.time()
    for w, id_set in upd_dataset.items():
        for id in id_set:
            k,v = client.update(w, id)
            csp.CMAP[k]=v

        t2_s = time.time()
        # 当对这个关键字的所有更新处理结束后，将w对应的H_w_upd上传
        k1='XJTUOSV1'.zfill(16).encode('utf-8')
        alpha, beta, H_w_upd, flag = client.DMAP[w]
        tau_w_upd = hmac.new(key=k1, msg= (w.zfill(16)+str(alpha).zfill(16)).encode('utf-8'), digestmod='sha256').digest()
        tx_hash = contract.functions.set_UMAP(tau_w_upd, H_w_upd).transact({
            'from':web3.eth.accounts[0], 
            'gasPrice': web3.eth.gasPrice, 
            'gas': 3000000000})

        # gas消耗
        tx_receipt = web3.eth.get_transaction_receipt(tx_hash)
        gas_0 = tx_receipt['gasUsed']
        gas = gas+gas_0

        t2_e = time.time()
        t_transact1 = t_transact1 + t2_e - t2_s
            
    t1_e = time.time()
    print("index construct time:", t1_e - t1_s - t_transact1)

    # 对更新的所有w进行搜索，从而将本批次更新的内容写入区块链
    Q=set()
    for w, id_set in upd_dataset.items():
        Q.add(w)
    
    token = client.gen_token(Q)
    round_list, merkle_proof, _, _, t_gen_ADS, t_transact2, gas_1 = csp.search(token)
    gas = gas+gas_1

    t_transact = t_transact1 + t_transact2

    print("ADS generation time:", t_gen_ADS)
    print("transaction time:", t_transact)
    print("Gas Used:", gas)
