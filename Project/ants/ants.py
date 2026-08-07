"""CS 61A presents Ants Vs. SomeBees."""

import random
from abc import ABC
from collections import OrderedDict
from typing import ClassVar, Never, Never, override

from ucb import interact, main, trace

################
# Core Classes #
################


class Place:
    """A Place holds insects and has an exit to another Place."""
    is_hive: ClassVar[bool] = False

    def __init__(self, name: str, exit: 'Place | None'=None):
        """Create a Place with the given NAME and EXIT.

        name -- A string; the name of this Place.
        exit -- The Place reached by exiting this Place (may be None).
        """
        self.name: str = name
        self.exit: Place | None = exit
        self.bees: list[Bee] = []        # A list of Bees
        self.ant: Ant | None = None       # An Ant
        self.entrance: Place | None = None  # A Place
        # Phase 1: Add an entrance to the exit
        # BEGIN Problem 2
        if isinstance(exit, Place):
            exit.entrance = self
        # END Problem 2

    def add_insect(self, insect: 'Insect') -> None:
        """Asks the insect to add itself to this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.add_to(self)

    def remove_insect(self, insect: 'Insect') -> None:
        """Asks the insect to remove itself from this place. This method exists so
        that it can be overridden in subclasses.
        """
        insect.remove_from(self)

    @override
    def __str__(self):
        return self.name


class Insect(ABC):
    """An Insect, the base class of Ant and Bee, has health and a Place."""

    next_id: ClassVar[int] = 0  # Every insect gets a unique id number
    damage: float = 0
    # ADD CLASS ATTRIBUTES HERE
    is_waterproof: ClassVar[bool] = False

    def __init__(self, health: float, place: Place | None=None):
        """Create an Insect with a health amount and a starting PLACE."""
        self.health: float = health
        self.place: Place | None = place

        # assign a unique ID to every insect
        self.id: int = Insect.next_id
        Insect.next_id += 1

    def reduce_health(self, amount: float) -> None:
        """Reduce health by AMOUNT, and remove the insect from its place if it
        has no health remaining.

        >>> test_insect = Insect(5)
        >>> test_insect.reduce_health(2)
        >>> test_insect.health
        3
        """
        self.health -= amount
        if self.health <= 0:
            self.zero_health_callback()
            self.place.remove_insect(self)

    def action(self, gamestate: 'GameState') -> None:  # pyright: ignore[reportUnusedParameter]
        """The action performed each turn."""

    def zero_health_callback(self) -> None:
        """Called when health reaches 0 or below."""

    def add_to(self, place: Place) -> None:
        self.place = place

    def remove_from(self, place: Place) -> None:  # pyright: ignore[reportUnusedParameter]
        self.place = None

    @override
    def __repr__(self):
        cname: str = type(self).__name__
        return f'{cname}({self.health}, {self.place})'


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    implemented: ClassVar[bool] = False  # Only implemented Ant classes should be instantiated
    food_cost: ClassVar[int] = 0
    is_container: ClassVar[bool] = False
    # ADD CLASS ATTRIBUTES HERE
    blocks_path: ClassVar[bool] = True

    def __init__(self, health: float=1):
        super().__init__(health)
        self.is_doubled: bool = False

    def can_contain(self, other: 'Ant') -> bool:  # pyright: ignore[reportUnusedParameter]
        return False

    def store_ant(self, other: 'Ant') -> None:  # pyright: ignore[reportUnusedParameter]
        assert False, f"{self} cannot contain an ant"

    def remove_ant(self, other: 'Ant') -> None:  # pyright: ignore[reportUnusedParameter]
        assert False, f"{self} cannot contain an ant"

    @override
    def add_to(self, place: Place) -> None:
        if place.ant is None:
            place.ant = self
        else:
            # BEGIN Problem 8b
            if place.ant.is_container and place.ant.can_contain(self):
                place.ant.store_ant(self)
            elif self.is_container and self.can_contain(place.ant):
                self.store_ant(place.ant)
                place.ant = self
            else:
                assert place.ant is None, f'Too many ants in {place}'
            # END Problem 8b
        Insect.add_to(self, place)

    @override
    def remove_from(self, place: Place) -> None:
        if place.ant is self:
            place.ant = None
        elif place.ant is None:
            assert False, f'{self} is not in {place}'
        else:
            place.ant.remove_ant(self)
        Insect.remove_from(self, place)

    def double(self) -> None:
        """Double this ants's damage, if it has not already been doubled."""
        # BEGIN Problem 12
        if not self.is_doubled:
            self.damage *= 2
            self.is_doubled = True
        # END Problem 12


class HarvesterAnt(Ant):
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name: ClassVar[str] = 'Harvester'
    implemented: ClassVar[bool] = True
    # OVERRIDE CLASS ATTRIBUTES HERE
    food_cost: ClassVar[int] = 2

    @override
    def action(self, gamestate: 'GameState') -> None:
        """Produce 1 additional food for the colony.

        gamestate -- The GameState, used to access game state information.
        """
        # BEGIN Problem 1
        gamestate.food += 1
        # END Problem 1


class ThrowerAnt(Ant):
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""

    name: ClassVar[str] = 'Thrower'
    implemented: ClassVar[bool] = True
    damage: float = 1
    # ADD/OVERRIDE CLASS ATTRIBUTES HERE
    food_cost: ClassVar[int] = 3
    lower_bound: ClassVar[float] = 0
    upper_bound: ClassVar[float] = float('inf')

    def nearest_bee(self) -> 'Bee | None':
        """Return the nearest Bee in a Place (that is not the hive) connected to
        the ThrowerAnt's Place by following entrances.

        This method returns None if there is no such Bee (or none in range).
        """
        # BEGIN Problem 3 and 4
        bee: Bee | None = None
        place: Place | None = self.place
        i: int = 0
        while place is not None and not place.is_hive and i <= self.upper_bound:
            if i >= self.lower_bound:
                bee = random_bee(place.bees)
                if bee is not None:
                    return bee
            place = place.entrance
            i += 1
        return None
        # END Problem 3 and 4

    def throw_at(self, target: 'Bee | None') -> None:
        """Throw a leaf at the target Bee, reducing its health."""
        if target is not None:
            target.reduce_health(self.damage)

    @override
    def action(self, gamestate: 'GameState') -> None:
        """Throw a leaf at the nearest Bee in range."""
        self.throw_at(self.nearest_bee())


def random_bee(bees: 'list[Bee]') -> 'Bee | None':
    """Return a random bee from a list of bees, or return None if bees is empty."""
    assert isinstance(bees, list), \
        "random_bee's argument should be a list but was a %s" % type(bees).__name__
    if bees:
        return random.choice(bees)

##############
# Extensions #
##############


class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name: ClassVar[str] = 'Short'
    food_cost: ClassVar[int] = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    upper_bound: ClassVar[float] = 3
    # BEGIN Problem 4
    implemented: ClassVar[bool] = True   # Change to True to view in the GUI
    # END Problem 4


class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name: ClassVar[str] = 'Long'
    food_cost: ClassVar[int] = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    lower_bound: ClassVar[float] = 5
    # BEGIN Problem 4
    implemented: ClassVar[bool] = True   # Change to True to view in the GUI
    # END Problem 4


class FireAnt(Ant):
    """FireAnt cooks any Bee in its Place when it expires."""

    name: ClassVar[str] = 'Fire'
    damage: float = 3
    food_cost: ClassVar[int] = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 5
    implemented: ClassVar[bool] = True   # Change to True to view in the GUI
    # END Problem 5

    def __init__(self, health: float=3):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)

    @override
    def reduce_health(self, amount: float) -> None:
        """Reduce health by AMOUNT, and remove the FireAnt from its place if it
        has no health remaining.

        Make sure to reduce the health of each bee in the current place, and apply
        the additional damage if the fire ant dies.
        """
        # BEGIN Problem 5
        bees: list[Bee] = list(self.place.bees)
        for bee in bees:
            bee.reduce_health(amount)
        super().reduce_health(amount)
        # END Problem 5

    @override
    def zero_health_callback(self) -> None:
        bees: list[Bee] = list(self.place.bees)
        for bee in bees:
            bee.reduce_health(self.damage)
        super().zero_health_callback()

# BEGIN Problem 6
# The WallAnt class
class WallAnt(Ant):
    name: ClassVar[str] = 'Wall'
    implemented: ClassVar[bool] = True
    food_cost: ClassVar[int] = 4

    def __init__(self, health: float=4):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)
# END Problem 6

# BEGIN Problem 7
# The HungryAnt Class
class HungryAnt(Ant):
    name: ClassVar[str] = 'Hungry'
    implemented: ClassVar[bool] = True
    food_cost: ClassVar[int] = 4
    chew_cooldown: ClassVar[int] = 3

    def __init__(self, health: float=1):
        """Create an Ant with a HEALTH quantity."""
        self.cooldown: int = 0
        super().__init__(health)

    @override
    def action(self, gamestate: 'GameState') -> None:
        """Eat a bee in its place."""
        if self.cooldown > 0:
            self.cooldown -= 1
        else:
            bee: Bee | None = random_bee(self.place.bees)
            if bee is not None:
                bee.reduce_health(bee.health)
                self.cooldown = self.chew_cooldown
# END Problem 7


class ContainerAnt(Ant):
    """
    ContainerAnt can share a space with other ants by containing them.
    """
    is_container: ClassVar[bool] = True

    def __init__(self, health: float):
        super().__init__(health)
        self.ant_contained: Ant | None = None

    @override
    def can_contain(self, other: Ant) -> bool:
        # BEGIN Problem 8a
        return self.ant_contained is None and not other.is_container
        # END Problem 8a

    @override
    def store_ant(self, other: Ant) -> None:
        # BEGIN Problem 8a
        if self.can_contain(other):
            self.ant_contained = other
        # END Problem 8a

    @override
    def remove_ant(self, other: Ant) -> None:
        if self.ant_contained is not other:
            assert False, f"{self} does not contain {other}"
        self.ant_contained = None

    @override
    def remove_from(self, place: Place) -> None:
        # Special handling for container ants
        if place.ant is self:
            # Container was removed. Contained ant should remain in the game
            place.ant = place.ant.ant_contained
            Insect.remove_from(self, place)
        else:
            # default to normal behavior
            Ant.remove_from(self, place)

    @override
    def action(self, gamestate: 'GameState') -> None:
        # BEGIN Problem 8a
        if self.ant_contained is not None:
            self.ant_contained.action(gamestate)
        # END Problem 8a


class BodyguardAnt(ContainerAnt):
    """BodyguardAnt provides protection to other Ants."""

    name: ClassVar[str] = 'Bodyguard'
    food_cost: ClassVar[int] = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 8c
    implemented: ClassVar[bool] = True   # Change to True to view in the GUI
    # END Problem 8c

    def __init__(self, health: float=2):
        super().__init__(health)


# BEGIN Problem 9
# The TankAnt class
class TankAnt(ContainerAnt):
    name: ClassVar[str] = 'Tank'
    damage: float = 1
    food_cost: ClassVar[int] = 6
    implemented: ClassVar[bool] = True

    def __init__(self, health: float=2):
        super().__init__(health)

    @override
    def action(self, gamestate: 'GameState') -> None:
        bees: list[Bee] = list(self.place.bees)
        for bee in bees:
            bee.reduce_health(self.damage)
        super().action(gamestate)
# END Problem 9


class Water(Place):
    """Water is a place that can only hold waterproof insects."""

    @override
    def add_insect(self, insect: Insect) -> None:
        """Add an Insect to this place. If the insect is not waterproof, reduce
        its health to 0."""
        # BEGIN Problem 10
        super().add_insect(insect)
        if not insect.is_waterproof:
            insect.reduce_health(insect.health)
        # END Problem 10

# BEGIN Problem 11
# The ScubaThrower class
class ScubaThrower(ThrowerAnt):
    name: ClassVar[str] = 'Scuba'
    food_cost: ClassVar[int] = 6
    is_waterproof: ClassVar[bool] = True
    implemented: ClassVar[bool] = True
# END Problem 11


class QueenAnt(ThrowerAnt):
    """QueenAnt boosts the damage of all ants behind her."""

    name: ClassVar[str] = 'Queen'
    food_cost: ClassVar[int] = 7
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 12
    implemented: ClassVar[bool] = True   # Change to True to view in the GUI
    # END Problem 12

    @override
    def action(self, gamestate: 'GameState') -> None:
        """A queen ant throws a leaf, but also doubles the damage of ants
        in her tunnel.
        """
        # BEGIN Problem 12
        super().action(gamestate)
        place: Place | None = self.place.exit
        while place is not None:
            ant: Ant | None = place.ant
            if ant is not None:
                ant.double()
                if ant.is_container and ant.ant_contained is not None:
                    ant.ant_contained.double()
            place = place.exit
        # END Problem 12

    @override
    def zero_health_callback(self) -> Never:
        ants_lose()


################
# Extra Challenge #
################

class SlowThrower(ThrowerAnt):
    """ThrowerAnt that causes Slow on Bees."""

    name: ClassVar[str] = 'Slow'
    food_cost: ClassVar[int] = 6
    # BEGIN Problem EC 1
    implemented: ClassVar[bool] = True   # Change to True to view in the GUI
    # END Problem EC 1

    @override
    def throw_at(self, target: 'Bee | None') -> None:
        # BEGIN Problem EC 1
        # super().throw_at(target)
        if target is not None:
            target.slow_count = 5  # pyright: ignore[reportAttributeAccessIssue]
            def action(gamestate: 'GameState') -> None:
                if target.slow_count == 0 or gamestate.time % 2 == 0:  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                    Bee.action(target, gamestate)
                if target.slow_count > 0:  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                    target.slow_count -= 1  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            target.action = action
        # END Problem EC 1


class ScaryThrower(ThrowerAnt):
    """ThrowerAnt that intimidates Bees, making them back away instead of advancing."""

    name: ClassVar[str] = 'Scary'
    food_cost: ClassVar[int] = 6
    # BEGIN Problem EC 2
    implemented: ClassVar[bool] = True   # Change to True to view in the GUI
    # END Problem EC 2

    @override
    def throw_at(self, target: 'Bee | None') -> None:
        # BEGIN Problem EC 2
        super().throw_at(target)
        if target is not None:
            target.scare(2)
        # END Problem EC 2


class NinjaAnt(Ant):
    """NinjaAnt does not block the path and damages all bees in its place."""

    name: ClassVar[str] = 'Ninja'
    damage: float = 1
    food_cost: ClassVar[int] = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    blocks_path: ClassVar[bool] = False
    # BEGIN Problem EC 3
    implemented: ClassVar[bool] = True   # Change to True to view in the GUI
    # END Problem EC 3

    @override
    def action(self, gamestate: 'GameState') -> None:
        # BEGIN Problem EC 3
        bees: list[Bee] = list(self.place.bees)
        for bee in bees:
            bee.reduce_health(self.damage)
        # END Problem EC 3


class LaserAnt(ThrowerAnt):
    """ThrowerAnt that damages all Insects standing in its path."""

    name: ClassVar[str] = 'Laser'
    food_cost: ClassVar[int] = 10
    # OVERRIDE CLASS ATTRIBUTES HERE
    damage: float = 2
    # BEGIN Problem EC 4
    implemented: ClassVar[bool] = True   # Change to True to view in the GUI
    # END Problem EC 4

    def __init__(self, health: float=1):
        super().__init__(health)
        self.insects_shot: int = 0

    def insects_in_front(self) -> dict[Insect, int]:
        # BEGIN Problem EC 4
        d: dict[Insect, int] = {}
        place: Place | None = self.place
        i: int = 0
        while place is not None:
            if place.ant is not None and place.ant is not self:
                d[place.ant] = i
            for bee in place.bees:
                d[bee] = i
            place = place.entrance
            i += 1
        return d
        # END Problem EC 4

    def calculate_damage(self, distance: int) -> float:
        # BEGIN Problem EC 4
        return max(self.damage - 0.0625 * self.insects_shot - 0.25 * distance, 0)
        # END Problem EC 4

    @override
    def action(self, gamestate: 'GameState') -> None:
        insects_and_distances = self.insects_in_front()
        for insect, distance in insects_and_distances.items():
            damage = self.calculate_damage(distance)
            insect.reduce_health(damage)
            if damage:
                self.insects_shot += 1


########
# Bees #
########

class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name: ClassVar[str] = 'Bee'
    damage: float = 1
    is_waterproof: ClassVar[bool] = True


    def sting(self, ant: Ant) -> None:
        """Attack an ANT, reducing its health by 1."""
        ant.reduce_health(self.damage)

    def move_to(self, place: Place) -> None:
        """Move from the Bee's current Place to a new PLACE."""
        self.place.remove_insect(self)
        place.add_insect(self)

    def blocked(self) -> bool:
        """Return True if this Bee cannot advance to the next Place."""
        # Special handling for NinjaAnt
        # BEGIN Problem EC 3
        return self.place.ant is not None and self.place.ant.blocks_path
        # END Problem EC 3

    @override
    def action(self, gamestate: 'GameState') -> None:
        """A Bee's action stings the Ant that blocks its exit if it is blocked,
        or moves to the exit of its current place otherwise.

        gamestate -- The GameState, used to access game state information.
        """
        destination: Place | None = self.place.exit


        if hasattr(self, 'scared') and self.scared > 0:
            destination = self.place.entrance
            self.scared -= 1
        if self.blocked():
            self.sting(self.place.ant)
        elif self.health > 0 and destination is not None and not destination.is_hive:
            self.move_to(destination)

    @override
    def add_to(self, place: Place) -> None:
        place.bees.append(self)
        super().add_to(place)

    @override
    def remove_from(self, place: Place) -> None:
        place.bees.remove(self)
        super().remove_from(place)

    def scare(self, length: int) -> None:
        """
        If this Bee has not been scared before, cause it to attempt to
        go backwards LENGTH times.
        """
        # BEGIN Problem EC 2
        if hasattr(self, 'scared'):
            return
        self.scared: int = length
        # END Problem EC 2


class Wasp(Bee):
    """Class of Bee that has higher damage."""
    name: ClassVar[str] = 'Wasp'
    damage: float = 2


class Boss(Wasp):
    """The leader of the bees. Damage to the boss by any attack is capped.
    """
    name: ClassVar[str] = 'Boss'
    damage_cap: ClassVar[int] = 8

    @override
    def reduce_health(self, amount: float) -> None:
        super().reduce_health(min(amount, self.damage_cap))


class Hive(Place):
    """The Place from which the Bees launch their assault.

    assault_plan -- An AssaultPlan; when & where bees enter the colony.
    """
    is_hive: ClassVar[bool] = True

    def __init__(self, assault_plan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees = []
        for bee in assault_plan.all_bees():
            self.add_insect(bee)
        # The following attributes are always None for a Hive
        self.entrance = None
        self.ant = None
        self.exit = None

    def strategy(self, gamestate: 'GameState'):
        exits = [p for p in gamestate.places.values() if p.entrance is self]
        for bee in self.assault_plan.get(gamestate.time, []):
            bee.move_to(random.choice(exits))
            gamestate.active_bees.append(bee)

###################
# Game Components #
###################

class GameState:
    """An ant collective that manages global game state and simulates time.

    Attributes:
    time -- elapsed time
    food -- the colony's available food total
    places -- A list of all places in the colony (including a Hive)
    bee_entrances -- A list of places that bees can enter
    """

    def __init__(self, beehive: Hive, ant_types, create_places, dimensions, food: int=2):
        """Create an GameState for simulating a game.

        Arguments:
        beehive -- a Hive full of bees
        ant_types -- a list of ant classes
        create_places -- a function that creates the set of places
        dimensions -- a pair containing the dimensions of the game layout
        """
        self.time: int = 0
        self.food: int = food
        self.beehive: Hive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees = []
        self.configure(beehive, create_places)

    def configure(self, beehive, create_places):
        """Configure the places in the colony."""
        self.base = AntHomeBase('Ant Home Base')
        self.places = OrderedDict()
        self.bee_entrances = []

        def register_place(place, is_bee_entrance):
            self.places[place.name] = place
            if is_bee_entrance:
                place.entrance = beehive
                self.bee_entrances.append(place)
        register_place(self.beehive, False)
        create_places(self.base, register_place,
                      self.dimensions[0], self.dimensions[1])

    def ants_take_actions(self): # Ask ants to take actions
        for ant in self.ants:
            if ant.health > 0:
                ant.action(self)

    def bees_take_actions(self, num_bees): # Ask bees to take actions
        for bee in self.active_bees[:]:
            if bee.health > 0:
                bee.action(self)
            if bee.health <= 0:
                num_bees -= 1
                self.active_bees.remove(bee)
        if num_bees == 0: # Check if player won
            raise AntsWinException()
        return num_bees

    def simulate(self):
        """Simulate an attack on the ant colony. This is called by the GUI to play the game."""
        num_bees = len(self.bees)
        try:
            while True:
                self.beehive.strategy(self) # Bees invade from hive
                yield None # After yielding, players have time to place ants
                self.ants_take_actions()
                self.time += 1
                yield None # After yielding, wait for throw leaf animation to play, then ask bees to take action
                num_bees = self.bees_take_actions(num_bees)
        except AntsWinException:
            print('All bees are vanquished. You win!')
            yield True
        except AntsLoseException:
            print('The bees reached homebase or the queen ant queen has perished. Please try again :(')
            yield False

    def deploy_ant(self, place_name, ant_type_name):
        """Place an ant if enough food is available.

        This method is called by the current strategy to deploy ants.
        """
        ant_type = self.ant_types[ant_type_name]
        if ant_type.food_cost > self.food:
            print('Not enough food remains to place ' + ant_type.__name__)
        else:
            ant = ant_type()
            self.places[place_name].add_insect(ant)
            self.food -= ant.food_cost
            return ant

    def remove_ant(self, place_name):
        """Remove an Ant from the game."""
        place = self.places[place_name]
        if place.ant is not None:
            place.remove_insect(place.ant)

    @property
    def ants(self):
        return [p.ant for p in self.places.values() if p.ant is not None]

    @property
    def bees(self):
        return [b for p in self.places.values() for b in p.bees]

    @property
    def insects(self):
        return self.ants + self.bees

    def __str__(self):
        status = ' (Food: {0}, Time: {1})'.format(self.food, self.time)
        return str([str(i) for i in self.ants + self.bees]) + status


class AntHomeBase(Place):
    """AntHomeBase at the end of the tunnel, where the queen normally resides."""

    def add_insect(self, insect):
        """Add an Insect to this Place.

        Can't actually add Ants to a AntHomeBase. However, if a Bee attempts to
        enter the AntHomeBase, a AntsLoseException is raised, signaling the end
        of a game.
        """
        assert isinstance(insect, Bee), 'Cannot add {0} to AntHomeBase'
        raise AntsLoseException()


def ants_win() -> Never:
    """Signal that Ants win."""
    raise AntsWinException()


def ants_lose() -> Never:
    """Signal that Ants lose."""
    raise AntsLoseException()


def ant_types():
    """Return a list of all implemented Ant classes."""
    all_ant_types = []
    new_types = [Ant]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_ant_types.extend(new_types)
    return [t for t in all_ant_types if t.implemented]


def bee_types():
    """Return a list of all implemented Bee classes."""
    all_bee_types = []
    new_types = [Bee]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_bee_types.extend(new_types)
    return all_bee_types


class GameOverException(Exception):
    """Base game over Exception."""
    pass


class AntsWinException(GameOverException):
    """Exception to signal that the ants win."""
    pass


class AntsLoseException(GameOverException):
    """Exception to signal that the ants lose."""
    pass


###########
# Layouts #
###########


def wet_layout(queen, register_place, tunnels=3, length=9, moat_frequency=3):
    """Register a mix of wet and and dry places."""
    for tunnel in range(tunnels):
        exit = queen
        for step in range(length):
            if moat_frequency != 0 and (step + 1) % moat_frequency == 0:
                exit = Water('water_{0}_{1}'.format(tunnel, step), exit)
            else:
                exit = Place('tunnel_{0}_{1}'.format(tunnel, step), exit)
            register_place(exit, step == length - 1)


def dry_layout(queen, register_place, tunnels=3, length=9):
    """Register dry tunnels."""
    wet_layout(queen, register_place, tunnels, length, 0)


#################
# Assault Plans #
#################

class AssaultPlan(dict):
    """The Bees' plan of attack for the colony.  Attacks come in timed waves.

    An AssaultPlan is a dictionary from times (int) to waves (list of Bees).

    >>> AssaultPlan().add_wave(4, 2)
    {4: [Bee(3, None), Bee(3, None)]}
    """

    def add_wave(self, bee_type, bee_health, time, count):
        """Add a wave at time with count Bees that have the specified health."""
        bees = [bee_type(bee_health) for _ in range(count)]
        self.setdefault(time, []).extend(bees)
        return self

    def all_bees(self):
        """Place all Bees in the beehive and return the list of Bees."""
        return [bee for wave in self.values() for bee in wave]