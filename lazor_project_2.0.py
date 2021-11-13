from PIL import Image, ImageDraw
from sympy.utilities.iterables import multiset_permutations
import copy
import random
import time
import numpy as np


def read_bff(file_name):
    '''
    Extract imformation from '.bff' file

    **Parameters**

        file_name: *str*
            The full name of the file which has information to be extracted

    **Return**

        tuple: *list, int, int, int, list, list*
            Elements in the tuple are as follow:
                Grid: *list*
                    The full grid in the form of a coordinate system
                A: *int*
                    The number of A-block available
                B: *int*
                    The number of B-block available
                C: *int*
                    The number of C-block available
                Lasors: *list*
                    The first two elements is the positon of the start point, the last two elements are the direction.
                End point: *list
                    The positions of the end points
    '''
    # initialize the parameters
    content = []  # store the content
    grid = []
    grid_origin = []
    grid_temp = []
    A_num = 0  # initialize A, B, C, L, P
    B_num = 0
    C_num = 0
    L_list = []
    P_list = []
    # open and read the file
    with open(file_name, 'r') as f:
        # get all the lines in the file
        lines = list(f)
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
            content.append(list(lines[i]))
    # extract useful information
    for i in range(len(content)):
        for j in range(len(content[i])):
            A_temp = []  # set up some temporary lists
            B_temp = []
            C_temp = []
            L_temp = []
            P_temp = []
            # Get the number of available A-block
            if content[i][j] == 'A' and (str.isalpha(content[i][j + 1]) is False):
                for k in range(len(content[i])):
                    if str.isdigit(content[i][k]):
                        A_temp.append(content[i][k])
                        A_num = int(''.join(A_temp))
            # Get the number of available B-block
            if content[i][j] == 'B' and (str.isalpha(content[i][j + 1]) is False):
                for k in range(len(content[i])):
                    if str.isdigit(content[i][k]):
                        B_temp.append(content[i][k])
                        B_num = int(''.join(B_temp))
            # Get the number of available C-block
            if content[i][j] == 'C' and (str.isalpha(content[i][j + 1]) is False):
                for k in range(len(content[i])):
                    if str.isdigit(content[i][k]):
                        C_temp.append(content[i][k])
                        C_num = int(''.join(C_temp))
            # Get the positions of the start point and direction of lasors
            if content[i][j] == 'L' and (str.isalpha(content[i][j + 1]) is False):
                L_temp = lines[i].strip().split(' ')
                L_temp.remove('L')
                L_list.append([int(L_temp[0]), int(L_temp[1]),
                               int(L_temp[2]), int(L_temp[3])])
            # Get the positions of the end points
            if content[i][j] == 'P' and (str.isalpha(content[i][j - 1]) is False):
                P_temp = lines[i].strip().split(' ')
                P_temp.remove('P')
                P_list.append([int(P_temp[0]), int(P_temp[1])])

        # get the raw grid from the file
        if lines[i] == 'GRID START':
            grid_start = i + 1
            while lines[grid_start] != 'GRID STOP':
                grid_temp.append(content[grid_start])
                grid_start += 1

    # Remove the spaces of the raw grid
    for i in range(len(grid_temp)):
        gridline = [x for x in grid_temp[i] if x != ' ']
        grid.append(gridline)
    # Get the original grid which will be used to draw a picture
    for i in range(len(grid_temp)):
        gridline = [x for x in grid_temp[i] if x != ' ']
        grid_origin.append(gridline)
    # Fulfill the grid with 'x' to get the full grid
    gridfull = grid.copy()
    row = len(gridfull)
    column = len(gridfull[0])
    insert = ['x'] * (2 * column + 1)
    for i in range(0, row):
        for j in range(0, column + 1):
            gridfull[i].insert(2 * j, 'x')
    for i in range(0, row + 1):
        gridfull.insert(2 * i, insert)

    # If unreasonable block number
    if (A_num + B_num + C_num) == 0:
        raise Exception('There are no available block ABC')
    if (A_num + B_num + C_num) >= row * column:
        raise Exception('There are more blocks than available spaces')
    # If there are no lasors
    if len(L_list) == 0:
        raise Exception('There are no lasors')
    for i in range(len(L_list)):
        # If the format of the lasor is incorrect
        if len(L_list[i]) != 4:
            raise Exception('The format of the lasor is incorrect')
    # If the start points of lasors are unreasonable
        if L_list[i][0] < 0 or L_list[i][0] > column * 2 or L_list[i][1] < 0 or L_list[i][1] > row * 2:
            raise Exception('The start point of lasors are out of the grid')
    # If the directions of the lasors are unreasonable
        if (L_list[i][2] != -1 and L_list[i][2] != 1) or (L_list[i][3] != -1 and L_list[i][3] != 1):
            raise Exception('The directions of lasors are unreasonable')
    for i in range(len(P_list)):
        # If the end points are unreasonable
        if P_list[i][0] < 0 or P_list[i][0] > column * 2 or P_list[i][1] < 0 or P_list[i][1] > row * 2:
            raise Exception('The end point of lasors are out of the grid')
    # If there are no end points
    if len(P_list) == 0:
        raise Exception('There are no end points')

    # If there is any element other than 'ABCxo' in grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] not in ['x', 'o', 'A', 'B', 'C']:
                raise Exception('There are undefined characters in the grid')

    return gridfull, A_num, B_num, C_num, L_list, P_list, grid_origin


class Block:
    '''
    Identify the function of block

    **Parameters**

        block_cor: *int tuple*
            represent for the coordinates of block

        type: *str* = A, B, C, x, o
            represent for the types of block

    **Return**

        new_direction: *list, int*
            represent the direction of lazor, when they meet a block

    '''

    def __init__(self, block_cor, type):
        self.block_cor = block_cor
        self.type = type

    def block_dir(self, point, direction):

        new_direction = []
        if self.type == 'A':
            if point[0] & 1 == 0:
                new_direction = [direction[0] * (-1), direction[1]]
            else:
                new_direction = [direction[0], direction[1] * (-1)]
        elif self.type == 'B':
            new_direction = []
        elif self.type == 'C':
            if point[0] & 1 == 0:
                new_direction = [direction[0], direction[1],
                                 direction[0] * (-1), direction[1]]
                # print(new_direction)
            else:
                new_direction = [direction[0], direction[1],
                                 direction[0], direction[1] * (-1)]
                # print(new_direction)
        elif self.type == 'o' or self.type == 'x':
            new_direction = direction
        return new_direction


def meet_block(grid, point, direction):
    '''
    If the laser is not currently at the boundary, this function will check
    whether laser interacts with a block and return the new direction of laser

    **Parameters**

        grid : *list, list, string*
            A list of list stand for a possible solution of the game
        point: *tuple, int*
            The current lazor point
        dirc: *tuple, int*
            The current direction of lazor

    **Return**

        new_dir: *list*
            a list that includes new directions of lazor
    '''

    x1, y1 = point[0], point[1] + direction[1]
    x2, y2 = point[0] + direction[0], point[1]

    if point[0] & 1 == 1:
        block_type = grid[y1][x1]
        block = Block((x1, y1), block_type)
        new_direction = block.block_dir(point, direction)
    if point[0] & 1 == 0:
        # print(y2, x2)
        block_type = grid[y2][x2]
        block = Block((x2, y2), block_type)
        new_direction = block.block_dir(point, direction)

    return new_direction


def inputblock(grid, A_num, B_num, C_num):
    '''
    Fill the blocks into the grid

    **Parameters**

        grid: *list*
            The full grid
        A_num: *int*
            The number of A-block available
        B_num: *int*
            The number of B-block available
        C_num: *int*
            The number of C-block available

    **Return**

        all_Blocks: *list*
            All possible blocks arrangements
    '''
    Blocks = []
    for a in grid:
        for b in a:
            if b == 'o':
                Blocks.append(b)
    # print(Blocks)
    for i in range(A_num):
        Blocks[i] = 'A'
        # print(Blocks)
    for i in range(A_num, (A_num + B_num)):
        Blocks[i] = 'B'
        # print(Blocks)
    for i in range((A_num + B_num), (A_num + B_num + C_num)):
        Blocks[i] = 'C'
    all_Blocks = list(multiset_permutations(Blocks))
    return all_Blocks


def check(grid, laz_co, direction):
    '''
    This function is used to check if the lazor and its next step
    is inside the grid, if it is not, return to the last step.

    **Parameters:**

        grid:*list,list,string*
            The grid contains a list of lists that can represent the grid
        laz_co:*tuple*
            Contains the current coordinate of the lazer point
        direction:*list*
            Contains the direction of the newest lazer

    **Returns**

        True if the lazer is still in the grid
    '''
    width = len(grid[0])
    length = len(grid)
    x = laz_co[0]
    y = laz_co[1]
    # print('width=' + str(width), length)
    # print('x=' + str(laz_co[0]), laz_co[1])
    if x < 0 or x > (width - 1) or \
        y < 0 or y > (length - 1) or \
        (x + direction[0]) < 0 or \
        (x + direction[0]) > (width - 1) or \
        (y + direction[1]) < 0 or \
            (y + direction[1]) > (length - 1):
        return True
    else:
        return False


def obvs_judge(lazorlist, gridfull_temp, possible_list, list_temp, holelist):
    '''
    This function can skip some obviously wrong grid

    **Parameters**

        lazorlist: *list*
            The list contains all the lasers. 

        gridfull_temp: *list*
            The grid about to be solved

        possible_list: *list
            All possible permutations of 'ABCo'.

        list_temp: *list*
            The permutation currently being used.

        holelist: *list*
            The positions of the end points

    **Return**

        None
    '''

    # any lazor is surrounded
    for ii in range(len(lazorlist)):
        if int(lazorlist[ii][0][1]) % 2 == 1:  # left&right
            x_temp, y_temp = lazorlist[ii][0][0], lazorlist[ii][0][1]
            if x_temp > 0 and x_temp != len(gridfull_temp[0])-1:
                if gridfull_temp[y_temp][x_temp - 1] and gridfull_temp[y_temp][x_temp + 1] in ['A', 'B']:
                    possible_list.remove(list_temp)
                    return False
                else:
                    return True
            if x_temp == 0:
                if gridfull_temp[y_temp][x_temp + 1] in ['A', 'B']:
                    possible_list.remove(list_temp)
                    return False
                else:
                    return True
            if x_temp == len(gridfull_temp[0])-1:
                if gridfull_temp[y_temp][x_temp - 1] in ['A', 'B']:
                    possible_list.remove(list_temp)
                    return False
                else:
                    return True

        if int(lazorlist[ii][0][1]) % 2 == 0:  # up&down
            x_temp, y_temp = lazorlist[ii][0][0], lazorlist[ii][0][1]
            if y_temp > 0 and y_temp != len(gridfull_temp)-1:
                if gridfull_temp[y_temp - 1][x_temp] and gridfull_temp[y_temp + 1][x_temp] in ['A', 'B']:
                    possible_list.remove(list_temp)
                    return False
                else:
                    return True
            if y_temp == 0:
                if gridfull_temp[y_temp + 1][x_temp] in ['A', 'B']:
                    possible_list.remove(list_temp)
                    return False
                else:
                    return True

            if y_temp == len(gridfull_temp) - 1:
                if gridfull_temp[y_temp - 1][x_temp] in ['A', 'B']:
                    possible_list.remove(list_temp)
                    return False
                else:
                    return True

    for jj in range(len(holelist)):
        x_hole = holelist[jj][1]
        y_hole = holelist[jj][0]
        if ((gridfull_temp[x_hole][y_hole + 1] in ['A', 'B']) and (gridfull_temp[x_hole][y_hole - 1] in ['A', 'B'])) or \
                ((gridfull_temp[x_hole + 1][y_hole] in ['A', 'B']) and (gridfull_temp[x_hole - 1][y_hole] in ['A', 'B'])):
            possible_list.remove(list_temp)
            return False
        else:
            return True


def grid_generation(grid, list_temp):
    '''
    This function can fill ABC into the grid.

    **Parameters**

        grid: *list*
            The full grid
        list_temp: *str*
            One possible arrangement

    **Return**

        grid: *list*
            The grid with blocks filled in
    '''
    list_temp_temp = copy.deepcopy(list_temp)
    gridfull_temp = copy.deepcopy(grid)
    for row in range(len(gridfull_temp)):
        for column in range(len(gridfull_temp[0])):
            if gridfull_temp[row][column] == 'o':
                gridfull_temp[row][column] = list_temp_temp.pop(0)
    # print(gridfull_temp)
    return gridfull_temp, list_temp


def solver(grid, init_laz_list, holelist, a, b, c, init_grid):
    """
    This function is the main function of the code, it uses
    the board we read and generated and the blocks we defined above.
    We first save all the points of the initial lazer and put the blocks
    on to the grid and save the new lazor path, this continues until we reach a
    hole, then the coordinate of this hole is removed from the hole list
    when there are no coordinates in the hole list, the loop ends and return
    the coordinate of each block.

    **Parameters**
    grid:*list,list,string*
        The grid contains a list of lists that can represent the grid.
    init_laz_list:*Array*
        The lazor contains the starting point coodinate and the direction
    of the lazors given.
    holelist:*list*
        The holelist contains all the holes' coordinates.
    """
    result = []
    grid_tuple = tuple(grid)
    # lazorlist = copy.deepcopy(lazorlist_save)
    coordination = (0, 0)
    direction = (0, 0)
    possible_list = inputblock(grid, a, b, c)
    print(len(possible_list))
    # print(lazorlist)
    num = 0
    test = True
    # When all the holes are filled, the loop ends, we also added an upper limit to the counter.
    while test:
        lazorlist = []
        p = 0
        for p in range(len(init_laz_list)):
            lazorlist.append([init_laz_list[p]])
        # L = len(possible_list)
        # ll = np.random.randint(0, L)
        # list_temp = possible_list[ll]
        list_temp = random.choice(possible_list)
        gridfull_temp, list_temp = grid_generation(grid, list_temp)
        # print(gridfull_temp)
        # # print(possible_list)
        # print(list_temp)
        # print(lazorlist)
        # print(holelist)
        if obvs_judge(lazorlist, gridfull_temp, possible_list, list_temp, holelist):
            num += 1
            for n in range(30):
                # The original lazor is added to the lazor list
                for k in range(len(lazorlist)):
                    coordination_x = lazorlist[k][-1][0]
                    coordination_y = lazorlist[k][-1][1]
                    direction_x = lazorlist[k][-1][2]
                    direction_y = lazorlist[k][-1][3]
                    coordination = [coordination_x, coordination_y]
                    direction = [direction_x, direction_y]
                    # Checking if the lazor and its next step is inside the boundary
                    if check(gridfull_temp, coordination, direction):
                        continue
                    else:
                        # Receiving the coordination & direction of lazor after a step
                        next_step = meet_block(
                            gridfull_temp, coordination, direction)
                        # If there are no elements in the list, it indicates it is block B
                        if len(next_step) == 0:
                            lazorlist[k].append([
                                coordination[0], coordination[1], 0, 0])
                            if (coordination in holelist) and (coordination not in result):
                                result.append(coordination)
                        # If there are 2 elements, it is "o" or A block
                        elif len(next_step) == 2:
                            direction = next_step
                            coordination = [
                                coordination[0] + direction[0], coordination[1] + direction[1]]
                            lazorlist[k].append(
                                [coordination[0], coordination[1], direction[0], direction[1]])
                            if (coordination in holelist) and (coordination not in result):
                                result.append(coordination)
                        # If there are 4 elements, it is C block, we seperate them and add the straight line to a new list in lazor list,
                        # and the other to the list under the original lazor
                        elif len(next_step) == 4:
                            direction = next_step
                            coordination_newlaz1 = [
                                coordination[0] + direction[0], coordination[1] + direction[1]]
                            coordination_newlaz2 = [
                                coordination[0] + direction[2], coordination[1] + direction[3]]
                            lazorlist.append(
                                [[coordination_newlaz1[0], coordination_newlaz1[1], direction[0], direction[1]]])
                            lazorlist[k].append(
                                [coordination_newlaz2[0], coordination_newlaz2[1], direction[2], direction[3]])
                            coordination = coordination_newlaz2
                            if (coordination in holelist) and (coordination not in result):
                                result.append(coordination)
                        else:
                            print('Wrong')
            if len(result) == len(holelist):
                test = False
                good_grid = []
                smallgrid = init_grid
                good_list = copy.deepcopy(list_temp)
                # print(list_temp)
                good_grid = copy.deepcopy(smallgrid)
                for row in range(len(good_grid)):
                    for column in range(len(good_grid[0])):
                        if good_grid[row][column] == 'o':
                            good_grid[row][column] = good_list.pop(0)
                print(len(possible_list))
                print(num)
                return gridfull_temp, lazorlist, list_temp, good_grid
            else:
                gridfull_temp = list(grid_tuple)
                # lazorlist = copy.deepcopy(lazorlist_save)
                possible_list.remove(list_temp)
                lazorlist = []
                result = []
                p = 0


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
    '''
    This function is to save the unsolved and solved board.
    "filename_board.png" and "filename_solved.png"
    The idea of the code come from the maze lab of the software carpentry class.

    ** Parameters **

        unsolved_board: *list*
            The unsolved grid 
        solved_board: *list
            The solved grid 
        filename: *str*
           The name of the file
        lazors_info: *list*
            Consisting of all origins and directions of the lazors
        holes: *list*
            Consisiting of the hole points
        stack_lazors: *list*
            Consisting of the lazor path for each lazor
        blocksize: *int*
            Size of the block of the board

    **Return**

            None
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
        # print(lazor_pos, lazor_dir)
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

    **Parameters**

        solved_board: *list*
            The solved grid
        answer_lazor: *list*
            The coordinations that lasers passed by
        filename: *str
            The name of the file
        lazors_info: *list*
            Consisting of all origins and directions of the lazors
        holes: *list*
            Consisiting of the hole points
        stack_lazors: *list*
            Consisting of the lazor path for each lazor
        blocksize: *int*
            Size of the blocks of the board

    ** Returns **

        None
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

        # for i in answer_lazor:
        #     end = [i[-1][0], i[-1][1]]
        #     while end not in holes:
        #         i.pop()
        #         end = [i[-1][0], i[-1][1]]

    for i in answer_lazor:
        for point in range(len(i)):
            co_start = (i[point][0] * blockSize / 2,
                        i[point][1] * blockSize / 2)
            if point + 1 < len(i):
                co_end = (i[point + 1][0] * blockSize / 2,
                            i[point + 1][1] * blockSize / 2)
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


def unit_test():
    # mad_1.bff
    fullgrid = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
    grid = [['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o']]
    A_blocks = 2
    B_blocks = 0
    C_blocks = 1
    lazorlist = [[2, 7, 1, -1]]
    holelist = [[3, 0], [4, 3], [2, 5], [4, 7]]
    solved_grid = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'C', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'A', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
    assert read_bff('mad_1.bff') == (fullgrid, A_blocks,
                                     B_blocks, C_blocks, lazorlist, holelist, grid)
    assert solver(fullgrid, lazorlist, holelist, A_blocks,
                  B_blocks, C_blocks, grid)[0] == solved_grid

    # mad_4.bff
    fullgrid = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
    grid = [['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o']]
    A_blocks = 5
    B_blocks = 0
    C_blocks = 0
    lazorlist = [[7, 2, -1, 1]]
    holelist = [[3, 4], [7, 4], [5, 8]]
    solved_grid = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'A', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'A', 'x', 'o', 'x', 'A', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'A', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
    assert read_bff('mad_4.bff') == (fullgrid, A_blocks,
                                     B_blocks, C_blocks, lazorlist, holelist, grid)
    assert solver(fullgrid, lazorlist, holelist, A_blocks,
                  B_blocks, C_blocks, grid)[0] == solved_grid

    # mad_7.bff
    fullgrid = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'x', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
    grid = [['o', 'o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o', 'x'],
            ['o', 'o', 'o', 'o', 'o'],
            ['o', 'o', 'o', 'o', 'o']]
    A_blocks = 6
    B_blocks = 0
    C_blocks = 0
    lazorlist = [[2, 1, 1, 1], [9, 4, -1, 1]]
    holelist = [[6, 3], [6, 5], [6, 7], [2, 9], [9, 6]]
    solved_grid = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'A', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'A', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'o', 'x', 'A', 'x', 'o', 'x', 'x', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'A', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'A', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
    assert read_bff('mad_7.bff') == (fullgrid, A_blocks,
                                     B_blocks, C_blocks, lazorlist, holelist, grid)
    assert solver(fullgrid, lazorlist, holelist, A_blocks,
                  B_blocks, C_blocks, grid)[0] == solved_grid

    # numbered_6.bff
    fullgrid = [['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'x', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x']]
    grid = [['o', 'o', 'o'],
            ['o', 'x', 'x'],
            ['o', 'o', 'o'],
            ['o', 'x', 'o'],
            ['o', 'o', 'o']]
    A_blocks = 3
    B_blocks = 3
    C_blocks = 0
    lazorlist = [[4, 9, -1, -1], [6, 9, -1, -1]]
    holelist = [[2, 5], [5, 0]]
    solved_grid = [['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'B', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'B', 'x', 'o', 'x', 'A', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'x', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'B', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x']]
    assert read_bff('numbered_6.bff') == (fullgrid, A_blocks,
                                          B_blocks, C_blocks, lazorlist, holelist, grid)
    assert solver(fullgrid, lazorlist, holelist, A_blocks,
                  B_blocks, C_blocks, grid)[0] == solved_grid

    # dark_1.bff
    fullgrid = [['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'x', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'x', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x']]
    grid = [['x', 'o', 'o'],
            ['o', 'o', 'o'],
            ['o', 'o', 'x']]
    A_blocks = 0
    B_blocks = 3
    C_blocks = 0
    lazorlist = [[3, 0, -1, 1], [1, 6, 1, -1], [3, 6, -1, -1], [4, 3, 1, -1]]
    holelist = [[0, 3], [6, 1]]
    solved_grid = [['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'x', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'B', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'B', 'x', 'B', 'x', 'x', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x']]
    assert read_bff('dark_1.bff') == (fullgrid, A_blocks,
                                      B_blocks, C_blocks, lazorlist, holelist, grid)
    assert solver(fullgrid, lazorlist, holelist, A_blocks,
                  B_blocks, C_blocks, grid)[0] == solved_grid

    # showstopper_4.bff
    fullgrid = [['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'B', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x']]
    grid = [['B', 'o', 'o'],
            ['o', 'o', 'o'],
            ['o', 'o', 'o']]
    A_blocks = 3
    B_blocks = 3
    C_blocks = 0
    lazorlist = [[3, 6, -1, -1]]
    holelist = [[2, 3]]
    solved_grid = [['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'B', 'x', 'A', 'x', 'B', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'B', 'x', 'o', 'x', 'A', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'o', 'x', 'B', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x']]
    assert read_bff('showstopper_4.bff') == (fullgrid, A_blocks,
                                             B_blocks, C_blocks, lazorlist, holelist, grid)
    assert solver(fullgrid, lazorlist, holelist, A_blocks,
                  B_blocks, C_blocks, grid)[0] == solved_grid

    # tiny_5.bff
    fullgrid = [['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'B', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x']]
    grid = [['o', 'B', 'o'],
            ['o', 'o', 'o'],
            ['o', 'o', 'o']]
    A_blocks = 3
    B_blocks = 0
    C_blocks = 1
    lazorlist = [[4, 5, -1, -1]]
    holelist = [[1, 2], [6, 3]]
    solved_grid = [['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'B', 'x', 'A', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'C', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x']]
    assert read_bff('tiny_5.bff') == (fullgrid, A_blocks,
                                      B_blocks, C_blocks, lazorlist, holelist, grid)
    assert solver(fullgrid, lazorlist, holelist, A_blocks,
                  B_blocks, C_blocks, grid)[0] == solved_grid

    # yarn_5.bff
    fullgrid = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'B', 'x', 'x', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'x', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'x', 'x', 'o', 'x', 'o', 'x', 'x', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'o', 'x', 'o', 'x', 'x', 'x', 'x', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                ['x', 'B', 'x', 'o', 'x', 'x', 'x', 'o', 'x', 'o', 'x'],
                ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
    grid = [['o', 'B', 'x', 'o', 'o'],
            ['o', 'o', 'o', 'o', 'o'],
            ['o', 'x', 'o', 'o', 'o'],
            ['o', 'x', 'o', 'o', 'x'],
            ['o', 'o', 'x', 'x', 'o'],
            ['B', 'o', 'x', 'o', 'o']]
    A_blocks = 8
    B_blocks = 0
    C_blocks = 0
    lazorlist = [[4, 1, 1, 1]]
    holelist = [[6, 9], [9, 2]]
    solved_grid = [['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'B', 'x', 'x', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'A', 'x', 'o', 'x', 'o', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'x', 'x', 'o', 'x', 'o', 'x', 'A', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'o', 'x', 'x', 'x', 'A', 'x', 'o', 'x', 'x', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'A', 'x', 'o', 'x', 'x', 'x', 'x', 'x', 'A', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'],
                   ['x', 'B', 'x', 'A', 'x', 'x', 'x', 'A', 'x', 'o', 'x'],
                   ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']]
    assert read_bff('yarn_5.bff') == (fullgrid, A_blocks,
                                      B_blocks, C_blocks, lazorlist, holelist, grid)
    assert solver(fullgrid, lazorlist, holelist, A_blocks,
                  B_blocks, C_blocks, grid)[0] == solved_grid


if __name__ == "__main__":

    t0 = time.time()
    open_start = time.time()
    read = read_bff('mad_1.bff')
    grid = read[0]
    a = read[1]
    b = read[2]
    c = read[3]
    lazorlist = read[4]
    holelist = read[5]
    smallgrid = read[6]
    open_end = time.time()

    answer = solver(grid=grid, init_laz_list=lazorlist,
                    holelist=holelist, a=a, b=b, c=c, init_grid=smallgrid)
    solved_grid = answer[0]
    solved_lazor = answer[1]
    solved_list = answer[2]
    small_solved_grid = answer[3]
    # print(solved_lazor)
    # print(small_solved_grid)
    t1 = time.time()

    print('reading %f seconds' % (open_end - open_start))
    print('solving all puzzles took %f seconds' % (t1 - t0))

    save_board(unsolved_board=smallgrid, lazors_info=lazorlist,
               holes=holelist, filename='mad_1.bff')
    save_answer_board(solved_board=small_solved_grid, answer_lazor=solved_lazor, lazors_info=lazorlist,
                      holes=holelist, filename='mad_1.bff')
