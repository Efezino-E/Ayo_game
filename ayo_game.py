import numpy as np
from agents import *

DISTRIBUTION_ORDER = ((0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (0, 0), (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5))

class ayo_game():
    def __init__(self):
        """
        Initializes board, player, and score
        """
        # initialize board
        self.board = np.full((2, 6), 4)

        # keep track of whose turn it is (0 is the upper side of the board, 1 is the lower)
        self.player = 0

        # keep track of players 
        self.players = [None, None]

        # keep track of score
        self.score = np.array([0, 0])
    
    def distribute(self, position, path = False, states = None):
        """
        updates board by distributing beads from position in an anticlockwise manner
        returns position of last bead drop
        """
        # get the number of beads in position n
        i, j = position
        n = self.board[i][j]

        # remove beads from the position
        self.board[i][j] = 0
        if path:
            states["boards"].append(self.board.copy())
            states["scores"].append(self.score.copy())

        # distribute the n beads in an anticlockwise manner
        order_index = DISTRIBUTION_ORDER.index((i, j))
        for p in range(order_index + 1, order_index + n + 1):
            p = p % 12
            pos = DISTRIBUTION_ORDER[p]
            self.board[pos[0]][pos[1]] += 1
            if path:
                states["boards"].append(self.board.copy())
                states["scores"].append(self.score.copy())
        
        return (pos[0], pos[1])


    def full_distribute(self, position, path = False):
        """
        updates the board and scores given a distribution from a certain valid position
        if path is True, return all the intermediate board states
        """
        # keep track of board states
        if path:
            states = {"boards" : [], "scores" : []}
        else:
            states = None

        # keep track of who collected last
        collected = None

        # continually distribute beads
        while True:
            # distribute beads from position and get the last updated cell position
            position = self.distribute(position, path, states)
            
            # if distrbution stops on a cell with formerly zero beads then stop loop
            if self.board[position[0]][position[1]] == 1:
                break

            # elif distribution stops on cell that now has four beads, collect score for player, and stop loop
            elif self.board[position[0]][position[1]] == 4:
                self.board[position[0]][position[1]] = 0
                self.score[self.player] += 4
                if path:
                    states["boards"].append(self.board.copy())
                    states["scores"].append(self.score.copy())
                collected = self.player
                break

            # else continue the loop

        # collect any fours created as scores to the player_side they were created
        for column in range(6):
            for player in (self.player, (self.player + 1) % 2):
                if self.board[player][column] == 4:
                    collected = player
                    self.board[player][column] = 0
                    self.score[player] += 4
                    if path:
                        states["boards"].append(self.board.copy())
                        states["scores"].append(self.score.copy())
        
        # if there are four beads left, give it to the last person who collected.
        if np.sum(self.board) == 4:
            self.board = np.full((2, 6), 0)
            self.score[collected] += 4
            if path:
                states["boards"].append(self.board.copy())
                states["scores"].append(self.score.copy())
        
        if path:
            return states

    def play(self):
        """
        get position from player
        checks if position is valid to play for player
        update board and scores from position returned
        switch player to opponent
        """
        # get the current player
        player = self.players[self.player]

        # get a position from the player
        position = player.get_position(self.board, player)

        # check if position is not valid
        if not self.valid(position):
            if player.species == "ai":
                raise ValueError("invalid position from AI")
            elif player.species == "homo_sapien":
                position = self.get_valid_position(player)
            else:
                raise ValueError("invalid position")
        
        # update board
        self.full_distribute(position)

        # switch player to opponent
        self.player = (self.player + 1) % 2
    
    def get_valid_position(self, player):
        """
        iteratively asks Human for a valid position till they give one
        """
        # Let human know valid positions
        print(f"please select a valid column from {[position[1] for position in self.valid_positions()]}")

        # select another position
        position = player.get_position(self.board, player)

        # while position selected is not valid repeat
        if not self.valid(position):
            return self.get_valid_position(player)
        else:
            return position

    def valid(self, position):
        """
        returns True is move is valid 
        retunrs (False, Rs) is move is invalid, 
        where Rs is the reason it is an invalid move
        """
        return position in self.valid_positions()
    
    def valid_positions(self):
        """
        returns a list of valid positions for player
        """
        # initialize the list of valid positions
        valid_pos = []

        # determine if there are beads in the other player's half
        opp_beads = np.sum(self.board[(self.player + 1) % 2])

        # iterate through all possible column choices
        for column in range(6):
            # if opponent has beads, all positions with beads in player's half are valid
            if opp_beads > 0 and self.board[self.player][column] > 0:
                valid_pos.append((self.player, column))
            
            # if opponent has no beads, the only valid moves should give the opponent beads to play with
            elif opp_beads == 0:
                if self.player == 0 and self.board[self.player][column] >= column + 1:
                    valid_pos.append((self.player, column))
                elif self.player == 1 and self.board[self.player][column] >= 6 - column:
                    valid_pos.append((self.player, column))
        
        return valid_pos
    
    def terminal(self):
        """
        checks if the game has ended and returns the winner if any
        """
        # if there are no beads left
        if np.sum(self.board) == 0:
            return True
        else:
            return False
    
    def winner(self):
        """
        prints the winner of the game
        """
        # find the winner and loser
        winner = np.argmax(self.score)
        loser = (winner + 1) % 2

        # check if it is a draw actually
        if self.score[winner] > self.score[loser]:
            tag = "defets"
        else:
            tag = "draws"

        # print game terminal status
        print(f"{self.players[winner].__name__()} {tag} {self.players[loser].__name__()}")
        print(f"with a score of {self.score[winner]} to {self.score[loser]}")

    def run(self, ai_1 = None, ai_2 = None):
        """
        assigns players
        runs the game between two players.
        if any AI is set, the a player must be that AI
        """
        # assign agents as players
        if ai_1:
            self.players[0] = ai_1
        else:
            self.players[0] = Human(0)

        if ai_2:
            self.players[1] = ai_2
        else:
            self.players[1] = Human(1)
        
        # print agents's side of the board and who plays first
        print("")
        print(f"{self.players[0].__name__()} plays has the upper side of the board, while {self.players[1].__name__()} has the lower side")
        print("")
        print(f"player {self.players[self.player].__name__()} plays first")
        
        # show the starting board
        self.show_board()

        # while game has not ended
        while not self.terminal():
            # ask the current player to play
            self.play()

            # show the board for the next player
            self.show_board()
        
        # since game has ended, show the winner
        self.winner()
            
    def show_board(self):
        """
        prints the board and score
        """
        print("")
        print(self.board)
        print("scores")
        for player in self.players:
            print(f"{player.__name__()}: {self.score[player.player_num]}")
        
        print("")

if __name__ == "__main__":
    game = ayo_game()
    game.run()
