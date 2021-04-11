#!/usr/bin/env python3

# Quake Game Log Parser Project ----------------------------------------------------------------------------------------
# CloudWalk Software Engineer test
# Coder: Daniel Sardo
# ----------------------------------------------------------------------------------------------------------------------
# Intended functionalities:
# - Read the log file
# - Group the game data of each match
# - Collect kill data
#
# Report: This script must print a report for each match as well as a player ranking.
#
# Notes:
# - When <world> kill a player, that player loses -1 kill score
# - Since <world> is not a player, it SHOULD NOT appear in the list of players or in the dictionary of kills
# - The counter "total_kills" MUST INCLUDE player and world deaths
#
# Proposed grouped information structure:
#
# "game_1": {
# "total_kills": 45,
# "players": ["Dono da bola", "Isgalamido", "Zeh"],
# "kills": {
#  "Dono da bola": 5,
#  "Isgalamido": 18,
#  "Zeh": 20
#  }
#}
# ======================================================================================================================

import sys
import json
from collections import Counter

# Opening the log file
try:
	quakelogfile = open("qgames.log", "r")

	# Read the log file into a list of lines
	full_log = quakelogfile.readlines()

	quakelogfile.close()
except IOError:
	sys.exit("File: qgames.log not found")


# Remove leading white spaces from each line and save them into a list
clean_lines_list = []
for raw_line in full_log:
	clean_lines_list.append(raw_line.strip())


# List of lines as lists of words
words_per_line_list = []
for line in clean_lines_list:
	line_aux = line.split(' ')

	if '------------------------------------------------------------' not in line_aux:
		words_per_line_list.append(line.split(' '))


# This for loop was used to simplify the next steps: converting an array of arrays into an array of strings
list_of_lines_as_strgs = []
for line in words_per_line_list:
	list_of_lines_as_strgs.append(' '.join(line))


# Creating a list of games
games_list = []
games_aux_list = []

for i in list_of_lines_as_strgs:
	games_aux_list.append(i)

	if 'ShutdownGame:' in i:
		games_list.append(games_aux_list)
		games_aux_list = []


# Counting the total of kills per game 
kill_counter = 0
kills_per_game_list = []
for game in games_list:
	for line_game in game:
		if 'Kill' in line_game:
			kill_counter += 1

	kills_per_game_list.append(kill_counter)


# Auxiliary variables for the treatment of the data of each game 
killer_list = []
killed_list = []
all_players = []
killed_by_world_dict = {}
ranking_data_dict = {}
death_cause_dict = {}

game_count = 0
total_kills = 0
killer_and_kills_dict = {}

# Loop for parsing the data of each game
for game in games_list:
	game_count += 1

	# Parsing kills, killer, killed and players data line by line
	for line in game:
		if "killed" in line:
			total_kills += 1

			line_header, game_ids, line_predicate = line.split(': ')

			# Collecting killer and killed into separate lists
			killer_name, killed_raw = line_predicate.split(' killed ')
			killed_name, death_cause = killed_raw.split(' by ')


			if killer_name == '<world>':
				killed_by_world_dict[killed_name] = -1

			killer_list.append(killer_name)
			killed_list.append(killed_name)

			# PLUS
			if death_cause in death_cause_dict:
				death_cause_dict[death_cause] += 1
			else:
				death_cause_dict[death_cause] = 1

		if 'ClientUserinfoChanged' in line:
			player = line.split('n\\')[1].split('\\t')
			all_players.append(player[0])

	# list of all players without repetition
	all_players = list(dict.fromkeys(all_players))

	# Remove <world> from the players list
	if '<world>' in all_players:
		all_players.remove('<world>')

	# List of killers without repetition
	single_killers = list(dict.fromkeys(killer_list))
	if '<world>' in single_killers:
		single_killers.remove('<world>')

	# Creating game ID
	game_id = 'game_' + str(game_count)

	# For each killer, the number of kills
	for single_killer in single_killers:
		kills = killer_list.count(single_killer)

		# Key and value of each killer in the game
		killer_and_kills_dict[single_killer] = kills

		
	# Sorting killers by number of kills
	killer_and_kills_dict = dict(sorted(killer_and_kills_dict.items(), key=lambda item: item[1], reverse=True))

	# Ranking data
	killed_by_world_dict_aux = Counter(killed_by_world_dict)
	killer_and_kills_dict_aux = Counter(killer_and_kills_dict)

	killed_by_world_dict_aux.update(killer_and_kills_dict_aux)
	ranking_data_dict = dict(killed_by_world_dict_aux)


	# Final dict for printing on the screen

	game_round = {game_id: {"total_kills": total_kills, "players": all_players, "kills": killer_and_kills_dict}}

	game_json = json.dumps(game_round, sort_keys=True, indent=4)

	ranking_data_dict = {game_id: {"Ranking": dict(sorted(ranking_data_dict.items(), key=lambda item: item[1], reverse=True))}}
	ranking_data_json = json.dumps(ranking_data_dict, indent=4)

	death_cause_dict = {game_id: {"Plus - kills_by_means": death_cause_dict}}
	death_cause_json = json.dumps(death_cause_dict, indent=4)

	# Printing parsed game information to the screen
	print(game_json)
	print(ranking_data_json)
	print(death_cause_json)



	# Cleaning variables for the next iteration
	total_kills = 0
	killer_list = []
	killed_list = []
	all_players = []
	killed_by_world_dict.clear()
	killer_and_kills_dict.clear()
	ranking_data_dict.clear()
	death_cause_dict.clear()





