# Lazor_Project
This is a project aiming at solving levels in the game 'LAZOR'
## Background
Lazor is a popular puzzle game in which you need to arrange blocks wisely to achieve the goals at each level. You can get this game on [Steam](https://store.steampowered.com/app/341290/Lazors/), [Google play](https://play.google.com/store/apps/details?id=net.pyrosphere.lazors&hl=en_US&gl=US), or search it on App Store. Some of the levels are easy, but some of them can be hard to solve. This project is to solve some of them.

## How to use it?
Get the .bff file of the level you want to solve or simply write one. A standard .bff should look like this:  
***The following demonstration content does not represent the actual level***
```
GRID START
o o o o
o o o o
o o x o
o o o o
o o o o
GRID STOP

A 1
B 2
C 3

L 7 2 -1 1

P 3 4
P 7 4
P 5 8
```
The grid should be placed between **GRID START** and **GRID STOP**.  
**A**: Reflect block  
**B**: Opaque block  
**C**: Refract block  
**L**: The first two numbers stand for the laser's start coordinates, the last two numbers stand for the laser's direction.  
**P**: The positions that lazers need to intersect.  

## How can this script help you solve the puzzle?
This script can solve puzzles ***really*** fast.  
Here, we take 'yarn_5' for example. The snapshot of this level is  


<img width="375" height="802.08" src=https://github.com/lelinz174125/Lazor_Project/blob/main/IMG/yarn_5_origin.jpg>

After running, you can get the answer picture named as 'yarn_5_solved.png', which looks like   


<img width="375" height="450" src=https://github.com/lelinz174125/Lazor_Project/blob/main/IMG/yarn_5_solved.png>   


Or for level mad_1, the answer looks like:    


<img width="375" height="375" src=https://github.com/lelinz174125/Lazor_Project/blob/main/IMG/mad_1_solved.png>  
  

**White Block**: Reflect block  
**Black Block**: Opaque block  
**Red Block**: Refract block  
**Lighter Gray Block**: The location where the block can be placed  
**Darker Gray Block**: The location where the block cannot be placed.  
**Hollow Red Circle**: The end point the laser needs to pass.  
**Solid Red Circle**: The place where the laser is emitted.  
**Red Line**: The optical path of the laser.  


## Contributors
This project exists thanks to all the people who contribute.  
Mingze Zheng: mzheng15@jhu.edu, mzheng15  
Bo Chao: bchao4@jhu.edu, bchao4  
Lelin Zhong: lzhong6@jhu.edu, lzhong6