from typing import Any, Type, Tuple, List, Sequence, Optional
import pygame
from settings import *
from stack import Stack
import actor

class Game:
    """
    Class representing the game.
    """
    size: Tuple[int, int]
    width: int
    height: int
    screen: Optional[pygame.Surface]
    x_tiles: int
    y_tiles: int
    tiles_number: Tuple[int, int]
    background: Optional[pygame.Surface]

    _actors: List[actor.Actor]
    _is: List[actor.Is]
    _running: bool
    _rules: List[str]
    _history: Stack

    player: Optional[actor.Actor]
    map_data: List[str]
    keys_pressed: Optional[Sequence[bool]]
    forbidden_list: List[str]

    def __init__(self) -> None:
        """
        Initialize variables for this Class.
        """
        self.width, self.height = 0, 0
        self.size = (self.width, self.height)
        self.screen = None
        self.x_tiles, self.y_tiles = (0, 0)
        self.tiles_number = (self.x_tiles, self.y_tiles)
        self.background = None

        self._actors = []
        self._is = []
        self._running = True
        self._rules = []
        self._history = Stack()

        self.player = None
        self.map_data = []
        self.keys_pressed = None
        self.forbidden_list = []

    def load_map(self, path: str) -> None:
        """
        Reads a .txt file representing the map
        """
        with open(path, 'rt') as f:
            for line in f:
                self.map_data.append(line.strip())

        self.width = (len(self.map_data[0])) * TILESIZE
        self.height = len(self.map_data) * TILESIZE
        self.size = (self.width, self.height)
        self.x_tiles, self.y_tiles = len(self.map_data[0]), len(self.map_data)

        # center the window on the screen
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def new(self) -> None:
        """
        Initialize variables to be object on screen.
        """
        self.screen = pygame.display.set_mode(self.size)
        self.background = pygame.image.load(
            "{}/backgroundBig.png".format(SPRITES_DIR)).convert_alpha()
        for col, tiles in enumerate(self.map_data):
            for row, tile in enumerate(tiles):
                if tile.isnumeric():
                    self._actors.append(
                        Game.get_character(CHARACTERS[tile])(row, col))
                elif tile in SUBJECTS:
                    self._actors.append(
                        actor.Subject(row, col, SUBJECTS[tile]))
                elif tile in ATTRIBUTES:
                    self._actors.append(
                        actor.Attribute(row, col, ATTRIBUTES[tile]))
                elif tile == 'I':
                    is_tile = actor.Is(row, col)
                    self._is.append(is_tile)
                    self._actors.append(is_tile)

    def get_actors(self) -> List[actor.Actor]:
        """
        Getter for the list of actors
        """
        return self._actors

    def get_is(self) -> List[actor.Is]:
        """
        Getter for the list of Is blocks
        """
        return self._is

    def get_running(self) -> bool:
        """
        Getter for _running
        """
        return self._running

    def get_rules(self) -> List[str]:
        """
        Getter for _rules
        """
        return self._rules

    def get_history(self) -> Stack:
        """
        Getter for _history
        """
        return self._history

    def get_keys_pressed(self) -> Optional[Sequence[bool]]:
        """
        Getter for keys_pressed
        """
        return self.keys_pressed

    def get_player(self):
        """
        Getter for player
        """
        return self.player

    def _draw(self) -> None:
        """
        Draws the screen, grid, and objects/players on the screen
        """
        self.screen.blit(self.background,
                         (((0.5 * self.width) - (0.5 * 1920),
                           (0.5 * self.height) - (0.5 * 1080))))
        for actor_ in self._actors:
            rect = pygame.Rect(actor_.x * TILESIZE,
                               actor_.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(actor_.image, rect)

        # Blit the player at the end to make it above all other objects
        if self.player:
            rect = pygame.Rect(self.player.x * TILESIZE,
                               self.player.y * TILESIZE, TILESIZE, TILESIZE)
            self.screen.blit(self.player.image, rect)

        pygame.display.flip()

    def _events(self) -> None:
        """
        Event handling of the game window
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            # Allows us to make each press count as 1 movement.
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed = pygame.key.get_pressed()
                ctrl_held = self.keys_pressed[pygame.K_LCTRL]

                # handle undo button and player movement here
                if event.key == pygame.K_z and ctrl_held:  # Ctrl-Z
                    self._undo()
                else:
                    if self.player is not None:
                        assert isinstance(self.player, actor.Character)
                        save = self._copy()
                        if self.player.player_move(self) \
                                and not self.win_or_lose():
                            self._history.push(save)
        return

    def win_or_lose(self) -> bool:
        """
        Check if the game has won or lost
        Returns True if the game is won or lost; otherwise return False
        """
        assert isinstance(self.player, actor.Character)
        for ac in self._actors:
            if isinstance(ac, actor.Character) \
                    and ac.x == self.player.x and ac.y == self.player.y:
                if ac.is_win():
                    self.win()
                    return True
                elif ac.is_lose():
                    self.lose(self.player)
                    return True
        return False

    def run(self) -> None:
        """
        Run the Game until it ends or player quits.
        """
        while self._running:
            pygame.time.wait(1000 // FPS)
            self._events()
            self._update()
            self._draw()

    def set_player(self, actor_: Optional[actor.Actor]) -> None:
        """
        Takes an actor and sets that actor to be the player
        """
        self.player = actor_

    def remove_player(self, actor_: actor.Actor) -> None:
        """
        Remove the given <actor> from the game's list of actors.
        """
        self._actors.remove(actor_)
        self.player = None

    def _update(self) -> None:
        """
        Check each "Is" tile to find what rules are added and which are removed
        if any, and handle them accordingly.
        """
        delete_list = []
        for rule in self._rules:
            if rule == '':
                self._rules.remove('')
        for is_block in self._is:  # adds rules in _rule list
            x_cord = is_block.x
            y_cord = is_block.y
            up = self.get_actor(x_cord, y_cord - 1)
            down = self.get_actor(x_cord, y_cord + 1)
            right = self.get_actor(x_cord + 1, y_cord)
            left = self.get_actor(x_cord - 1, y_cord)
            tup = is_block.update(up, down, left, right)
            string1 = tup[0]
            string2 = tup[1]
            delete_list.append(string1)
            delete_list.append(string2)
            if string1 not in self._rules:
                self._rules.append(string1)
            if string2 not in self._rules:
                self._rules.append(string2)
        for rule in self._rules:  # deletes rules that have been removed
            if rule not in delete_list:
                if rule != '':
                    subject = rule[0: rule.find(' ')]
                    attribute = rule[rule.find(' ') + 3:]
                    act = self.get_character(subject)
                    self.unset_action(act, attribute)
                self._rules.remove(rule)
        for i, rule in enumerate(self._rules):  # applies the rules
            if rule != '':
                subject = rule[0: rule.find(' ')]
                attribute = rule[rule.find(' ') + 3:]
                act = self.get_character(subject)
                self.set_action(act, attribute)

    def set_action(self, act: Optional[Type[Any]],
                   attribute: str) -> None:
        """
        Sets the action of the rule
        """
        for actors in self._actors:
            if isinstance(actors, act):
                if attribute == 'You':
                    self.set_player(actors)
                if attribute == 'Push':
                    actor.Character.set_push(actors)
                if attribute == 'Stop':
                    actor.Character.set_stop(actors)
                if attribute == 'Victory':
                    actor.Character.set_win(actors)
                if attribute == 'Lose':
                    actor.Character.set_lose(actors)

    def unset_action(self, act: Optional[Type[Any]], attribute: str) \
            -> Optional[Type[Any]]:
        """
        Unsets the action of the rule
        """
        for actors in self._actors:
            if isinstance(actors, act):
                if attribute == 'You':
                    self.set_player(None)
                if attribute == 'Push':
                    actor.Character.unset_push(actors)
                if attribute == 'Stop':
                    actor.Character.unset_stop(actors)
                if attribute == 'Victory':
                    actor.Character.unset_win(actors)
                if attribute == 'Lose':
                    actor.Character.unset_lose(actors)
        return None

    @staticmethod
    def get_character(subject: str) -> Optional[Type[Any]]:
        """
        Takes a string, returns appropriate class representing that string
        """
        if subject == "Meepo":
            return actor.Meepo
        elif subject == "Wall":
            return actor.Wall
        elif subject == "Rock":
            return actor.Rock
        elif subject == "Flag":
            return actor.Flag
        elif subject == "Bush":
            return actor.Bush
        return None

    def _undo(self) -> None:
        """
        Returns the game to a previous state based on what is at the top of the
        _history stack.
        """
        if not self._history.is_empty():
            old_game = self._history.pop()
            self._actors = old_game.get_actors()
            self._rules = old_game.get_rules()
            self._is = old_game.get_is()

    def _copy(self) -> 'Game':
        """
        Copies relevant attributes of the game onto a new instance of Game.
        Return new instance of game
        """
        game_copy = Game()
        for act in self._actors:
            if isinstance(act, actor.Is):
                act.copy()
        for act in self._actors:
            c = act.copy()
            game_copy._actors.append(c)
        for rule in self._rules:
            game_copy._rules.append(rule)
        for is_block in self._is:
            c = is_block.copy()
            game_copy._is.append(c)
        return game_copy

    def get_actor(self, x: int, y: int) -> Optional[actor.Actor]:
        """
        Return the actor at the position x,y. If the slot is empty, Return None
        """
        for ac in self._actors:
            if ac.x == x and ac.y == y:
                return ac
        return None

    def win(self) -> None:
        """
        End the game and print win message.
        """
        self._running = False
        print("Congratulations, you won!")

    def lose(self, char: actor.Character) -> None:
        """
        Lose the game and print lose message
        """
        self.remove_player(char)
        print("You lost! But you can have it undone if undo is done :)")


if __name__ == "__main__":

    game = Game()
    # load_map public function
    game.load_map(MAP_PATH)
    game.new()
    game.run()
