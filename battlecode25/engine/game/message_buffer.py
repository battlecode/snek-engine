from .message import Message

class MessageBuffer:

    def __init__(self, size):
        self.rounds = [[] for _ in range(size)]
        self.head = 0
        self.round = 0

    def add_message(self, message: Message):
        messages = self.rounds[self.head]
        messages.append(Message(message.bytes, message.sender_id, message.round))

    def next_round(self):
        self.head += 1
        self.head %= len(self.rounds)
        self.round += 1
        self.rounds[self.head] = []

    def get_all_messages(self):
        '''Returns messages in reverse-chronological order'''
        result = []
        for i in range(len(self.rounds)):
            index = self.head - i
            result.extend(self.rounds[index])
        return result

    def get_messages(self, round):
        if self.round - round + 1 > len(self.rounds):
            return []
        return self.rounds[self.head - (self.round - round)][:]