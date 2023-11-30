# Meepo is You

<img src="https://github.com/clarencechau/Meepo-Is-You/blob/main/readmepictures/game.png?raw=true" width="500" height="500" />

## Game Description

Meepo is You is a project in Python I did in university, based on popular puzzle game Baba is You. The goal of the game is to get the character (Meepo) to the red finish flag, by going through different obstacles and rooms, but with a catch. Everything object in the game is naturally static and immobile: from the walls, to the finish flag, to even the character being played. So how do we interact with the character and objects then? Command blocks. Every map is filled with three different types of command blocks with words inside them: object word blocks, IS blocks, and verb blocks. Moving one of each of these blocks in a row, will affect the functionality of the object in the game.

<div style="display: flex; justify-content: space-between;">
    <img src="https://github.com/clarencechau/Meepo-Is-You/blob/main/readmepictures/wallispush.png?raw=true" width="200" height="200" />
    <img src="https://github.com/clarencechau/Meepo-Is-You/blob/main/readmepictures/pushedwall.png?raw=true" width="200" height="200" />
</div>

For example, walls in the game are naturally static, and can not be pushed. Pushing command blocks to make a combination of WALL, IS, and PUSH, will make all the walls in the game pushable, allowing Meepo to get closer to the finish flag. This is one of many combinations the user can play around with in the game, ranging from pushing objects, stopping objects, to even losing the game when touching an object. Below are all the available command blocks available in the game.

<div style="display: flex; justify-content: space-between;">
    <img src="https://github.com/clarencechau/Meepo-Is-You/blob/main/readmepictures/objects.png?raw=true" width="200" height="70" />
    <img src="https://github.com/clarencechau/Meepo-Is-You/blob/main/readmepictures/isblock.png?raw=true" width="100" height="70" />
    <img src="https://github.com/clarencechau/Meepo-Is-You/blob/main/readmepictures/verbblock.png?raw=true" width="200" height="70" />
</div>

## Instructions

* Use the arrow keys to move your current character
* Ctrl + Z to undo your last move
  * Can be done as many times as the user
  * Must use when the YOU block isn't in a combination, as the game can't assign the user to an object
  * Used a LIFO list to easily track and remove moves
