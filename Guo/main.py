import ICC20
from web3 import Web3
import json
import experiment



################################## 连接区块链 ######################################
ganache_url = "ws://127.0.0.1:8545"
web3 = Web3(Web3.WebsocketProvider(ganache_url, websocket_kwargs={'timeout': 2400}))
contract_address='0xc6797953D4f9CF34F8BD1A8DA0982Fe5D7bb03Df'
json_file='./contract/build/contracts/write.json'
abi=None
with open(json_file,'r') as f:
    contract_json =json.load(f)
    abi=contract_json['abi']

contract=web3.eth.contract(address=contract_address,abi=abi)


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
# # 100K file, 200w, w1~w10匹配前1K文件，搜索2个w
# experiment.test_search("../dataset/inv_100K_file_200_w_1000.dat", 2, web3, contract)
# # 100K file, 200w, w1~w10匹配前1K文件，搜索4个w
# experiment.test_search("../dataset/inv_100K_file_200_w_1000.dat", 4, web3, contract)
# # 100K file, 200w, w1~w10匹配前1K文件，搜索6个w
# experiment.test_search("../dataset/inv_100K_file_200_w_1000.dat", 6, web3, contract)
# # 100K file, 200w, w1~w10匹配前1K文件，搜索8个w
# experiment.test_search("../dataset/inv_100K_file_200_w_1000.dat", 8, web3, contract)
# # 100K file, 200w, w1~w10匹配前1K文件，搜索10个w
# experiment.test_search("../dataset/inv_100K_file_200_w_1000.dat", 10, web3, contract)

# 100K file, 200 w, w1匹配前200文件，搜索10个w
# experiment.test_search("../dataset/inv_100K_file_200_w_200.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前400文件，搜索10个w
# experiment.test_search("../dataset/inv_100K_file_200_w_400.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前600文件，搜索10个w
# experiment.test_search("../dataset/inv_100K_file_200_w_600.dat", 10, web3, contract)
# 100K file, 200 w, w1匹配前800文件，搜索10个w
# experiment.test_search("../dataset/inv_100K_file_200_w_800.dat", 10, web3, contract)


################################ 测试update #######################################
experiment.test_setup("../dataset/inv_100K_file_200_w.dat", web3, contract)
# 100K file, 200 w, 更新100K w-id pair
# 100K file, 200 w, 更新100K w-id pair
experiment.test_update("../dataset/inv_upd_100K.dat", web3, contract)
# 100K file, 200 w, 更新200K w-id pair
experiment.test_update("../dataset/inv_upd_200K.dat", web3, contract)
# 100K file, 200 w, 更新300K w-id pair
experiment.test_update("../dataset/inv_upd_300K.dat", web3, contract)
# 100K file, 200 w, 更新400K w-id pair
experiment.test_update("../dataset/inv_upd_400K.dat", web3, contract)
# 100K file, 200 w, 更新500K w-id pair
experiment.test_update("../dataset/inv_upd_500K.dat", web3, contract)