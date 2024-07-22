import imp
import time
from web3 import Web3
import json
import owner
import server
import experiment



########################## 连接到区块链网络 #########################
# ganache网络
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

########################### 加载合约地址和ABI ############################
# 合约地址
contract_address='0x74C3385d5c2f1AfD865cbB1cae62518A2c8A9E42'
# 从json文件中读取abi
json_file='../contract/build/contracts/ADS.json'
abi=None
with open(json_file,'r') as f:
    contract_json =json.load(f)
    abi=contract_json['abi']

############################ 生成合约账户 ##############################
contract=web3.eth.contract(address=contract_address,abi=abi)

############################ 业务代码 ###################################
# # 小数据集
# dataset={'f1':{'w1','w2'}, 'f2':{'w2','w3'}}
# # 查询条件
# Q={'w4','w1'}


dataset={'f1':{'w1','w2','w3','w4'}, 'f2':{'w1','w3','w4', 'w5','w6'}, 'f3':{'w2','w3','w5','w7'}, 
        'f4':{'w1','w2','w4','w6','w7'}}
Q={'w1','w4'}

# dataset=experiment.gen_dataset(10,10)
# Q={'1','2'}



# 查询
k1, k2, index1, index2, index3, P, ST, gas=owner.setup(dataset,web3,contract)
# updtk=owner.update(ST, 'add', '2','3', index2, index3, web3, contract)
# P = server.update('add', updtk,index1, index2, index3)
updtk=owner.update(ST, 'del', 'w4', 'f2', index2, index3, web3, contract)
P=server.update('del', updtk, index1, index2, index3)
w, t_w,P_Q,st=owner.search(Q,ST,k1)
print(w)
correctness_proof, pi4 = server.search(t_w, P_Q, st, index1, index2, index3, P)
flag,R=owner.verify(w, P_Q, correctness_proof, pi4, web3,contract,k2)
print(flag)
print(R)