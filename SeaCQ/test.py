from web3 import Web3
import json
from hexbytes import HexBytes

# 连接到区块链网络
# ganache网络
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# 加载合约地址和ABI
# 合约地址
contract_address='0xEa5031B83bCECA32c6443f3D6CCe87a4Cb10cfD6'
# 从json文件中读取abi
json_file='./contract/build/contracts/ADS.json'
abi=None
with open(json_file,'r') as f:
    contract_json =json.load(f)
    abi=contract_json['abi']

# 生成合约账户
contract=web3.eth.contract(address=contract_address,abi=abi)

# 要传递的数据
w1 = 'a'.zfill(16)
n1=123813810293102398102938102381029381029381020230238947293842309802938
w2='b'.zfill(16)
n2=13012983012938487394571823019230129802482095820984230994820348230809219
w3='c'.zfill(16)
n3=int(n1)*int(n2)

w_list=[Web3.toBytes(text=w1),Web3.toBytes(text=w2)]
v_list=[Web3.toBytes(int(n1)),Web3.toBytes(int(n2))]




# 调用智能合约
contract.functions.batch_setADS(w_list,v_list,2).transact(
    {'from':web3.eth.accounts[0], 
     'gasPrice': web3.eth.gasPrice, 
     'gas': web3.eth.getBlock('latest').gasLimit})

r=contract.functions.getADS(Web3.toBytes(text=w2)).call()
print(Web3.toInt(r))