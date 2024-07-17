from web3 import Web3
import json
import owner

########################## 连接到区块链网络 #########################
# ganache网络
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

########################### 加载合约地址和ABI ############################
# 合约地址
contract_address='0xEa5031B83bCECA32c6443f3D6CCe87a4Cb10cfD6'
# 从json文件中读取abi
json_file='./contract/build/contracts/ADS.json'
abi=None
with open(json_file,'r') as f:
    contract_json =json.load(f)
    abi=contract_json['abi']

############################ 生成合约账户 ##############################
contract=web3.eth.contract(address=contract_address,abi=abi)


############################ 业务代码 ###################################
# 数据集
dataset={'f1':{'w1','w2'}, 'f2':{'w2','w3'}}

# owner setup
k1,k2,index1,index2,ST,gas=owner.setup(dataset,web3,contract)
print(index2)
print(gas)
