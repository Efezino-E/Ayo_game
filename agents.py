class Human():
    def __init__(self, player_num):
        self.player_num = player_num
        self.species = "homo_sapien"
        self.name = input(f"Player {self.player_num}, state your name: ")
    
    def __name__(self):
        return self.name
    
    def get_position(self, board, player):
        # map player index to side of the board
        side = {0 : "upper", 1 : "lower"}
        
        # print whose turn it is and thei rside
        print(f"it is player {self.name}'s turn. He/She plays at the {side[player.player_num]} side of the board")

        # prompt human to select column
        column = input("starting from the left as column 0, what column number do you want to distribute beads from: ")

        # convert column to board position
        position = (player.player_num, int(column))

        # return position
        return position