Game Overview
This title is a Dungeon Role-Playing Game (DRPG) featuring a total of five dungeon floors. 
Once you conquer the fifth floor, the adventure comes to an end. Each dungeon layout is randomly generated at the start of play (note: saving and loading will not regenerate the dungeon map). 
With every step you take, there is a chance of encountering monsters（and some elite monsters）. Reaching the Exit (E) will allow you to descend to the next floor. Along the way, you may also discover Treasure Chests (C)—stepping onto one will trigger a unique Treasure Event.


Combat System
Battles follow a turn-based format: the player always acts first, followed by the enemy. 

During your turn, you may choose from the following actions:

Run Away – Attempt to escape the battle.（not 100% successful）

Attack – Deliver a standard strike against the foe.

Skill – Unleash one of your learned abilities.

Information – View your current condition and stats.

Potions(sp) - restore your SP using Potions (SP: everytime you use Skill, it will consume the sp. Different skills cost different sp)

Heal - restore your HP using Potions (HP: your life point, if you life point equals with 0, game over!)

Enemy Phase
Monsters take their turn after you act and will relentlessly attack each round.



Treasure Chest Events

Possible Mimic Encounter
There is a chance the chest is a Mimic—an elite foe whose type is randomly chosen and whose stats scale with the current floor. Approach with caution.

Reward: Defeat the Mimic to earn generous loot.

Fleeing: If you choose Run Away, you will step back to the tile before the event. The chest remains on the map (it does not disappear).

If it’s a real chest
The chest presents two choices:

Safe Option: Restore HP and SP.

Gamble Option: Leave it to fate. Your attributes change at random—they may increase or decrease.


If you want to pass this game quickly:
You can modify the possibility of encountering monsters in main.py(random.random())
You can modify the attributes of player in models.py

So that you can quickly pass through this game.





About config.json:

{
  "treasure": {
    "chest_per_floor": 1,       
    "mimic_chance": 0.30,       // 30% chance the chest is a Mimic
    "heal_rate": 0.30,          // heal 30% HP & SP
    "gamble_attr_count_min": 1, // gamble: min number of affected attributes
    "gamble_attr_count_max": 3, // gamble: max number of affected attributes
    "backfire_prob": 0.20,      // per-attribute chance to flip to negative
    "mimic_boost_bias": 0.20    // extra positive bias when reward is from Mimic
  }
}