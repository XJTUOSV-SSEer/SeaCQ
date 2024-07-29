from pydoc import cli
from gen_data import gen_data
import owner
import server
import round
import binSearchTree


################################## 连接区块链 ######################################


####################################### 数据集 ##################################
# 小数据集
# dataset = {'w1':{1,2,}, 'w2':{2,3}, 'w3':{1,3}}
# Q = {'w1','w2','w3'}

# 中数据集
# dataset = {'w1':{1,2,3,4,5}, 'w2':{1,3,5,6,8}, 'w3':{2,4,7,8,9}, 'w4':{3,4,6,7,8}, 'w5':{1,3,7,9,10}}
# Q={'w1','w2','w3','w5'}

# 大数据集
dataset = gen_data(20,1000)
Q = {'w1','w2','w3','w4'}






################################ 业务代码 ##################################
# setup
client = owner.onwer()
csp = server.server()
CMAP = client.setup(dataset)
csp.CMAP = CMAP


# update
k,v = client.update('w1', 10000000)
csp.CMAP[k]=v
k,v=client.update('w2', 10000000)
csp.CMAP[k]=v

# search
token = client.gen_token(Q)
round_list, merkle_proof = csp.search(token)
client.verify(round_list, merkle_proof)

k,v = client.update('w3', 10000000)
csp.CMAP[k]=v
k,v=client.update('w4', 10000000)
csp.CMAP[k]=v

token = client.gen_token(Q)
round_list, merkle_proof = csp.search(token)
client.verify(round_list, merkle_proof)