
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

def get_colors():
    '''
    Colors map that the lazor board will use:
        0 - BlackGray - The background
        A - White - A reflect block 
        B - Black - A black block
        C - transparent - A transparent block
        o - Gray - A possible space for putting block
        x - BlackGray - A place that could not have block

    **Returns**

        color_map: *dict, int, tuple*
            A dictionary that will correlate the integer key to
            a color.
    '''
    return {
        0: (20, 20, 20),
        'A': (255, 255, 255),
        'B': (0, 0, 0),
        'C': (255, 0, 0),
        'o': (100, 100, 100),
        'x': (50, 50, 50),
    }

def save_board(unsolved_board, lazors_info, holes, filename, blockSize=100):
            #   (unsolved_board, solved_board, filename,
            #   lazors_pos, holes, stack_lazors, blockSize=100)
    '''
    This function is to save the unsolved and solved board.
    "filename_board.png" and "filename_solved.png"
    The idea of the code come from the maze lab of the software carpentry class.
    *** Parameters ***
    unsolved_board : List of Lists 
    solved_board : List of Lists 
    filename: String - .bff filename
    lazors_info : List of tuples - Consisting of all origins and directions of the lazors
    holes : List - consisiting of the hole points
    stack_lazors - List of Lists - consisting of the lazor path
                                   for each lazor
    blocksize - Integer - Size of the block of the board
    *** Returns ***
    Nothing as it saves the boards as images
    '''

    nBlocksx = len(unsolved_board[0])
    nBlocksy = len(unsolved_board)
    dimx = nBlocksx * blockSize
    dimy = nBlocksy * blockSize
    colors = get_colors()

    # Verify that all values in the board are valid colors.
    ERR_MSG = "Error, invalid board value found!"
    assert all([x in colors.keys()
                for row in unsolved_board for x in row]), ERR_MSG

    img = Image.new("RGB", (dimx, dimy), color=0)

    # Parse "board" into pixels
    for jy in range(nBlocksy):
        for jx in range(nBlocksx):
            x = jx * blockSize
            y = jy * blockSize

            for i in range(blockSize):
                for j in range(blockSize):
                    img.putpixel((x + i, y + j),
                                 colors[unsolved_board[jy][jx]])

    for i in range(nBlocksy - 1):
        y = (i + 1) * blockSize
        shape = [(0, y), (dimx, y)]
        img_new = ImageDraw.Draw(img)
        img_new.line(shape, fill=0 in colors.keys(), width=5)

    for i in range(nBlocksx - 1):
        x = (i + 1) * blockSize
        shape = [(x, 0), (x, dimy)]
        img_new = ImageDraw.Draw(img)
        img_new.line(shape, fill=0 in colors.keys(), width=5)

    for i in range(len(lazors_info)):
        lazor_info = lazors_info[i]
        lazor_pos = (lazor_info[0], lazor_info[1])
        lazor_dir = (lazor_info[2], lazor_info[3])
        print(lazor_pos, lazor_dir)
        # x=lazor_pos[0]*blockSize/2
        # y=lazor_pos[1]*blockSize/2
        # print(x,y)
        img_new = ImageDraw.Draw(img)
        img_new.ellipse([lazor_pos[0] * blockSize / 2 - 10, lazor_pos[1] * blockSize / 2 - 10,
                         lazor_pos[0] * blockSize / 2 + 10, lazor_pos[1] * blockSize / 2 + 10], fill=(255, 0, 0))

        lazor_out = (lazor_pos[0] + lazor_dir[0], lazor_pos[1] + lazor_dir[1])
        while 0 < lazor_out[0] < nBlocksx * 2 and 0 < lazor_out[1] < nBlocksy * 2:
            x = lazor_out[0] + lazor_dir[0]
            lazor_out = (lazor_out[0] + lazor_dir[0],
                         lazor_out[1] + lazor_dir[1])

        x1 = lazor_pos[0] * blockSize / 2
        y1 = lazor_pos[1] * blockSize / 2
        x2 = lazor_out[0] * blockSize / 2
        y2 = lazor_out[1] * blockSize / 2
        img_new = ImageDraw.Draw(img)
        img_new.line([(x1, y1), (x2, y2)], fill=(255, 0, 0), width=5)

    for i in range(len(holes)):
        img_new.ellipse([holes[i][0] * blockSize / 2 - 10, holes[i][1] * blockSize / 2 - 10,
                         holes[i][0] * blockSize / 2 + 10, holes[i][1] * blockSize / 2 + 10], fill=(255, 255, 255), outline="red", width=2)


    if not filename.endswith(".png"):
        filename += ".png"

    img.save("%s" % filename)


def save_answer_board(solved_board, answer_lazor, lazors_info, holes, filename, blockSize=100):
            #   (unsolved_board, solved_board, filename,
            #   lazors_pos, holes, stack_lazors, blockSize=100)
    '''
    This function is to save the unsolved and solved board.
    "filename_board.png" and "filename_solved.png"
    The idea of the code come from the maze lab of the software carpentry class.
    *** Parameters ***
    solved_board : List of Lists 
    answer_lazor: List of Lists
    filename: String - .bff filename
    lazors_info : List of tuples - Consisting of all origins and directions of the lazors
    holes : List - consisiting of the hole points
    stack_lazors - List of Lists - consisting of the lazor path
                                   for each lazor
    blocksize - Integer - Size of the block of the board
    *** Returns ***
    Nothing as it saves the boards as images
    '''

    nBlocksx = len(solved_board[0])
    nBlocksy = len(solved_board)
    dimx = nBlocksx * blockSize
    dimy = nBlocksy * blockSize
    colors = get_colors()


    # Verify that all values in the board are valid colors.
    ERR_MSG = "Error, invalid board value found!"
    assert all([x in colors.keys()
                for row in solved_board for x in row]), ERR_MSG

    img = Image.new("RGB", (dimx, dimy), color=0)

    # Parse "board" into pixels
    for jy in range(nBlocksy):
        for jx in range(nBlocksx):
            x = jx * blockSize
            y = jy * blockSize

            for i in range(blockSize):
                for j in range(blockSize):
                    img.putpixel((x + i, y + j),
                                 colors[solved_board[jy][jx]])

    for i in range(nBlocksy - 1):
        y = (i + 1) * blockSize
        shape = [(0, y), (dimx, y)]
        img_new = ImageDraw.Draw(img)
        img_new.line(shape, fill=0 in colors.keys(), width=5)

    for i in range(nBlocksx - 1):
        x = (i + 1) * blockSize
        shape = [(x, 0), (x, dimy)]
        img_new = ImageDraw.Draw(img)
        img_new.line(shape, fill=0 in colors.keys(), width=5)

    for i in range(len(lazors_info)):
        lazor_info = lazors_info[i]
        lazor_pos = (lazor_info[0], lazor_info[1])
        lazor_dir = (lazor_info[2], lazor_info[3])
        # x=lazor_pos[0]*blockSize/2
        # y=lazor_pos[1]*blockSize/2
        # print(x,y)
        img_new = ImageDraw.Draw(img)
        img_new.ellipse([lazor_pos[0] * blockSize / 2 - 10, lazor_pos[1] * blockSize / 2 - 10,
                         lazor_pos[0] * blockSize / 2 + 10, lazor_pos[1] * blockSize / 2 + 10], fill=(255, 0, 0))

        for i in answer_lazor:
            end = [i[-1][0],i[-1][1]]
            while end not in holes:
                i.pop()
                end = [i[-1][0],i[-1][1]]

        for i in answer_lazor:
            for point in range(len(i)):
                co_start = (i[point][0]* blockSize / 2,i[point][1]* blockSize / 2)
                if point+1 < len(i):
                    co_end = (i[point+1][0]* blockSize / 2,i[point+1][1]* blockSize / 2)
                else:
                    co_end = co_start
                img_new = ImageDraw.Draw(img)
                img_new.line([co_start, co_end], fill=(255, 0, 0), width=5)

    for i in range(len(holes)):
        img_new.ellipse([holes[i][0] * blockSize / 2 - 10, holes[i][1] * blockSize / 2 - 10,
                         holes[i][0] * blockSize / 2 + 10, holes[i][1] * blockSize / 2 + 10], fill=(255, 255, 255), outline="red", width=2)

    if not filename.endswith(".png"):
        filename += "_solved.png"

    img.save("%s" % filename)



if __name__ == "__main__":

    grid = [['B', 'o', 'o'], ['A', 'x', 'x'], [
        'B', 'o', 'A'], ['A', 'x', 'o'], ['B', 'o', 'o']]
    lazors = [[4, 9, -1, -1], [6, 9, -1, -1]]
    hole = [[2, 5], [5, 0]]
    
    print(solver(grid=grid, init_laz_list=lazors, holelist=hole))
