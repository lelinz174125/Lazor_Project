
def read_bff(file_name):
    '''
    Extract imformation from '.bff' file

   
    '''
   pass

class Block:
    def __init__(self, block_cor, type):
        self.block_cor = block_cor
        self.type = type

    def block_dir(self, point, direction):

       pass


def meet_block(grid, point, direction):
    '''
    If the laser is not currently at the boundary, this function will check
    whether laser interacts with a block and return the new direction of laser
   
    '''
    pass

def inputblock(grid, A_num, B_num, C_num):
    pass


def check(grid, laz_co, direction):
    """
    This function is used to check if the lazer and its next step
    is inside the grid, if it is not, return to the last step.

   
    """
    pass


def solver(grid, init_laz_list, holelist):
    """
    This function is the main function of the code, it uses
    the board we read and generated and the blocks we defined above.
    We first save all the points of the initial lazer and put the blocks
    on to the grid and save the new lazor path, this continues until we reach a
    hole, then the coordinate of this hole is removed from the hole list
    when there are no coordinates in the hole list, the loop ends and return
    the coordinate of each block.
    """
   pass


if __name__ == "__main__":

    grid = [['B', 'o', 'o'], ['A', 'x', 'x'], [
        'B', 'o', 'A'], ['A', 'x', 'o'], ['B', 'o', 'o']]
    lazors = [[4, 9, -1, -1], [6, 9, -1, -1]]
    hole = [[2, 5], [5, 0]]
    
    print(solver(grid=grid, init_laz_list=lazors, holelist=hole))
