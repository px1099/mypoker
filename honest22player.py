from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
import random as rand
import pprint

class Honest22Player(BasePokerPlayer):

	# Number of simulation
	NB_SIMULATION = 250

	# Minumum rounds needed to collect base data for 2nd heuristic
	MIN_NUM_DATA_COLLECTED = 100

	# Psuedo infinite
	POS_INF = 10000.0

	# Street name constant
	STREET_ZERO_CARD = "preflop"
	STREET_THREE_CARD = "flop"
	STREET_FOUR_CARD = "turn"
	STREET_FIVE_CARD = "river"

	# List of streets
	LIST_OF_STREET = [STREET_ZERO_CARD, STREET_THREE_CARD, STREET_FOUR_CARD, STREET_FIVE_CARD]

	# Action name constant
	FOLD = "fold"
	CALL = "call"
	RAISE = "raise"

	# Action index constant
	FOLD_INDEX = 0
	CALL_INDEX = 1
	RAISE_INDEX = 2

	# Game constant (declared here as it is difficult to check during game)
	# ENGINE BUG: The engine uses 20 for preflop, flop and 40 for turn, river 
	# instead of 10 like the project specification stated
	RAISE_AMOUNT_PREFLOP = 20
	RAISE_AMOUNT_FLOP = 20
	RAISE_AMOUNT_TURN = 40
	RAISE_AMOUNT_RIVER = 40

	# Limited poker constant
	NUM_STREET_PER_ROUND = 4
	NUM_RAISE_PER_STREET = 4
	NUM_RAISE_PER_ROUND_PER_PLAYER = 4

	# Player turn constant
	PLAYER_TURN = True
	OPPONENT_TURN = False

	# Street index
	STREET_INDEX_DICT = {
		STREET_ZERO_CARD: 0,
		STREET_THREE_CARD: 1,
		STREET_FOUR_CARD: 2,
		STREET_FIVE_CARD: 3
	}

	# Raise amount dictionary
	RAISE_AMOUNT_DICT = {
		STREET_ZERO_CARD: RAISE_AMOUNT_PREFLOP,
		STREET_THREE_CARD: RAISE_AMOUNT_FLOP,
		STREET_FOUR_CARD: RAISE_AMOUNT_TURN,
		STREET_FIVE_CARD: RAISE_AMOUNT_RIVER,
		0: RAISE_AMOUNT_PREFLOP,
		1: RAISE_AMOUNT_FLOP,
		2: RAISE_AMOUNT_TURN,
		3: RAISE_AMOUNT_RIVER
	}

	# Convert card letter to number
	CARD_NUM_DICT = {
		"2": 2,
		"3": 3,
		"4": 4,
		"5": 5,
		"6": 6,
		"7": 7,
		"8": 8,
		"9": 9,
		"T": 10,
		"J": 11,
		"Q": 12,
		"K": 13,
		"A": 14
	}


	# Hold history of Opponent's action and outcome
	# To search: self.RAISE_HISTORY[did_player_win][is_player_big_blind][street][num_raises]
	RAISE_HISTORY = {
		# Roundts won
		True: {
			# Player is big blind
			True: {
				#Streets history (index: number_of_raises, value: number_of_rounds)
				STREET_ZERO_CARD: [0, 0, 0, 0, 0],
				STREET_THREE_CARD: [0, 0, 0, 0, 0],
				STREET_FOUR_CARD: [0, 0, 0, 0, 0],
				STREET_FIVE_CARD: [0, 0, 0, 0, 0]
			},
			# Opponent is big blind
			False: {
				#Streets history (index: number_of_raises, value: number_of_rounds)
				STREET_ZERO_CARD: [0, 0, 0, 0, 0],
				STREET_THREE_CARD: [0, 0, 0, 0, 0],
				STREET_FOUR_CARD: [0, 0, 0, 0, 0],
				STREET_FIVE_CARD: [0, 0, 0, 0, 0]
			}
		},
		# Rounds lost
		False: {
			# Player is big blind
			True: {
				# Streets history (index: number_of_raises, value: number_of_rounds)
				STREET_ZERO_CARD: [0, 0, 0, 0, 0],
				STREET_THREE_CARD: [0, 0, 0, 0, 0],
				STREET_FOUR_CARD: [0, 0, 0, 0, 0],
				STREET_FIVE_CARD: [0, 0, 0, 0, 0]
			},
			# Opponent is big blind
			False: {
				# Streets history (index: number_of_raises, value: number_of_rounds)
				STREET_ZERO_CARD: [0, 0, 0, 0, 0],
				STREET_THREE_CARD: [0, 0, 0, 0, 0],
				STREET_FOUR_CARD: [0, 0, 0, 0, 0],
				STREET_FIVE_CARD: [0, 0, 0, 0, 0]
			}
		}
	}

	# Hold win rates history given the player who is big blind this round
	# To search: self.WIN_RATES_FROM_RAISE_HISTORY[street][num_raises]
	WIN_RATES_FROM_RAISE_HISTORY = {
		# Streets history (index: number_of_raises, value: win_rates)
		STREET_ZERO_CARD: [0.0, 0.0, 0.0, 0.0, 0.0],
		STREET_THREE_CARD: [0.0, 0.0, 0.0, 0.0, 0.0],
		STREET_FOUR_CARD: [0.0, 0.0, 0.0, 0.0, 0.0],
		STREET_FIVE_CARD: [0.0, 0.0, 0.0, 0.0, 0.0]
	}

	BET_AVG_KEY = "avg"
	BET_NUM_KEY = "num"
	BET_TOT_KEY = "total"

	BET_AMOUNT_HISTORY = {
		# Streets history (current_amount: {BET_AVG_KEY: avg, BET_NUM_KEY: num, BET_TOT_KEY: total})
		STREET_ZERO_CARD: {},
		STREET_THREE_CARD: {},
		STREET_FOUR_CARD: {}
	}

	# Hold card probability look up table
	# To search: self.PREFLOP_EXPECTED_VALUE[is_same_shape][lower_card_number][higher_card_number]
	""" TO BE FILLED HERE """
	PREFLOP_EXPECTED_VALUE = {
		# Same shape (suited)
		True: {
			# Lower card number
			"2": {
				# Higher card number
				"3": -0.2803, "4": -0.2634  , "5": -0.2430  , "6": -0.2466  , "7": -0.2369  ,
				"8": -0.1946, "9": -0.1517  , "T": -0.1032  , "J": -0.0524  , "Q": 0.0034   ,
				"K": 0.0642 , "A": 0.1476
			},
			"3": {
				"4": -0.2272, "5": -0.2061, "6": -0.2093, "7": -0.1993, "8": -0.1825,
				"9": -0.1347, "T": -0.0861, "J": -0.0354, "Q": 0.0204, "K": 0.0811,
				"A": 0.1644
			},
			"4": {
				"5": -0.1709, "6": -0.1733, "7": -0.1630, "8": -0.1460, "9": -0.1228,
				"T": -0.0694, "J": -0.0186, "Q": 0.0371, "K": 0.0977, "A": 0.1807
			},
			"5": {
				"6": -0.1373, "7": -0.1265, "8": -0.1091, "9": -0.0856, "T": -0.0557,
				"J": -0.0003, "Q": 0.0554, "K": 0.1159, "A": 0.1985
			},
			"6": {
				"7": -0.0926, "8": -0.0751, "9": -0.0514, "T": -0.0212, "Q": 0.0723,
				"J": 0.0121, "K": 0.1328, "A": 0.1981
			},
			"7": {
				"8": -0.0413, "9": -0.0174, "T": 0.0128, "J": 0.0465, "Q": 0.0860,
				"K": 0.1580, "A": 0.2197
			},
			"8": {
				"9": 0.0016, "T": 0.0467, "J": 0.0803, "Q": 0.1204, "K": 0.1662,
				"A": 0.2389
			},
			"9": {
				"T": 0.0806, "J": 0.1132, "Q": 0.1533, "K": 0.1998, "A": 0.2556
			},
			"T": {
				"J": 0.1506, "Q": 0.1894, "K": 0.2358, "A": 0.2920
			},
			"J": { 
				"Q": 0.2052, "K": 0.2513, "A": 0.3079
			},
			"Q": {
				"K": 0.2680, "A": 0.3242
			},
			"K": {
				"A": 0.3409
			}
		},
		# Different shape (unsuited)
		False: {
			# Lower card number
			"2": {
				# Higher card number
				"2": 0.0067 , "3": -0.3539  , "4": -0.3360  , "5": -0.3143  , "6": -0.3185  ,
				"7": -0.3083, "8": -0.2634  , "9": -0.2180  , "T": -0.1666  , "J": -0.1130  ,
				"Q": -0.0541, "K": 0.0102   , "A": 0.0986
			},
			"3": {
				"3": 0.0739, "4": -0.2971, "5": -0.2747, "6": -0.2784, "7": -0.2680,
				"8": -0.2503, "9": -0.1996, "T": -0.1481, "J": -0.0945, "Q": -0.0356,
				"K": -0.0285, "A": 0.1169
			},
			"4": {
				"4": 0.1405, "5": -0.2369, "6": -0.2398, "7": -0.2290, "8": -0.2111, 
				"9": -0.1866, "T": -0.1299, "J": -0.0763, "Q": -0.0174, "K": 0.0465, 
				"A": 0.1346
			},
			"5": {
				"5": 0.2065, "6": -0.2011, "7": -0.1898, "8": -0.1714, "9": -0.1466, 
				"T": -0.1150, "J": -0.0564, "Q": 0.0024, "K": 0.0663, "A": 0.1539
			},
			"6": {
				"6": 0.2657, "7": -0.1535, "8": -0.1353, "9": -0.1102, "T": -0.0782, 
				"J": -0.0431, "Q": 0.0205, "K": 0.0845, "A": 0.1536
			},
			"7": {
				"7": 0.3247, "8": -0.0990, "9": -0.0740, "T": -0.0418, "J": -0.0064, 
				"Q": 0.0353, "K": 0.1037, "A": 0.1768 
			},
			"8": {
				"8": 0.3833, "9": -0.0381, "T": -0.0056, "J": 0.0298, "Q": 0.0720, 
				"K": 0.1204, "A": 0.1975
			},
			"9": {
				"9": 0.4411, "T": 0.0306, "J": 0.0650, "Q": 0.1072, "K": 0.1562, 
				"A": 0.2155
			},
			"T": {
				"T":0.5002, "J": 0.1050, "Q": 0.1458, "K": 0.1948, "A": 0.2544
			},
			"J": { 
				"J": 0.5494, "Q": 0.1627, "K": 0.2114, "A": 0.2713
			},
			"Q": {
				"Q": 0.5985, "K": 0.2291, "A": 0.2886
			},
			"K": {
				"K": 0.6479, "A": 0.3064
			},
			"A": {
				"A": 0.7041
			}
		}
	}


	def __init__(self):
		BasePokerPlayer.__init__(self)
		# To be re-initialized at the start of each game
		# Agent info
		# self.uuid is already initialized by the engine
		self.name = "agent22"
		self.seat_pos = 0
		# Rule info
		self.small_blind_amount = 0
		self.big_blind_amount = 0
		self.max_round = 1000
		# To be re-initialized at the start of each round
		# Round info
		self.round_count = 0
		self.big_blind_seat_pos = 0
		self.is_player_big_blind = True
		self.hole_card = []
		self.player_stack_at_start_of_round = 10000
		self.opponent_stack_at_start_of_round = 10000
		self.prev_outcome = 0
		# To be re-initialized at the start of each street
		# Street info
		self.street = self.STREET_ZERO_CARD
		self.is_start_of_street = True
		self.community_card = []
		self.player_bet_at_start_of_street = 0
		self.opponent_bet_at_start_of_street = 0
		self.bet_at_end_of_street = []
		self.remaining_raise_this_street = self.NUM_RAISE_PER_STREET	#set to 4
		self.remaining_player_raise_this_round = self.NUM_RAISE_PER_ROUND_PER_PLAYER	#set to 4
		self.remaining_opponent_raise_this_round = self.NUM_RAISE_PER_ROUND_PER_PLAYER	#set to 4
		self.preflop_expected_value = 0.0
		self.winning_probability = 0.5
		self.opp_heuristic_weight = 0.0
		# To be re-initialized at the start of each update
		# Current info (will be reinitialize from game info)
		self.player_stack = 1000
		self.opponent_stack = 1000
		self.player_bet = 0 
		self.opponent_bet = 0
		self.last_action = {}
		# Pre-calculating and populating data for estimating the future raising amount
		self.avg_raise_amount_remaining_street = []
		self.pre_calculate_avg_raise_amount_remaining_street()

	def declare_action(self, valid_actions, hole_card, round_state):
		call_action_info = valid_actions[self.best_action(valid_actions)]
		action = call_action_info["action"]
		return action	# action returned here is sent to the poker engine

	def receive_game_start_message(self, game_info):
		# initialize game infomation
		self.small_blind_amount = game_info["rule"]["small_blind_amount"]
		self.big_blind_amount = 2 * self.small_blind_amount
		self.max_round = game_info["rule"]["max_round"]
		# initialize personal data
		for i in range(0, len(game_info["seats"])):
			if game_info["seats"][i]["uuid"] == self.uuid:
				self.seat_pos = i
				self.name = game_info["seats"][i]["name"]
		# initialize money stack
		self.player_stack_at_start_of_round = game_info["rule"]["initial_stack"]
		self.opponent_stack_at_start_of_round = game_info["rule"]["initial_stack"]
		self.player_stack = self.player_stack_at_start_of_round
		self.opponent_stack = self.opponent_stack_at_start_of_round
		# DEBUG
		# pprint.pprint(game_info)
		# print("-----GAME START-----")
		# print("name: " + str(self.name))
		# print("uuid: " + str(self.uuid))
		# print("small_blind_amount: " + str(self.small_blind_amount))
		# print("big_blind_amount: " + str(self.big_blind_amount))
		# print("max_round: " + str(self.max_round))
		# print("seat_pos: " + str(self.seat_pos))
		# print("--------------------")
		# pass

	def receive_round_start_message(self, round_count, hole_card, seats):
		# Initialize round info
		self.round_count = round_count
		self.hole_card = list(hole_card)
		self.remaining_player_raise_this_round = self.NUM_RAISE_PER_ROUND_PER_PLAYER
		self.remaining_opponent_raise_this_round = self.NUM_RAISE_PER_ROUND_PER_PLAYER
		# Initialize last action
		self.last_action = {}
		# Initialize bet amount at end of street
		self.bet_at_end_of_street = []
		# Initialize for preflop street
		self.player_bet_at_start_of_street = 0
		self.opponent_bet_at_start_of_street = 0
		self.remaining_raise_this_street = self.NUM_RAISE_PER_STREET
		# Update stack and initialize small/big blind bet
		for i in range(0, len(seats)):
			if seats[i]["uuid"] == self.uuid:
				self.player_stack = seats[i]["stack"]
				self.player_bet = self.player_stack_at_start_of_round - self.player_stack
				# big blind/all in is considered as a raise
				if self.player_bet > self.small_blind_amount:
					self.remaining_raise_this_street -= 1
					self.big_blind_seat_pos = i
			else:
				self.opponent_stack = seats[i]["stack"]
				self.opponent_bet = self.opponent_stack_at_start_of_round - self.opponent_stack
				# big blind/all in is considered as a raise
				if self.opponent_bet > self.small_blind_amount:
					self.remaining_raise_this_street -= 1
					self.big_blind_seat_pos = i
		self.is_player_big_blind = (self.seat_pos == self.big_blind_seat_pos)
		# DEBUG
		# pprint.pprint(hole_card)
		# pprint.pprint(seats)
		# print("-----ROUND START-----")
		# print("round_count: " + str(self.round_count))
		# print("big_blind_seat_pos: " + str(self.big_blind_seat_pos))
		# print("hole_card: ")
		# pprint.pprint(self.hole_card)
		# print("player_stack_at_start_of_round: " + str(self.player_stack_at_start_of_round))
		# print("opponent_stack_at_start_of_round: " + str(self.opponent_stack_at_start_of_round))
		# print("---------------------")
		# pass

	def receive_street_start_message(self, street, round_state):
		# Initialize street info
		self.street = street
		self.is_start_of_street = True
		self.community_card = list(round_state["community_card"])
		# Initialize for non-preflop street
		if self.street != self.STREET_ZERO_CARD:
			self.remaining_raise_this_street = self.NUM_RAISE_PER_STREET
			self.player_bet_at_start_of_street = self.player_bet
			self.opponent_bet_at_start_of_street = self.opponent_bet
			self.bet_at_end_of_street.append(self.player_bet_at_start_of_street)
		# Update stacks
		for i in range(0, len(round_state["seats"])):
			if round_state["seats"][i]["uuid"] == self.uuid:
				self.player_stack = round_state["seats"][i]["stack"]
			else:
				self.opponent_stack = round_state["seats"][i]["stack"]
		# Recalculate winning probability
		self.re_calculate_probability()
		# DEBUG
		# pprint.pprint(round_state)
		# print("-----STREET START-----")
		# print("street: " + str(self.street))
		# print("raise_amount: " + str(self.raise_amount(self.street)))
		# print("avg_raise_amount_remaining_street: " 
		#		+ str(self.avg_raise_amount_remaining_street[self.STREET_INDEX_DICT[self.street]]))
		# pprint.pprint(self.community_card)
		# print("player_bet_at_start_of_street: " + str(self.player_bet_at_start_of_street))
		# print("opponent_bet_at_start_of_street: " + str(self.opponent_bet_at_start_of_street))
		# print("player_bet: " + str(self.player_bet))
		# print("opponent_bet: " + str(self.opponent_bet))
		# print("----------------------")
		# pass

	# ENGINE BUG (RARE): Poker game might send update message 2 times
	# In order to update number of remaining raise while dealing with this bug,
	# we make use of the fact that a player cannot preform 2 identical raise action 
	# subsequently withour letting the opponent do anything
	def receive_game_update_message(self, action, round_state):
		# Check for repeating bug
		if ((action != self.last_action) or (self.is_start_of_street == True)):
			# Update bet amount
			if action["player_uuid"] == self.uuid:
				if action["action"] != self.FOLD:
					self.player_bet = self.player_bet_at_start_of_street + action["amount"]
				if action["action"] == self.RAISE:
					self.remaining_raise_this_street -= 1
					self.remaining_player_raise_this_round -= 1
			else:
				if action["action"] != self.FOLD:
					self.opponent_bet = self.opponent_bet_at_start_of_street + action["amount"]
				if action["action"] == self.RAISE:
					self.remaining_raise_this_street -= 1
					self.remaining_opponent_raise_this_round -= 1
			# Update stacks
			for i in range(0, len(round_state["seats"])):
				if round_state["seats"][i]["uuid"] == self.uuid:
					self.player_stack = round_state["seats"][i]["stack"]
				else:
					self.opponent_stack = round_state["seats"][i]["stack"]
			# An action has been preformed since the start of the street
			self.is_start_of_street = False
		# Update last action
		self.last_action = dict(action)
		# DEBUG
		# pprint.pprint(action)
		# pprint.pprint(round_state)
		# print("-----GAME UPDATE-----")
		# print("player_bet: " + str(self.player_bet))
		# print("opponent_bet: " + str(self.opponent_bet))
		# print("player_stack: " + str(self.player_stack))
		# print("opponent_stack: " + str(self.opponent_stack))
		# print("remaining_raise_this_street: " + str(self.remaining_raise_this_street))
		# print("remaining_player_raise_this_round: " + str(self.remaining_player_raise_this_round))
		# print("remaining_opponent_raise_this_round: " + str(self.remaining_opponent_raise_this_round))
		# print("---------------------")
		# pass

	def receive_round_result_message(self, winners, hand_info, round_state):
		# Update bet amount history
		if (self.last_action["action"] != self.FOLD):
			final_bet = self.player_bet
			if (len(self.bet_at_end_of_street) == (self.NUM_STREET_PER_ROUND - 1)):
				for i in range(0, self.NUM_STREET_PER_ROUND - 1):
					street = self.LIST_OF_STREET[i]
					bet = self.bet_at_end_of_street[i]
					if bet in self.BET_AMOUNT_HISTORY[street].keys():
						self.BET_AMOUNT_HISTORY[street][bet][self.BET_TOT_KEY] += final_bet
						self.BET_AMOUNT_HISTORY[street][bet][self.BET_NUM_KEY] += 1
						self.BET_AMOUNT_HISTORY[street][bet][self.BET_AVG_KEY] = (
							self.BET_AMOUNT_HISTORY[street][bet][self.BET_TOT_KEY]
							/ float(self.BET_AMOUNT_HISTORY[street][bet][self.BET_NUM_KEY]))
					else:
						self.BET_AMOUNT_HISTORY[street][bet] = {
							self.BET_AVG_KEY: final_bet,
							self.BET_NUM_KEY: 1,
							self.BET_TOT_KEY: final_bet
						}

		# Update stacks
		for i in range(0, len(round_state["seats"])):
			if round_state["seats"][i]["uuid"] == self.uuid:
				self.player_stack = round_state["seats"][i]["stack"]
			else:
				self.opponent_stack = round_state["seats"][i]["stack"]

		self.prev_outcome = self.player_stack - self.player_stack_at_start_of_round
		self.player_stack_at_start_of_round = self.player_stack
		self.opponent_stack_at_start_of_round = self.opponent_stack

		has_won = (winners[0]["name"] == self.name)
		
		# We can only evaluate how powerful the opponent is given their action if we do not fold
		if not ((has_won == False) and (self.last_action["action"] == self.FOLD)):
			num_raises = [0, 0, 0, 0]
			for street in round_state["action_histories"].keys():
				# Calculate number of raise per street
				for turn in round_state["action_histories"][street]:
					if turn["action"] == "RAISE" and turn["uuid"] != self.uuid:
						num_raises[self.STREET_INDEX_DICT[street]] += 1

			# Calculate number of raise by the end of certain street
			for i in range(self.NUM_STREET_PER_ROUND - 1, 0, -1):
				for j in range(0, i):
					num_raises[i] += num_raises[j]

			for street in self.LIST_OF_STREET:
				num_opp_raises = num_raises[self.STREET_INDEX_DICT[street]]
				self.RAISE_HISTORY[has_won][self.is_player_big_blind][street][num_opp_raises] += 1

			# Note: it can be mathematically proven that we only need to update 
			# entries with number of raises by the end of each street of this round
			for street in self.WIN_RATES_FROM_RAISE_HISTORY.keys():
				if street in round_state["action_histories"].keys():
					raises = num_raises[self.STREET_INDEX_DICT[street]]
					self.WIN_RATES_FROM_RAISE_HISTORY[street][raises] = (
						self.win_chance_from_raise_history(street, raises))

		# DEBUG
		# print(self.RAISE_HISTORY)
		# pprint.pprint(winners)
		# pprint.pprint(hand_info)
		# pprint.pprint(round_state)
		# print("-----ROUND RESULT-----")
		# print("player_stack: " + str(self.player_stack))
		# print("opponent_stack: " + str(self.opponent_stack))
		# print("----------------------")
		# pass

	def raise_amount(self, street):
		# Default result: RAISE_AMOUNT_PREFLOP
		result = self.RAISE_AMOUNT_DICT.get(street, self.RAISE_AMOUNT_PREFLOP)
		return result

	# First call of the heuristic minimax search, return best action index
	# Special case: call in the very first turn of the street will not end the street
	def best_action(self, valid_actions):
		bet_diff = self.opponent_bet - self.player_bet
		# Initialize with fold action
		best_outcome = (-1) * self.player_bet
		best_action_index = self.FOLD_INDEX
		# Check call action
		call_outcome = 0
		if self.is_start_of_street == True:
			call_outcome = self.heuristic_minimax(	#player calls, opponent turn
								self.OPPONENT_TURN,
								self.opponent_bet,
								self.opponent_bet,
								self.player_stack - bet_diff,
								self.opponent_stack,
								self.remaining_player_raise_this_round,
								self.remaining_opponent_raise_this_round,
								self.remaining_raise_this_street,
								best_outcome,
								self.POS_INF)
		else:
			call_outcome = self.expected_outcome(	#player calls, street ends
								self.opponent_bet,
								self.player_stack - bet_diff,
								self.opponent_stack,
								self.remaining_player_raise_this_round,
								self.remaining_opponent_raise_this_round)
		if call_outcome >= best_outcome:
			best_outcome = call_outcome
			best_action_index = self.CALL_INDEX
		# Check raise action
		if len(valid_actions) == 3:
			raise_outcome = 0
			raise_amount_this_street = self.raise_amount(self.street)
			player_has_enough_money = (self.player_stack >= (bet_diff + raise_amount_this_street))	#flag
			opponent_has_enough_money = (self.opponent_stack >= raise_amount_this_street)	#flag
			if (player_has_enough_money and opponent_has_enough_money):
				raise_outcome = self.heuristic_minimax(	#player raises
									self.OPPONENT_TURN,
									self.opponent_bet + raise_amount_this_street,
									self.opponent_bet,
									self.player_stack - bet_diff - raise_amount_this_street,
									self.opponent_stack,
									self.remaining_player_raise_this_round - 1,
									self.remaining_opponent_raise_this_round,
									self.remaining_raise_this_street - 1,
									best_outcome,
									self.POS_INF)
			else:
				last_raise_amount = min(self.player_stack - bet_diff, self.opponent_stack)
				raise_outcome = self.heuristic_minimax(	#player raises to the highest possible remaining amount
									self.OPPONENT_TURN,
									self.opponent_bet + last_raise_amount,
									self.opponent_bet,
									self.player_stack - bet_diff - last_raise_amount,
									self.opponent_stack,
									self.remaining_player_raise_this_round - 1,
									self.remaining_opponent_raise_this_round,
									self.remaining_raise_this_street - 1,
									best_outcome,
									self.POS_INF)
			if raise_outcome >= best_outcome:
				best_outcome = raise_outcome
				best_action_index = self.RAISE_INDEX
		return best_action_index

	# Alpha-beta prunning heuristic minimax algorithm
	# Special case in the first turn of the street is already checked in best_action
	def heuristic_minimax(self,
						player_turn,
						player_bet,
						opponent_bet,
						player_stack,
						opponent_stack,
						remaining_player_raise_this_round,
						remaining_opponent_raise_this_round,
						remaining_raise_this_street,
						alpha,
						beta
						):
		best_outcome = 0
		call_outcome = 0
		raise_outcome = 0
		raise_amount_this_street = self.raise_amount(self.street)
		# Max player
		if player_turn == self.PLAYER_TURN: 	# if it is player's turn
			best_outcome = (-1) * player_bet 	# initialize with folding
			if (best_outcome >= beta):
				return best_outcome				# prunning
			bet_diff = opponent_bet - player_bet
			# Check call outcome
			call_outcome = self.expected_outcome(
								opponent_bet,
								player_stack - bet_diff,
								opponent_stack,
								remaining_player_raise_this_round,
								remaining_opponent_raise_this_round)
			if call_outcome >= best_outcome:
				best_outcome = call_outcome
			if (best_outcome >= beta):
				return best_outcome				# prunning
			# Check raise outcome
			if remaining_raise_this_street > 0:	#make sure there is eligible number of raises left in street
				if remaining_player_raise_this_round > 0:	#check if player is still eligible to raise
					if ((player_stack > bet_diff) and (opponent_stack > 0)):
						player_has_enough_money = (player_stack >= (bet_diff + raise_amount_this_street))
						opponent_has_enough_money = (opponent_stack >= raise_amount_this_street)
						if (player_has_enough_money and opponent_has_enough_money):
							raise_outcome = self.heuristic_minimax(	#recursive miniMax
												self.OPPONENT_TURN,
												opponent_bet + raise_amount_this_street,
												opponent_bet,
												player_stack - bet_diff - raise_amount_this_street,
												opponent_stack,
												remaining_player_raise_this_round - 1,
												remaining_opponent_raise_this_round,
												remaining_raise_this_street - 1,
												max(alpha, best_outcome),
												beta)
						else:
							last_raise_amount = min(player_stack - bet_diff, opponent_stack)
							raise_outcome = self.heuristic_minimax(	#recursive miniMax
												self.OPPONENT_TURN,
												opponent_bet + last_raise_amount,
												opponent_bet,
												player_stack - bet_diff - last_raise_amount,
												opponent_stack,
												remaining_player_raise_this_round - 1,
												remaining_opponent_raise_this_round,
												remaining_raise_this_street - 1,
												max(alpha, best_outcome),
												beta)
						if raise_outcome >= best_outcome:
							best_outcome = raise_outcome
		# Min player
		else:
			best_outcome = opponent_bet
			if (best_outcome <= alpha):
				return best_outcome				# prunning
			bet_diff = player_bet - opponent_bet
			# Check call outcome
			call_outcome = self.expected_outcome(
								player_bet,
								player_stack,
								opponent_stack - bet_diff,
								remaining_player_raise_this_round,
								remaining_opponent_raise_this_round)
			if call_outcome <= best_outcome:
				best_outcome = call_outcome
			if (best_outcome <= alpha):
				return best_outcome				# prunning
			# Check raise outcome
			if remaining_raise_this_street > 0:
				if remaining_opponent_raise_this_round > 0:
					if ((opponent_stack > bet_diff) and (player_stack > 0)):
						opponent_has_enough_money = (opponent_stack >= (bet_diff + raise_amount_this_street))
						player_has_enough_money = (player_stack >= raise_amount_this_street)
						if (player_has_enough_money and opponent_has_enough_money):
							raise_outcome = self.heuristic_minimax(
												self.PLAYER_TURN,
												player_bet,
												player_bet + raise_amount_this_street,
												player_stack,
												opponent_stack - bet_diff - raise_amount_this_street,
												remaining_player_raise_this_round,
												remaining_opponent_raise_this_round - 1,
												remaining_raise_this_street - 1,
												alpha,
												min(beta, best_outcome))
						else:
							last_raise_amount = min(opponent_stack - bet_diff, player_stack)
							raise_outcome = self.heuristic_minimax(
												self.PLAYER_TURN,
												player_bet,
												player_bet + last_raise_amount,
												player_stack,
												opponent_stack - bet_diff - last_raise_amount,
												remaining_player_raise_this_round,
												remaining_opponent_raise_this_round - 1,
												remaining_raise_this_street - 1,
												alpha,
												min(beta, best_outcome))
						if raise_outcome <= best_outcome:
							best_outcome = raise_outcome
		return best_outcome

	def expected_outcome(self, 
						bet_amount,
						player_stack, 
						opponent_stack,
						remaining_player_raise_this_round, 
						remaining_opponent_raise_this_round):
		num_opponent_raise = self.NUM_RAISE_PER_ROUND_PER_PLAYER - remaining_opponent_raise_this_round
		if self.street == self.STREET_FIVE_CARD:
			expected_bet = bet_amount
		else:
			if ((self.round_count > self.MIN_NUM_DATA_COLLECTED)
				and (bet_amount in self.BET_AMOUNT_HISTORY[self.street].keys())):
				expected_bet = self.BET_AMOUNT_HISTORY[self.street][bet_amount][self.BET_AVG_KEY]
			else:
				expected_bet = self.naive_expected_bet_amount(
									bet_amount, 
									player_stack, 
									opponent_stack,
									remaining_player_raise_this_round,
									remaining_opponent_raise_this_round)
		expected_value = self.evaluate_value(expected_bet, num_opponent_raise)
		return expected_value

	def naive_expected_bet_amount(self, 
								bet_amount, 
								player_stack, 
								opponent_stack, 
								remaining_player_raise_this_round, 
								remaining_opponent_raise_this_round):
		num_player_raise = self.NUM_RAISE_PER_ROUND_PER_PLAYER - remaining_player_raise_this_round
		num_opponent_raise = self.NUM_RAISE_PER_ROUND_PER_PLAYER - remaining_opponent_raise_this_round
		street_index = self.STREET_INDEX_DICT[self.street]
		num_street = street_index + 1
		num_remaining_street = self.NUM_STREET_PER_ROUND - num_street
		avg_raise_amount_remaining_street = self.avg_raise_amount_remaining_street[street_index]
		expected_num_player_future_raise = min(remaining_player_raise_this_round, 
												float(num_player_raise) / num_street * num_remaining_street)
		expected_num_opponent_future_raise = min(remaining_opponent_raise_this_round, 
												float(num_opponent_raise) / num_street * num_remaining_street)
		remaining_possible_total_raise = num_remaining_street * self.NUM_RAISE_PER_STREET
		expected_increase_bet = min(player_stack, 
									opponent_stack,
									((expected_num_player_future_raise + expected_num_opponent_future_raise) 
										* avg_raise_amount_remaining_street),
									remaining_possible_total_raise * avg_raise_amount_remaining_street)
		expected_bet = bet_amount + expected_increase_bet
		return expected_bet

	def evaluate_value(self, bet_amount, num_opponent_raise):
		first_card = self.hole_card[0]
		second_card = self.hole_card[1]
		value = 0
		if self.street == self.STREET_ZERO_CARD:
			card_heuristic = bet_amount * self.preflop_expected_value
			# card_heuristic = bet_amount * (2 * self.winning_probability - 1)
		else:	#not in PREFLOP
			# E = P(W) * B - (1 - P(W)) * B
			card_heuristic = bet_amount * (2 * self.winning_probability - 1)
		win_rates_from_raise_history = self.WIN_RATES_FROM_RAISE_HISTORY[self.street][num_opponent_raise]
		opp_heuristic = bet_amount * (2 * win_rates_from_raise_history - 1)
		if ((win_rates_from_raise_history >= 0.0) 
			and (win_rates_from_raise_history <= 1.0) 
			and (self.round_count > self.MIN_NUM_DATA_COLLECTED)):
			value = (1 - self.opp_heuristic_weight) * card_heuristic + self.opp_heuristic_weight * opp_heuristic
		else:
			value = card_heuristic
		return value

	def re_calculate_probability(self):
		# if in PREFLOP, we check against expected value and reverse the equation 
		if self.street == self.STREET_ZERO_CARD:
			first_card = self.hole_card[0]
			second_card = self.hole_card[1]
			
			if self.CARD_NUM_DICT[first_card[1]] > self.CARD_NUM_DICT[second_card[1]]: #check number
				lower_card_number = second_card[1]
				higher_card_number = first_card[1]
			else:
				lower_card_number = first_card[1]
				higher_card_number = second_card[1]
			if first_card[0] == second_card[0]: #check same shape
				is_same_shape = True
			else:
				is_same_shape = False
			#reverse engineer equation, 2*Pr(win) = (Expected Value Per Bet) + 1
			self.preflop_expected_value = (
				self.PREFLOP_EXPECTED_VALUE[is_same_shape][lower_card_number][higher_card_number])
			self.winning_probability = (self.preflop_expected_value + 1) / 2

		#when not in PREFLOP
		else:
			self.winning_probability = estimate_hole_card_win_rate(
											nb_simulation = self.NB_SIMULATION,
											nb_player = 2,
											hole_card = gen_cards(list(self.hole_card)),
											community_card = gen_cards(list(self.community_card)))

	def pre_calculate_avg_raise_amount_remaining_street(self):
		total_raise_amount_value = 0
		for i in range(0, self.NUM_STREET_PER_ROUND):	#calculating raise amount sum of all 4 street
			total_raise_amount_value += self.RAISE_AMOUNT_DICT[i]
		num_remaining_street = self.NUM_STREET_PER_ROUND	#set to 4
		for i in range(0, self.NUM_STREET_PER_ROUND):	#calculate avg remaining raise for each street
			total_raise_amount_value -= self.RAISE_AMOUNT_DICT[i]
			num_remaining_street -= 1
			avg_raise_value = 0
			if num_remaining_street != 0:
				avg_raise_value = float(total_raise_amount_value) / num_remaining_street
			self.avg_raise_amount_remaining_street.append(avg_raise_value)

	def rounds_won(self, street_name):
		won = 0
		for x in self.RAISE_HISTORY[True][self.is_player_big_blind][street_name]:
			won += x
		return won

	def rounds_lost(self, street_name):
		lost = 0
		for x in self.RAISE_HISTORY[False][self.is_player_big_blind][street_name]:
			lost += x
		return lost

	def rounds_with_specific_raises(self, street_name, num_raises):
		result = (self.RAISE_HISTORY[False][self.is_player_big_blind][street_name][num_raises] 
					+ self.RAISE_HISTORY[True][self.is_player_big_blind][street_name][num_raises])
		return result
        
	# Use definition of conditional probability to calculate prob of winning given the num of raises made by opponent
	# Return a probability between 0.0 and 1.0 if success, and return -1.0 if cannot compute
	def win_chance_from_raise_history(self, street, num_raises):
		num_wins = self.rounds_won(street)
		num_lost = self.rounds_lost(street)
		prob_player_win_given_opp_raises = -1.0	#initialize to card winning probability in case cannot compute
		if (num_wins + num_lost != 0):
			prob_cur_opp_raises_and_player_win = (self.RAISE_HISTORY[True][self.is_player_big_blind][street][num_raises] 
														/ float(num_wins + num_lost))
			prob_opp_raises = self.rounds_with_specific_raises(street, num_raises) / float(num_wins + num_lost)
			if prob_opp_raises != 0:
				prob_player_win_given_opp_raises = prob_cur_opp_raises_and_player_win / prob_opp_raises
		return prob_player_win_given_opp_raises

def setup_ai():
	return Honest22Player()
