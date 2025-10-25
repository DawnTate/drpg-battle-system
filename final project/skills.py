
class Skill:
    def __init__(self, name: str, cost: int, multiplier: float, desc: str = "", stun: bool = False):
        """
        Represents a combat skill that the player can use in battle.

        Parameters
        ----------
        name : str
            The display name of the skill (e.g., "Power Strike").
        cost : int
            The SP (Skill Points) cost required to use the skill.
        multiplier : float
            Damage multiplier relative to the player's normal attack.
            For example, 1.5 means 150% of normal damage.
        desc : str, optional
            A short description of the skill shown in the skill menu.
            Defaults to an empty string.
        stun : bool, optional
            Whether this skill stuns the enemy for 1 turn.
            Defaults to False.
        """

        self.name = name
        self.cost = cost
        self.multiplier = multiplier
        self.desc = desc
        self.stun = stun

# skills pool
ALL_SKILLS = [
    Skill("Power Strike", 3, 2.0, "A strong blow (x2 damage)."),
    Skill("Double Slash", 5, 4, "Two quick slashes (x4 damage)."),
    Skill("Guard Break", 4, 0.6, "less damage(x0.6) but stuns the enemy.", stun=True),
]
