import time
import threading
import sys
from web3 import Web3
import asyncio
import json
import websockets
from neo4j import (
    GraphDatabase,
    basic_auth,
)

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/0f9fab07058c4d90afd7b3f6014d491f'))
tx_queue = []
lock = threading.Lock()

class WatchThread(threading.Thread):
    def run(self):
        asyncio.run(self.watch())
    
    async def watch(self):
        async with websockets.connect("wss://mainnet.infura.io/ws/v3/0f9fab07058c4d90afd7b3f6014d491f", ping_interval=None) as ws:
            await ws.send(json.dumps({"id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]})) #newHeads
            subscription_response = await ws.recv()
            #print(subscription_response)
            while True:
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=120)
                    data = json.loads(message)
                    print(message)
                    tx_hash = data['params']['result']

                    # add only valid transaction into queue
                    tx = w3.eth.get_transaction(tx_hash)
                    tx_queue.append(tx_hash)   
                except websockets.exceptions.ConnectionClosedError:
                    print(sys.exc_info())
                    break
                except:
                    print(sys.exc_info())  

                #asyncio.sleep(1)  

def record_transaction(data):
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=basic_auth('neo4j', 'qwer1234'))
    neo4j_db = driver.session(database='game')
    #driver = GraphDatabase.driver('bolt://172.30.77.160:7687', auth=basic_auth('Chris', 'ChrisMeta67%!'))
    #neo4j_db = driver.session()

    def _work(tx, data):
        query = (
            'MERGE (:Tx { hash: $hash }) ',
            'ON CREATE SET block_hash=$block_hash, block_number=$block_number, from=$from, gas=$gas, gas_price=$gas_price, nonce=$nonce, to=$to, tx_index=$tx_index, type=$type, confirm_count=$confirm_count'
        )
        return tx.run(query, data)

    neo4j_db.write_transaction(_work, data)

class ConfirmThread(threading.Thread):
    def run(self):
        while (True):
            lock.acquire()
            new_queue = tx_queue.copy()
            for tx_hash in new_queue:
                try:
                    tx = w3.eth.get_transaction(tx_hash)
                    ret, confirm_count = self.check_confirmation(tx)
                    if ret == False:
                        continue

                    tx_queue.remove(tx_hash)

                    block_number = tx['blockNumber']
                    block_hash = tx['blockHash']
                    from_ = tx['from']
                    gas = tx['gas']
                    gas_price = tx['gasPrice']
                    #input = tx['input'] # not sure
                    hash = tx['hash']
                    nonce = tx['nonce']
                    #r = tx['r'] # not sure
                    #s = tx['s'] # not sure
                    to = tx['to']
                    tx_index = tx['transactionIndex']
                    type_ = tx['type']
                    #v = tx['v'] # not sure
                    #value = tx['value'] # not sure
                    print('SUCCESS >>> hash: ', hash, ' block number: ', block_number, ' block hash: ', block_hash, ' from: ', 
                    from_, ' gas: ', gas, ' gas_price: ', gas_price, ' nonce: ', nonce, ' to: ', to, ' tx index: ', tx_index, 
                    ' type: ', type_)

                    data = {
                        'block_hash': block_hash,
                        'block_number': block_number,
                        'from': from_,
                        'gas': gas,
                        'gas_price': gas_price,
                        'hash': hash,
                        'nonce': nonce,
                        'to': to,
                        'tx_index': tx_index,
                        'type': type_,   
                        'confirm_count': confirm_count                     
                    }

                    record_transaction(data)
                except:
                    print('confirmation >>> ', sys.exc_info())
            
            lock.release()
            time.sleep(30)

    def check_confirmation(self, tx, min_confirm_count = 5) -> int:
        confirm_count = self.get_confirmation(tx)
        print('>>> CONFIRM COUNT: ', confirm_count)
        if confirm_count > min_confirm_count:
            return True, confirm_count
        else:
            return False, confirm_count

    def get_confirmation(self, tx) -> int :
        try:
            current_block_number = w3.eth.get_block_number()
            tx_block_number = tx['blockNumber']
            if tx_block_number is None:
                return 0
            else:
                return current_block_number - tx_block_number
        except:
            print(sys.exc_info())
            return 0

def main():
    watch_thread = WatchThread()
    confirm_thread = ConfirmThread()
    watch_thread.start()
    confirm_thread.start()
    
    #loop = asyncio.get_event_loop()
    #while True:
    #    loop.run_until_complete(get_event())

if (__name__ == '__main__'):
    main()