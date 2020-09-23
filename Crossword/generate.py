import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # iterate through each variable
        for var in self.crossword.variables:
            domain_consistent = set()
            # append each word in domain to list if lengths match
            for word in self.domains[var]:
                if var.length == len(word):
                    domain_consistent.add(word)
            # update domain of variable
            self.domains[var] = domain_consistent

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        change = False
        overlap = self.crossword.overlaps[x, y]

        # for a given (x, y) pair with an overlap
        if overlap is not None:
            to_remove = set()
            i = overlap[0]
            j = overlap[1]
            # iterate through each word in domain of x
            for word in self.domains[x]:
                # append to set if word does not have any match in domain of y
                if all(word[i] != other[j] for other in self.domains[y]):
                    change = True
                    to_remove.add(word)
            # remove invalid words from domain of x
            for word in list(to_remove):
                self.domains[x].remove(word)
        return change

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # if no arcs in argument, get list of all arcs (i.e. all overlaps)
        # filter to list of non-None tuples
        if arcs is None:
            arcs = []
            for key in self.crossword.overlaps.keys():
                if self.crossword.overlaps[key[0], key[1]] is not None:
                    arcs.append(key)
        while len(arcs) > 0:
            # get first element of list (queue)
            arc = arcs.pop(0)
            # if a change was made to the domain of arc[0]
            if self.revise(arc[0], arc[1]):
                # check if it now has no elements in its domain
                if len(self.domains[arc[0]]) == 0:
                    return False
                # otherwise, add all (Z, X) pairs to the end of the queue
                neighbors = list(self.crossword.neighbors(arc[0]) - {arc[1]})
                if len(neighbors) >= 1:
                    for neighbor in neighbors:
                        arcs.append((neighbor, arc[0]))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # check if any variable is not in assignment.keys()
        for var in self.crossword.variables:
            if var not in assignment.keys():
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # for each variable-word pair in the current assignment
        for var, word in assignment.items():
            # check to make sure lengths match (this should have already been enforced by node consistency)
            if var.length != len(word):
                return False
            # check all neighbors of the current variable
            for neighbor in self.crossword.neighbors(var):
                # if a given neighbor has been assigned in the current assignment
                if neighbor in assignment.keys():
                    overlap = self.crossword.overlaps[var, neighbor]
                    neighbor_word = assignment[neighbor]
                    # make sure the overlap matches
                    if word[overlap[0]] != neighbor_word[overlap[1]]:
                        return False
        # make sure all words are unique (sets only consider unique elements)
        if len(list(assignment.values())) != len(set(assignment.values())):
            return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domain_values = list()
        domain_list = list()
        # for each value in the domain of the variable
        for value in self.domains[var]:
            # initialize a counter
            n = 0
            # for each unassigned neighbor
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment.keys():
                    # get the overlap, and iterate through each word in the neighbor's domain
                    overlap = self.crossword.overlaps[var, neighbor]
                    for neighbor_value in self.domains[neighbor]:
                        # if the overlap does not match, this word is forbidden, so the counter is incremented
                        if value[overlap[0]] != neighbor_value[overlap[1]]:
                            n += 1
            domain_values.append(n)
            domain_list.append(value)
        # sort list by n
        sorted_list = [x for _,x in sorted(zip(domain_values, domain_list))]
        return sorted_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # lists for minimum remaining value, degree of node, and unassigned variables
        MRV = list()
        degree = list()
        vars = list()
        # for each unassigned variable
        for var in self.crossword.variables:
            if var not in assignment.keys():
                # append the variable, its MRV, and its degree
                vars.append(var)
                MRV.append(len(self.domains[var]))
                degree.append(len(self.crossword.neighbors(var)))

        # find minimum MRV of all unassigned variables
        min_val = min(MRV)
        # if more than one have the minimum value
        if MRV.count(min_val) > 1:
            # extract degree of each of these nodes
            degree_index = [i for i,x in enumerate(MRV) if x == min_val]
            min_degree = [degree[i] for i in degree_index]
            # choose the one with the maximum degree
            idx = degree.index(max(min_degree))
            return vars[idx]
        # otherwise, return the variable with the minimum value
        return vars[MRV.index(min_val)]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # if assignment is complete, done
        if self.assignment_complete(assignment):
            return assignment
        # select an unassigned variable
        var = self.select_unassigned_variable(assignment)
        # iterate over each of its possible word assignments, from least constraining first
        for value in self.order_domain_values(var, assignment):
            # copy the current assignment and add the new var-value pair
            assignment_new = assignment.copy()
            assignment_new[var] = value
            # if this new assignment is inconsistent, go to next iteration; otherwise
            if self.consistent(assignment_new):
                # record current domains prior to enforcing arc consistency with new assignment
                domain_old = dict()
                for var2 in self.crossword.variables:
                    domain_old[var2] = self.domains[var2]
                # make list of (Z, X) arcs to consider with new assignment
                arcs = list()
                for neighbor in self.crossword.neighbors(var):
                    arcs.append((neighbor, var))
                # update domains with new assignment (Maintaining Arc-Consistency)
                inferences = self.ac3(arcs)
                # continue to next word if unsuccessful (i.e. if a variable has an empty domain)
                if not inferences:
                    continue
                # recursively call backtrack with current assignment
                res = self.backtrack(assignment_new)
                if res:
                    return res
                # if backtrack was unsuccessful, restore domain back to previous state and continue to next word
                for var2 in self.crossword.variables:
                    self.domains[var2] = domain_old[var2]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
