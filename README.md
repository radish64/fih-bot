# Fih Bot
Fishing minigame bot for Discord

## Usage:
- Install python3 and postgresql
- install requirements.txt with pip
- Add your discord bot key to bot.py
- Add your postgres information to fishy.py
- Run bot.py

## How To Play:
- type `/fish` in a Discord channel to fish
    - you can fish once an hour, if you fish too early the bot will insult you!
    - various categories of fish can be caught, as seen in fishies.fih
- type `/leaderboard` to see the standings!
- type `/shop` to see items available in the shop!
- type `/items` to see items in your inventory!
- type `/buy <item name>` to buy an item!
- type `/use <item name> <@target>` to use an item!

## Adding New Content:
- the `.fih` file format is what is used for storing new types of fih!
	- to add a category, add a new line to fishies.fih as follows:
		- `Category:fish 1,fish 2,...,fish n`
	- then, add a the category alongside the others in fishy.py
	- you can add new fish to existing categories by adding them at the end of the lines, comma separated like above
	- you can similarly add new insults to `errors.fih`
- items are defined in `shop.csv`, and their behaviors in `bot.py`
	- new items will automatically be added to the database when you start the bot