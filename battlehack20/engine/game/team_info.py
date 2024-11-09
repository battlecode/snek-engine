from .constants import GameConstants

class TeamInfo:

    def __init__(self, game_world):
        self.game_world = game_world
        self.coin_counts = [0] * 2  
        self.tiles_painted = [0] * 2 
        self.paint_counts = [0] * 2
        self.old_coin_counts = [0] * 2
        self.num_allied_towers = [0] * 2
        self.num_allied_units = [0] * 2

    # ***** GETTER METHODS *****

    def get_coins(self, team):
        """Return the total coins of the specified team."""
        return self.coin_counts[team]

    def get_tiles_painted(self, team):
        """Return the total tiles painted by the specified team."""
        return self.tiles_painted[team]
    
    def get_shared_array(self, team):
        """Return the shared array of the specified team."""
        return self.shared_arrays[team]

    def get_round_coin_change(self, team):
        """Return the change in coins for the specified team during the current round."""
        return self.coin_counts[team] - self.old_coin_counts[team]

    def get_num_allied_towers(self, team):
        return self.num_allied_towers[team]
    
    def get_paint_counts(self, team):
        return self.paint_counts[team]
    
    def get_num_allied_units(self, team):
        return self.num_allied_units[team]
    
    # ***** UPDATE METHODS *****

    def add_coins(self, team, amount):
        """Add or subtract coins for the specified team."""
        if self.coin_counts[team.value] + amount < 0:
            raise ValueError("Invalid coin change")
        self.coin_counts[team.value] += amount

    def paint_tile(self, team):
        """Increment the count of tiles painted by the specified team."""
        self.tiles_painted[team.value] += 1

    def process_end_of_round(self):
        """Save the current coin counts to track changes in the next round."""
        self.old_coin_counts = self.coin_counts.copy()
