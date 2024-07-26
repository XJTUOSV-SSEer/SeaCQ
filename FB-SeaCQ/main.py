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
contract_address='0xEc7BDab99585fb8dF55C0B8Cf71289Ca8c41D0a6'
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
# Q={'w1'}


# 中数据集
# dataset={'f1':{'w1','w2','w3','w4'}, 'f2':{'w1','w3','w5','w6'}, 'f3':{'w2','w3','w5','w7'}, 
#         'f4':{'w1','w2','w4','w6','w7'}}
# Q={'w2','w3'}
# Q={'w6','w4','w1','w3'}
# Q={'w4','w3','w2','w1'}
# Q={'w6','w4','w1','w7'}


# 大数据集
dataset=experiment.gen_dataset(1,5000)
Q={'1'}
# print(dataset)
print("generate dataset")


###################### 静态 ##############################################
# # owner setup
start_time = time.time()
k1,k2,index1,index2,ST,gas=owner.setup(dataset,web3,contract)
end_time = time.time()
print("setup time cost:", end_time - start_time, "s")
print("setup finish")

# user search
# 生成token
w, t_w,P_Q,st=owner.search(Q,ST,k1)
print("tokengen finish")

# server搜索并返回结果
start_time = time.time()
result=server.search(t_w,P_Q,st,index1,index2)
end_time = time.time()
print("search time cost:", end_time - start_time, "s")
print("search finish")

# user验证
start_time = time.time()
flag,R=owner.verify(w,P_Q,result, web3,contract,k2)
end_time = time.time()
print("verify time cost:", end_time - start_time, "s")
# print(w)
print(flag)
# print(R)


###################### add ##############################################

# add (w,fid)
# dataset=experiment.gen_dataset(5,5)
# Q={'1','2'}
# k1,k2,index1,index2,ST,gas=owner.setup(dataset,web3,contract)

# updtk_add=owner.update(ST, 'add', 'w2', 'f2', index2, web3, contract)
# server.update('add', updtk_add, index1, index2)

# # 再次搜索
# w, t_w,P_Q,st=owner.search(Q,ST,k1)
# result=server.search(t_w,P_Q,st,index1,index2)
# flag,R=owner.verify(w,P_Q,result, web3,contract,k2)
# print(flag)
# print(R)


###################### del ##############################################
# dataset={'f1':{'w1','w2','w3','w4'}, 'f2':{'w1','w3','w5','w6'}, 'f3':{'w2','w3','w5','w7'}, 
#         'f4':{'w1','w2','w4','w6','w7'}}
# Q={'w1','w2','w3'}


# k1,k2,index1,index2,ST,gas=owner.setup(dataset,web3,contract)

# 先add再del
# updtk_add=owner.update(ST, 'add', 'w3', 'f4', index2, web3, contract)
# server.update('add', updtk_add, index1, index2)
# updtk_del=owner.update(ST, 'del', 'w2', 'f1', index2, web3, contract)
# server.update('del', updtk_del, index1, index2)

# 再次搜索
# w, t_w,P_Q,st=owner.search(Q,ST,k1)
# result=server.search(t_w,P_Q,st,index1,index2)
# flag,R=owner.verify(w,P_Q,result, web3,contract,k2)
# print(flag)
# print(R)