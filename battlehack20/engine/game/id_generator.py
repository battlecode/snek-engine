import random

class IDGenerator:

    ID_BLOCK_SIZE = 4096
    MIN_ID = 10000

    def __init__(self):
        self.cursor = 0
        self.next_id_block = IDGenerator.MIN_ID
        self.allocate_next_block()
        self.reserved_ids = [0] * IDGenerator.ID_BLOCK_SIZE

    def next_id(self):
        id = self.reserved_ids[self.cursor]
        self.cursor += 1

        if self.cursor == IDGenerator.ID_BLOCK_SIZE:
            self.allocate_next_block()
        return id
    
    def allocate_next_block(self):
        self.cursor = 0
        for i in range(IDGenerator.ID_BLOCK_SIZE):
            self.reserved_ids[i] = self.next_id_block + i + 1

        for i in range(IDGenerator.ID_BLOCK_SIZE-1, 0, -1):
            swap = random.randint(0, i)
            temp = self.reserved_ids[swap]
            self.reserved_ids[swap] = self.reserved_ids[i]
            self.reserved_ids[i] = temp

        self.next_id_block += IDGenerator.ID_BLOCK_SIZE

