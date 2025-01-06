class Message:
    
    def __init__(self, bytes: int, sender_id: int, round: int):
        self.sender_id = sender_id
        self.round = round
        self.bytes = bytes

    def get_sender_id(self) -> int:
        """
        Returns the ID of the robot that sent this message
        """
        return self.sender_id

    def get_round(self) -> int:
        """
        Returns the round in which this message was sent
        """
        return self.round

    def get_bytes(self) -> int:
        """
        Returns the content of the message as a 32-bit integer
        """
        return self.bytes

    def __str__(self):
        return f"Message with value {self.bytes} sent from robot with ID {self.sender_id} during round {self.round}."