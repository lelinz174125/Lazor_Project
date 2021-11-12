# Lazor_Project: 
This is a project aiming at solving levels in the game 'LAZOR'
## Background
Lazor is a popular puzzle game which you need to arrange blocks wisely to achieve the goals in each level. You can get this game on [Steam](https://store.steampowered.com/app/341290/Lazors/), [Google play](https://play.google.com/store/apps/details?id=net.pyrosphere.lazors&hl=en_US&gl=US) or search it on App Store. Some of the levels are easy, but some of them can be really hard to solve. This project is to solve some of them.

## How to use it?
Get the .bff file of the level you want to solve or simply write one. A standard .bff should look like this:
```
GRID START
o o o o
o o o o
o o o o
o o o o
o o o o
GRID STOP

A 5

L 7 2 -1 1

P 3 4
P 7 4
P 5 8
```
The grid should be placed between **GRID STAR** and **GRID STOP**.
**A**: Reflect block.
**B**: Opaque block.
**C**: Refract block.
**L**: The first two numbers stand for the laser's start coordinates, the last two numbers stand for the laser's direction.
**P**: The positions that lazers need to intersect.

## How can this script help you solve the puzzle?
Here, we take 'yarn_5' for example. The snapshot of this level is 
![yarn_5_origin](https://assets/images/yarn_5_origin.jpg)

After running, you can get two picture named as 'yarn_5.png' and 'yarn_5_solved.png', which looks like 
![yarn_5](https://assets/images/yarn_5.png)
![yarn_5_solved](https://assets/images/yarn_5_solved.png)

## Contributors
This prohect exists thankls to all the people who contribure.

Mingze Zheng: mzheng15@jhu.edu, mzheng15

Bo Chao: bchao4@jhu.edu, bchao4

Lelin Zhong: lzhong6@jhu.edu, lzhong6