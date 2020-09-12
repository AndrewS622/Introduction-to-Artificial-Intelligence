import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # a cell is known to be a mine if the length of the set is equal to the count
        if len(self.cells) <= self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # a cell is known to be safe if the count is zero
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # marking a mine removes the cell from the set and decrements the count
        if cell in self.cells:
            self.count -= 1
            cell_set = set()
            cell_set.add(cell)
            self.cells = self.cells.difference(cell_set)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # marking a mine as safe removes the cell from the set and doesn't affect the count
        if cell in self.cells:
            cell_set = set()
            cell_set.add(cell)
            self.cells = self.cells.difference(cell_set)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # add cell to moves made, safes, and call mark_safe to adjust all sentences
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # get all valid neighbors of the cell and restrict to those not already known to be safe or already visited
        neighbors = self.get_neighbors(cell)
        neighbors = neighbors.difference(self.safes).difference(self.moves_made)

        # if some of the neighbors are known to be mines, remove them as well and decrement the count
        if len(neighbors.intersection(self.mines)) > 0:
            count -= len(neighbors.intersection(self.mines))
            neighbors = neighbors.difference(self.mines)

        # add new knowledge if the remaining neighbor set is non-zero in length
        if len(neighbors) > 0:
            self.knowledge.append(Sentence(neighbors, count))

        # loop over all sentences and check if we can make conclusions
        for sentence in self.knowledge:
            # if we know all cells are mines, mark them all and add them to list
            if len(sentence.known_mines()) is not 0:
                for mine in sentence.known_mines():
                    self.mark_mine(mine)
            # similar if we know all cells are safe
            elif len(sentence.known_safes()) is not 0:
                for safe in sentence.known_safes():
                    self.mark_safe(safe)
            # loop over all other sentences and compare to check for subsets
            for sentence2 in self.knowledge:
                if sentence.cells < sentence2.cells:
                    # if we find a subset, add a new sentence with the count difference if it is not in knowledge yet
                    new_sentence = Sentence(sentence2.cells.difference(sentence.cells), sentence2.count - sentence.count)
                    if new_sentence not in self.knowledge:
                        self.knowledge.append(new_sentence)

    def get_neighbors(self, cell):
        """
        Gets all the legal neighbors surrounding a cell on the board
        """
        # construct all neighbors based on combinations of i, j +/- 1
        i, j = cell
        h = Minesweeper().height
        w = Minesweeper().width
        neighbors = {(i - 1, j - 1), (i - 1, j), (i - 1, j + 1), (i, j - 1), (i, j + 1),
                     (i + 1, j - 1), (i + 1, j), (i + 1, j + 1)}
        legal = set()

        # restrict output to those bounded by the board dimensions
        for neighbor in neighbors:
            if 0 <= neighbor[0] < h and 0 <= neighbor[1] < w:
                legal.add(neighbor)
        return legal

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # available moves are those known to be safe that have not been made
        avail_moves = self.safes.difference(self.moves_made)
        if len(avail_moves) == 0:
            return None
        else:
            move = random.sample(avail_moves, 1)[0]
            return move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # construct all positions on board
        h = Minesweeper().height
        w = Minesweeper().width
        moves = set()
        for i in range(h):
            for j in range(w):
                moves.add((i, j))

        # available moves are those that have not been made and are not known to be mines
        avail_moves = moves.difference(self.moves_made).difference(self.mines)

        # randomly choose one
        move = random.sample(avail_moves, 1)[0]
        return move
