import imp
import time
from web3 import Web3
import json
import owner
import server
import experiment



########################## 连接到区块链网络 #########################
# ganache网络
ganache_url = "ws://127.0.0.1:8545"
web3 = Web3(Web3.WebsocketProvider(ganache_url, websocket_kwargs={'timeout': 360}))

########################### 加载合约地址和ABI ############################
# 合约地址
contract_address='0x62FdAc849501A7C648a44963238395FA692E8843'
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


# dataset={'f1':{'w1','w2','w3','w4'}, 'f2':{'w1','w3','w4', 'w5','w6'}, 'f3':{'w2','w3','w5','w7'}, 
#         'f4':{'w1','w2','w4','w6','w7'}}
# Q={'w1','w4'}

# dataset=experiment.gen_dataset(1, 5000)
# Q={'1'}



# 查询
# start_time = time.time()
# k1, k2, index1, index2, index3, P, ST, gas=owner.setup(dataset,web3,contract)
# end_time = time.time()
# print("setup time cost:", end_time - start_time, "s")
# print("setup gas cost:", gas)
# print("setup finish")


# updtk=owner.update(ST, 'add', '2','3', index2, index3, web3, contract)
# P = server.update('add', updtk,index1, index2, index3)
# updtk=owner.update(ST, 'del', 'w4', 'f2', index2, index3, web3, contract)
# P=server.update('del', updtk, index1, index2, index3)


# w, t_w,P_Q,st=owner.search(Q,ST,k1)

# start_time = time.time()
# correctness_proof, pi4 = server.search(t_w, P_Q, st, index1, index2, index3, P)
# end_time = time.time()
# print("search time cost:", end_time - start_time, "s")
# print("search finish")

# start_time = time.time()
# flag,R=owner.verify(w, P_Q, correctness_proof, pi4, web3,contract,k2)
# end_time = time.time()
# print("verify time cost:", end_time - start_time, "s")
# print(flag)
# print(len(R))



############################## 实验 #########################
###########################   测试Setup ###################
# 100K file, 50 w
# experiment.test_setup("../dataset/100K_file_50_w.dat", web3, contract)
# 100K file, 100 w
# experiment.test_setup("../dataset/100K_file_100_w.dat", web3, contract)
# 100K file, 150 w
# experiment.test_setup("../dataset/100K_file_150_w.dat", web3, contract)
# 100K file, 200 w
# experiment.test_setup("../dataset/100K_file_200_w.dat", web3, contract)
# 100K file, 250 w
# experiment.test_setup("../dataset/100K_file_250_w.dat", web3, contract)

# 20K file, 200 w
# experiment.test_setup("../dataset/20K_file_200_w.dat", web3, contract)
# 40K file, 200 w
# experiment.test_setup("../dataset/40K_file_200_w.dat", web3, contract)
# 60K file, 200 w
# experiment.test_setup("../dataset/60K_file_200_w.dat", web3, contract)
# 80K file, 200 w
# experiment.test_setup("../dataset/80K_file_200_w.dat", web3, contract)

############################## 测试search #######################################
# 100K file, 200w, w1~w10匹配前1K文件，搜索2/4/6/8/10个w
# experiment.test_search("../dataset/100K_file_200_w_1000.dat", 2, web3, contract)

# 100K file, 200 w, w1匹配前200文件，搜索10个w
experiment.test_search("../dataset/100K_file_200_w_200.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前400文件，搜索10个w
experiment.test_search("../dataset/100K_file_200_w_400.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前600文件，搜索10个w
experiment.test_search("../dataset/100K_file_200_w_600.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前800文件，搜索10个w
experiment.test_search("../dataset/100K_file_200_w_800.dat", 10, web3, contract)


################################ 测试update #######################################
experiment.test_setup("../dataset/100K_file_200_w.dat", web3, contract)
# 100K file, 200 w, 更新100K w-id pair
# 100K file, 200 w, 更新100K w-id pair
experiment.test_update("../dataset/upd_100K.dat", web3, contract)
# 100K file, 200 w, 更新200K w-id pair
experiment.test_update("../dataset/upd_200K.dat", web3, contract)
# 100K file, 200 w, 更新300K w-id pair
experiment.test_update("../dataset/upd_300K.dat", web3, contract)
# 100K file, 200 w, 更新400K w-id pair
experiment.test_update("../dataset/upd_400K.dat", web3, contract)
# 100K file, 200 w, 更新500K w-id pair
experiment.test_update("../dataset/upd_500K.dat", web3, contract)