from pydoc import cli
from gen_data import gen_data
import owner
import server
import round
import binSearchTree
from web3 import Web3
import json


################################## 连接区块链 ######################################
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
contract_address='0x84a4fF26D156985544C3D529333171732D847eBe'
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
dataset = gen_data(20,1000)
Q = {'w1','w3','w4','w5'}






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
# setup
client = owner.onwer(web3, contract)
csp = server.server(web3, contract)
CMAP = client.setup(dataset)
csp.CMAP = CMAP

token = client.gen_token(Q)
round_list, merkle_proof = csp.search(token)
client.verify(round_list, merkle_proof)

# update
k,v = client.update('w1', 10001)
csp.CMAP[k]=v
k,v=client.update('w3', 10001)
csp.CMAP[k]=v

# search
token = client.gen_token(Q)
round_list, merkle_proof = csp.search(token)
client.verify(round_list, merkle_proof)

k,v = client.update('w1', 10002)
csp.CMAP[k]=v
k,v=client.update('w3', 10002)
csp.CMAP[k]=v
k,v = client.update('w4', 10001)
csp.CMAP[k]=v
k,v=client.update('w5', 10001)
csp.CMAP[k]=v

token = client.gen_token(Q)
round_list, merkle_proof = csp.search(token)
client.verify(round_list, merkle_proof)