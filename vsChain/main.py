from gen_data import gen_data
import owner
import server
import round
import binSearchTree
from web3 import Web3
import json
import experiment


################################## 连接区块链 ######################################
ganache_url = "ws://127.0.0.1:8545"
web3 = Web3(Web3.WebsocketProvider(ganache_url, websocket_kwargs={'timeout': 2400}))
contract_address='0xC6E64bC0A06e701e649fE9a432C7FB8712E36152'
json_file='./contract/build/contracts/Merkle.json'
abi=None
with open(json_file,'r') as f:
    contract_json =json.load(f)
    abi=contract_json['abi']

contract=web3.eth.contract(address=contract_address,abi=abi)


####################################### 数据集 ##################################
# 小数据集
# dataset = {'w1':{1,2}, 'w2':{2,3}, 'w3':{1,3}}
# Q = {'w1'}

# 中数据集
# dataset = {'w1':{1,2,3,4,5}, 'w2':{1,3,5,6,8}, 'w3':{2,4,7,8,9}, 'w4':{3,4,6,7,8}, 'w5':{1,3,7,9,10}}
# Q={'w1','w2','w3','w4','w5'}

# 大数据集
# dataset = gen_data(20,1000)
# Q = {'w1','w3','w4','w5'}


################################ 业务代码 for 中数据集 ##################################
# setup
# client = owner.onwer(web3, contract)
# csp = server.server(web3, contract)
# CMAP = client.setup(dataset)
# csp.CMAP = CMAP

# token = client.gen_token(Q)
# round_list, merkle_proof = csp.search(token)
# client.verify(round_list, merkle_proof)

# update
# k,v = client.update('w1', 8)
# csp.CMAP[k]=v
# k,v=client.update('w3', 3)
# csp.CMAP[k]=v

# search
# token = client.gen_token(Q)
# round_list, merkle_proof = csp.search(token)
# client.verify(round_list, merkle_proof)

# k,v = client.update('w4', 1)
# csp.CMAP[k]=v
# k,v=client.update('w5', 8)
# csp.CMAP[k]=v

# token = client.gen_token(Q)
# round_list, merkle_proof = csp.search(token)
# client.verify(round_list, merkle_proof)


################################ 业务代码 for 中数据集 ##################################
# # setup
# client = owner.onwer(web3, contract)
# csp = server.server(web3, contract)
# CMAP = client.setup(dataset)
# csp.CMAP = CMAP

# token = client.gen_token(Q)
# round_list, merkle_proof = csp.search(token)
# client.verify(round_list, merkle_proof)

# # update
# k,v = client.update('w1', 10001)
# csp.CMAP[k]=v
# k,v=client.update('w3', 10001)
# csp.CMAP[k]=v

# # search
# token = client.gen_token(Q)
# round_list, merkle_proof = csp.search(token)
# client.verify(round_list, merkle_proof)

# k,v = client.update('w1', 10002)
# csp.CMAP[k]=v
# k,v=client.update('w3', 10002)
# csp.CMAP[k]=v
# k,v = client.update('w4', 10001)
# csp.CMAP[k]=v
# k,v=client.update('w5', 10001)
# csp.CMAP[k]=v

# token = client.gen_token(Q)
# round_list, merkle_proof = csp.search(token)
# client.verify(round_list, merkle_proof)



############################## 实验 #########################
###########################   测试Setup ###################
# 100K file, 50 w
# experiment.test_setup("../dataset/inv_100K_file_50_w.dat", web3, contract)
# 100K file, 100 w
# experiment.test_setup("../dataset/inv_100K_file_100_w.dat", web3, contract)
# 100K file, 150 w
# experiment.test_setup("../dataset/inv_100K_file_150_w.dat", web3, contract)
# 100K file, 200 w
# experiment.test_setup("../dataset/inv_100K_file_200_w.dat", web3, contract)
# 100K file, 250 w
# experiment.test_setup("../dataset/inv_100K_file_250_w.dat", web3, contract)

# 20K file, 200 w
# experiment.test_setup("../dataset/inv_20K_file_200_w.dat", web3, contract)
# 40K file, 200 w
# experiment.test_setup("../dataset/inv_40K_file_200_w.dat", web3, contract)
# 60K file, 200 w
# experiment.test_setup("../dataset/inv_60K_file_200_w.dat", web3, contract)
# 80K file, 200 w
# experiment.test_setup("../dataset/inv_80K_file_200_w.dat", web3, contract)

############################## 测试search #######################################
# 100K file, 200w, w1~w10匹配前1K文件，搜索随机的2/4/6/8/10个w
# experiment.test_search1("../dataset/inv_100K_file_200_w_1000.dat", 2, web3, contract)


# 100K file, 200 w, w1匹配前200文件，搜索10个w
# experiment.test_search2("../dataset/inv_100K_file_200_w_200.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前400文件，搜索10个w
# experiment.test_search2("../dataset/inv_100K_file_200_w_400.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前600文件，搜索10个w
# experiment.test_search2("../dataset/inv_100K_file_200_w_600.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前800文件，搜索10个w
# experiment.test_search2("../dataset/inv_100K_file_200_w_800.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前1000文件，搜索10个w
# experiment.test_search2("../dataset/inv_100K_file_200_w_1000.dat", 10, web3, contract)


################################ 测试update #######################################
# 100K file, 200 w, 更新100K w-id pair
# experiment.test_update("../dataset/inv_100K_file_200_w.dat", "../dataset/inv_upd_100K.dat", web3, contract)
# 100K file, 200 w, 更新200K w-id pair
experiment.test_update("../dataset/inv_100K_file_200_w.dat", "../dataset/inv_upd_200K.dat", web3, contract)
# 100K file, 200 w, 更新300K w-id pair
# experiment.test_update("../dataset/inv_100K_file_200_w.dat", "../dataset/inv_upd_300K.dat", web3, contract)
# 100K file, 200 w, 更新400K w-id pair
# experiment.test_update("../dataset/inv_100K_file_200_w.dat", "../dataset/inv_upd_400K.dat", web3, contract)
# 100K file, 200 w, 更新500K w-id pair
# experiment.test_update("../dataset/inv_100K_file_200_w.dat", "../dataset/inv_upd_500K.dat", web3, contract)