class MessageBuffer:

    def __init__(self, size, max_per_round):
        self.rounds = [[] for _ in range(size)]
        self.head = 0
        self.round = 0

    def add_message(self, message):
        messages = self.rounds[self.head]
        messages.append(message)

    def next_round(self):
        self.head += 1
        self.head %= len(self.rounds)
        self.round += 1
        self.rounds[self.head] = []

    def get_all_messages(self):
        '''return messages in reverse-chronological order'''
        result = []
        for i in range(len(self.rounds)):
            index = self.head - i
            result.extend([(self.round - i, message) for message in self.rounds[index]])
        return result

    def get_messages(self, round):
        return [(round, message) for message in self.rounds[self.head - (self.round - round)]]