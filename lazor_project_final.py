from PIL import Image, ImageDraw
from sympy.utilities.iterables import multiset_permutations
import copy
import time


def read_bff(file_name):
    '''
    Extract imformation from '.bff' file

    **Parameters**

        file_name: *str*
            The full name of the file which has information to be extracted

    **Return**

        tuple: *list, int, int, int, list, list*
            Elements in the tuple are as follow:
                grid_full: *list*
                    The full grid in the form of a coordinate system
                A_num: *int*
                    The number of A-block available
                B_num: *int*
                    The number of B-block available
                C_num: *int*
                    The number of C-block available
                L_list: *list*
                    The first two elements is the positon of the start point, the last two elements are the direction.
                P_list: *list*
                    The positions of the end points
                grid_origin: *list*
                    The grid directly obtained from the '.bff' file
    '''
    # Initialize the parameters
    content = []  # Store the content
    grid = []
    grid_origin = []
    grid_temp = []
    A_num = 0  # Initialize A, B, C, L, P
    B_num = 0
    C_num = 0
    L_list = []
    P_list = []
    # Open and read the file
    with open(file_name, 'r') as f:
        # Get all the lines in the file
        lines = list(f)
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
            content.append(list(lines[i]))
    # Extract useful information
    for i in range(len(content)):
        for j in range(len(content[i])):
            # Set up some temporary lists
            A_temp = []
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

        # Get the raw grid from the file
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
    # Here are some troubleshooting for '.bff' files
    # Unreasonable block number
    if (A_num + B_num + C_num) == 0:
        raise Exception('There are no available block ABC')
    if (A_num + B_num + C_num) >= row * column:
        raise Exception('There are more blocks than available spaces')
    # No lasers
    if len(L_list) == 0:
        raise Exception('There are no lasors')
    for i in range(len(L_list)):
        # The format of the lasor is incorrect
        if len(L_list[i]) != 4:
            raise Exception('The format of the lasor is incorrect')
    # The start points of lasers are unreasonable
        if L_list[i][0] < 0 or L_list[i][0] > column * 2 or L_list[i][1] < 0 or L_list[i][1] > row * 2:
            raise Exception('The start point of lasors are out of the grid')
    # The directions of the lasors are unreasonable
        if (L_list[i][2] != -1 and L_list[i][2] != 1) or (L_list[i][3] != -1 and L_list[i][3] != 1):
            raise Exception('The directions of lasors are unreasonable')
    for i in range(len(P_list)):
        # The end points are unreasonable
        if P_list[i][0] < 0 or P_list[i][0] > column * 2 or P_list[i][1] < 0 or P_list[i][1] > row * 2:
            raise Exception('The end point of lasors are out of the grid')
    # No end points
    if len(P_list) == 0:
        raise Exception('There are no end points')

    # Any element other than 'ABCxo' in grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] not in ['x', 'o', 'A', 'B', 'C']:
                raise Exception('There are undefined characters in the grid')

    return gridfull, A_num, B_num, C_num, L_list, P_list, grid_origin


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


def save_answer_board(solved_board, answer_lazor, lazors_info, holes, filename, blockSize=100):
    '''
    This function is to save the unsolved and solved board.
    "filename_board.png" and "filename_solved.png"
    The idea of the code comes from the maze lab of the software carpentry class.

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

        The image of the correct answer
    '''

    nBlocksx = len(solved_board[0])
    nBlocksy = len(solved_board)
    dimx = nBlocksx * blockSize
    dimy = nBlocksy * blockSize
    colors = get_colors()

    # Verify that all values in the board are valid colors
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
        img_new = ImageDraw.Draw(img)
        img_new.ellipse([lazor_pos[0] * blockSize / 2 - 10, lazor_pos[1] * blockSize / 2 - 10,
                         lazor_pos[0] * blockSize / 2 + 10, lazor_pos[1] * blockSize / 2 + 10], fill=(255, 0, 0))

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

    # Name the result image
    if not filename.endswith(".png"):
        filename_new = '.'.join(filename.split(".")[0:-1])
        filename_new += "_solved.png"

    img.save("%s" % filename_new)


class Grid(object):

    def __init__(self, origrid):
        self.origrid = origrid
        self.length = len(origrid)
        self.width = len(origrid[0])

    def gen_grid(self, listgrid, position):
        '''
        This function can fill ABC block into the grid.

        **Parameters**

            grid: *list*
                The full grid
            list_temp: *str*
                One possible arrangement

        **Return**

            grid: *list*
                The grid with blocks filled in
        '''
        self.listgrid = listgrid
        for row in range(len(self.origrid)):
            for column in range(len(self.origrid[0])):
                if [row, column] not in position:
                    if self.origrid[row][column] != 'x':
                        self.origrid[row][column] = listgrid.pop(0)
        return self.origrid


class Lazor(object):

    def __init__(self, grid, lazorlist, holelist):
        self.grid = grid
        self.lazorlist = lazorlist
        self.holelist = holelist

    def meet_block(self, point, direction):
        '''
        If the laser is not currently at the boundary, this function will check whether 
        the laser interacts with a block and returns the new direction of the laser

        **Parameters**

            grid : *list*
                A list of list stand for a possible solution of the game
            point: *tuple*
                The current lazor point
            dirc: *tuple*
                The current direction of lazor

        **Return**

            new_dir: *list*
                A list that includes new directions of lazor
        '''
        self.point = point
        self.direction = direction
        # Calculate the next position of the laser
        x1, y1 = point[0], point[1] + direction[1]
        x2, y2 = point[0] + direction[0], point[1]
        # Obtain the block laser touches
        if point[0] & 1 == 1:
            block_type = self.grid[y1][x1]
            new_direction = self.new_dir(block_type)
        if point[0] & 1 == 0:
            block_type = self.grid[y2][x2]
            new_direction = self.new_dir(block_type)

        return new_direction

    def new_dir(self, block_type):
        '''
        This function is to achieve the role of different blocks

        **Parameters**

            block_type: *str*
                This represents different blocks
                'A': Reflect block
                'B': Opaque block
                'C': Refract block
                'o': Blank space

        **Return

            new_direction: *list*
                The new direction lasers head after meet a block
        '''
        self.type = block_type
        new_direction = []
        # When lasers touches the reflect block
        if self.type == 'A':
            if self.point[0] & 1 == 0:
                new_direction = [self.direction[0] * (-1), self.direction[1]]
            else:
                new_direction = [self.direction[0], self.direction[1] * (-1)]
        # When lasers touches the opaque block
        elif self.type == 'B':
            new_direction = []
        # When lasers touches the refract block
        elif self.type == 'C':
            if self.point[0] & 1 == 0:
                new_direction = [self.direction[0], self.direction[1],
                                 self.direction[0] * (-1), self.direction[1]]
            else:
                new_direction = [self.direction[0], self.direction[1],
                                 self.direction[0], self.direction[1] * (-1)]
        # When lasers touches the blank space
        elif self.type == 'o' or self.type == 'x':
            new_direction = self.direction

        return new_direction

    def check(self, laz_co, direction):
        '''
        This function is used to check if the laser and its next step
        is inside the grid, if not, return to the last step.

        **Parameters:**

            grid:*list*
                Contains a list of lists that can represent the grid
            laz_co:*tuple*
                Contains the current coordinate of the lazer point
            direction:*list*
                Contains the direction of the newest lazer

        **Returns**

            True if the lazer is still in the grid
        '''
        width = len(self.grid[0])
        length = len(self.grid)
        x = laz_co[0]
        y = laz_co[1]
        # Determine whether the position is in the grid
        if x < 0 or x > (width - 1) or y < 0 or y > (length - 1) or \
            (x + direction[0]) < 0 or \
            (x + direction[0]) > (width - 1) or \
            (y + direction[1]) < 0 or \
                (y + direction[1]) > (length - 1):
            return True
        else:
            return False

    def lazor_path(self):
        '''
        This function can return a list of the lasers path
        
        **Parameters**

            None

        **Return**

            lazorlist: *list*
                A list contains the positions lasers passed
        '''
        result = []
        lazorlist = []
        # Get the lasers' list from input and store them into lazorlist
        for p in range(len(self.lazorlist)):
            lazorlist.append([self.lazorlist[p]])
        # IMPORTANT!!!
        # 'n' here is to avoid infinite loop of laser in a circle
        # The range can be bigger, but the bigger it is, the slower the script runs
        # It cannot be too small because of the limitations of some levels
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
                if self.check(coordination, direction):
                    continue
                else:
                    # Receiving the coordination & direction of lazor after a step
                    next_step = self.meet_block(coordination, direction)
                    # If there are no elements in the list, it indicates it is block B
                    if len(next_step) == 0:
                        lazorlist[k].append([
                            coordination[0], coordination[1], 0, 0])
                        if (coordination in self.holelist) and (coordination not in result):
                            result.append(coordination)
                    # If there are 2 elements, it is "o" or A block
                    elif len(next_step) == 2:
                        direction = next_step
                        coordination = [
                            coordination[0] + direction[0], coordination[1] + direction[1]]
                        lazorlist[k].append(
                            [coordination[0], coordination[1], direction[0], direction[1]])
                        if (coordination in self.holelist) and (coordination not in result):
                            result.append(coordination)
                    # If there are 4 elements, it is C block, we seperate them and add the straight line to a new list in lazor list,
                    # and the other to the list under the original lazor
                    elif len(next_step) == 4:
                        direction = next_step
                        coordination_newlaz1 = [
                            coordination[0] + direction[0], coordination[1] + direction[1]]
                        coordination_newlaz2 = [
                            coordination[0], coordination[1]]
                        lazorlist.append(
                            [[coordination_newlaz1[0], coordination_newlaz1[1], direction[0], direction[1]]])
                        lazorlist[k].append(
                            [coordination_newlaz2[0], coordination_newlaz2[1], direction[2], direction[3]])
                        coordination = coordination_newlaz2
                        if (coordination in self.holelist) and (coordination not in result):
                            result.append(coordination)
                    else:
                        print('Wrong')
        if len(result) == len(self.holelist):
            return lazorlist
        else:
            return 0


def obvs_judge(lazorlist, gridfull_temp, possible_list, list_temp, holelist):
    '''
    This function can skip some obviously wrong grids generated

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

    # Any laser or hole that is surrounded by 'A' or 'B' blocks can not have a result , thus we
    # rule them out
    for ii in range(len(lazorlist)):
        if int(lazorlist[ii][1]) % 2 == 1:  # Suitable for blocks blocking left&right
            x_temp, y_temp = lazorlist[ii][0], lazorlist[ii][1]
            if x_temp > 0 and x_temp != len(gridfull_temp[0])-1:
                if gridfull_temp[y_temp][x_temp - 1] and gridfull_temp[y_temp][x_temp + 1] in ['A', 'B']:
                    return False
                else:
                    return True
            if x_temp == 0:
                if gridfull_temp[y_temp][x_temp + 1] in ['A', 'B']:
                    return False
                else:
                    return True
            if x_temp == len(gridfull_temp[0])-1:
                if gridfull_temp[y_temp][x_temp - 1] in ['A', 'B']:
                    return False
                else:
                    return True

        if int(lazorlist[ii][1]) % 2 == 0:  # Suitable for blocks blocking up&down
            x_temp, y_temp = lazorlist[ii][0], lazorlist[ii][1]
            if y_temp > 0 and y_temp != len(gridfull_temp)-1:
                if gridfull_temp[y_temp - 1][x_temp] and gridfull_temp[y_temp + 1][x_temp] in ['A', 'B']:
                    return False
                else:
                    return True
            if y_temp == 0:
                if gridfull_temp[y_temp + 1][x_temp] in ['A', 'B']:
                    return False
                else:
                    return True

            if y_temp == len(gridfull_temp) - 1:
                if gridfull_temp[y_temp - 1][x_temp] in ['A', 'B']:
                    return False
                else:
                    return True

    for jj in range(len(holelist)): # Ruling out grids that have blocks blocking a hole
        x_hole = holelist[jj][1]
        y_hole = holelist[jj][0]
        if ((gridfull_temp[x_hole][y_hole + 1] in ['A', 'B']) and (gridfull_temp[x_hole][y_hole - 1] in ['A', 'B'])) or \
                ((gridfull_temp[x_hole + 1][y_hole] in ['A', 'B']) and (gridfull_temp[x_hole - 1][y_hole] in ['A', 'B'])):
            possible_list.remove(list_temp)
            return False
        else:
            return True


def find_path(grid, A_num, B_num, C_num, lazorlist, holelist, position):
    '''
    Generate a possible grid with blocks filled in and solves it, if it is the right grid, we return all the necessary parameters of the grid

    **Parameters**

        Grid: *list*
            The full grid in the form of a coordinate system
        A_num: *int*
            The number of A-block available
        B_num: *int*
            The number of B-block available
        C_num: *int*
            The number of C-block available
        lazorlist: *list*
            The first two elements is the positon of the start point, the last two elements are the direction.
        holelist: *list*
            The positions of the end points   
        position: *list*
            A list store the pre-placed blocks
    
    **Return**

        solution: *list*
            The positions and directions laser passed
        list_temp_save: *list*
            One possible permutation of blocks
        test_board: *list*
            The full grid in coordination
    '''
    Blocks = []
    # Wxtract the blank positions and replace them with blocks
    for a in grid:
        for b in a:
            if b == 'o':
                Blocks.append(b)
    for i in range(A_num):
        Blocks[i] = 'A'
    for i in range(A_num, (A_num + B_num)):
        Blocks[i] = 'B'
    for i in range((A_num + B_num), (A_num + B_num + C_num)):
        Blocks[i] = 'C'
    # Generate a list of permutations of blocks and blank postion
    list_Blocks = list(multiset_permutations(Blocks))

    while len(list_Blocks) != 0:
        list_temp = list_Blocks[-1]
        list_temp_save = copy.deepcopy(list_temp)
        list_Blocks.pop()
        # Generate a board from grid function
        ori_grid = Grid(grid)
        test_board = ori_grid.gen_grid(list_temp,position)
        # Test the board with obvs_judge and run it through Lazor to see if it is the right board
        if obvs_judge(lazorlist, test_board, list_Blocks, list_temp, holelist):
            lazor = Lazor(test_board, lazorlist, holelist)
            solution = lazor.lazor_path()
            # We retunr 0 if the board is wrong and return a list with the path of lazors if its right.
            if solution != 0:
                return solution, list_temp_save, test_board
            else:
                continue


def find_fixed_block(smallgrid):
    '''
    This function looks for blocks that were in the original board so that we wouldn't replace it when generating grids

    **Parameters**

        smallgrid: *list*
            This is the orignial grid provided by the .bff file

    **Return**

        position: *list*
            The coordination of the fixed blocks provided by the game

    '''
    position = []
    for i in range(len(smallgrid)):
        for j in range(len(smallgrid[0])):
            block = smallgrid[i][j]
            if block == 'A' or block == 'B' or block=='C':
                position.append([i*2+1,j*2+1])
    return position


def solver(fptr):
    '''
    This function provides all the necessary parameters of the correct grid and generates a picture of the result 

    **Parameters**

        fptr: *str*
            This is the .bff file name you want to run.

    **Return**

        good_grid: *list*
            The correct grid
        answer: *list*
            A list contains all the position lasers passed and the direction they head
        lazor: *list*
            The correct grid but every element in one list
    '''

    # We read the .bff file and obatin the grid that we filled with 'x' for coordination, 
    # the number of a,b,c, the original lasor list, the hole list and the original grid
    read = read_bff(fptr)
    grid = read[0]
    a = read[1]
    b = read[2]
    c = read[3]
    lazorlist = read[4]
    holelist = read[5]
    smallgrid = read[6]
    # We find out the coordination of blocks that are fixed
    position = find_fixed_block(smallgrid)
    # We find out the lasor pathway and permutation of the correct grid
    answer, lazor = find_path(grid, a, b, c, lazorlist, holelist, position)[:2]
    # We generate the orignial board filled with the correct lazor path
    good_list = copy.deepcopy(lazor)
    good_grid = copy.deepcopy(smallgrid)
    for row in range(len(good_grid)):
        for column in range(len(good_grid[0])):
            if good_grid[row][column] == 'o':
                good_grid[row][column] = good_list.pop(0)
    # We save and generate a picture for the solve
    save_answer_board(solved_board=good_grid, answer_lazor=answer, lazors_info=lazorlist,
                      holes=holelist, filename=fptr)
    answer_pic_name = '.'.join(fptr.split('.')[0:-1])
    print('Success! The answer is saved as {}'. format(answer_pic_name + '_solved.png'))
    return(good_grid, answer, lazor)


if __name__ == "__main__":
    t0 = time.time()
    # solver('dark_1.bff')
    # solver('mad_1.bff')
    # solver('mad_4.bff')
    # solver('mad_7.bff')
    # solver('numbered_6.bff')
    # solver('showstopper_4.bff')
    # solver('tiny_5.bff')
    solver('mad_7.bff')
    t1 = time.time()
    print(t1 - t0)
