class Message:
    
    def __init__(self, bytes, sender_id, round):
        self.sender_id = sender_id
        self.round = round
        self.bytes = bytes

    def get_sender_id(self):
        return self.sender_id

    def get_round(self):
        return self.round

    def get_bytes(self):
        return self.bytes

    def __str__(self):
        return f"Message with value {self.bytes} sent from robot with ID {self.sender_id} during round {self.round}."