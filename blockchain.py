import hashlib
import json
import time
import os

class Blockchain:
    def __init__(self):
        self.chain = []
        self.ledger_file = 'ledger.json'
        self.load_ledger()
        if not self.chain:
            self.create_block(transaction_data='Genesis Block', user_id='SYSTEM')

    def create_block(self, transaction_data, user_id):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.strftime('%d-%b-%Y %H:%M:%S'),
            'user_id': user_id,
            'transaction_data': transaction_data,
            'previous_hash': self.get_last_block_hash(),
        }
        block['hash'] = self.hash_block(block)
        self.chain.append(block)
        self.save_to_ledger()
        return block

    def add_block(self, data):
        return self.create_block(transaction_data=data['transaction_data'], user_id=data['user_id'])

    def get_last_block_hash(self):
        if not self.chain:
            return '0'
        return self.chain[-1]['hash']

    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def get_full_chain(self):
        return self.chain

    def to_list(self):
        return self.get_full_chain()

    def save_to_ledger(self):
        try:
            with open(self.ledger_file, 'w') as f:
                json.dump(self.chain, f, indent=4)
        except Exception as e:
            print(f"Error saving ledger: {e}")

    def load_ledger(self):
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, 'r') as f:
                    self.chain = json.load(f)
            except Exception as e:
                print(f"Error loading ledger: {e}")
                self.chain = []
        else:
            self.chain = []

# Global blockchain instance
blockchain = Blockchain()
