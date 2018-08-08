# here we will define all main functions we want to run
from TakiGame.GameLogic.GameManager import GameManager, PLAYER, PLAYER_TYPE
import pickle
import os
from collections import Counter
import sys
from matplotlib import pyplot

mdp_weights_path = '/tmp/weights/MDP_weights.pickle'
pomdp_weights_path = '/tmp/weights/POMDP_weights.pickle'

HEURISTIC = "-heuristic"
ALPHA_BETA = "-alpha"
EXPECTIMAX = "-expectimax"
MDP = "-mdp"
POMDP = "-pomdp"
MANUAL = "-manual"
DISCOUNT_INDEX = 10
EPSILON_INDEX = 9
LEVELS_INDEX = 8


def check_pickle_file_path(path):
    c = Counter()
    if os.path.getsize(path) > 0:
        with open(path, 'rb') as outputfile:
            c = pickle.load(outputfile)
    return c


def train_MDP_agent(game, number_of_training_for_session=1000):
    """
    trains the mdp agent for one session of number_of_traning_for_session games
    :param game:
    :param number_of_traning_for_session:
    :return: the number of new state-action combination he saw during the session
    """
    # pre_session_number_of_state_observed = len(set([state for state, action in game.players[1][PLAYER].Q_values]))
    # print("starting new session with current learned states : ", pre_session_number_of_state_observed)
    game.players[1][PLAYER].init_repeat_counter()

    for i in range(number_of_training_for_session):
        game.run_single_game(True)

    # post_session_number_of_state_observed = len(set([state for state, action in game.players[1][PLAYER].Q_values]))
    # print("ended new session with current learned states : ", post_session_number_of_state_observed)
    # print("Difference in this iteration: ", post_session_number_of_state_observed - pre_session_number_of_state_observed)
    print("Number of repeated state-action updates: ", game.players[1][PLAYER].get_repeat_counter())

    # return post_session_number_of_state_observed - pre_session_number_of_state_observed


def save_weights_to_pickle_file(game):
    print("start save pickles")
    for player in game.players.values():
        if player[PLAYER_TYPE] == "POMDPAgent":
            counter_to_save = player[PLAYER].Q_values
            with open(pomdp_weights_path, 'wb') as outputfile:
                pickle.dump(counter_to_save, outputfile)

        if player[PLAYER_TYPE] == "MDPAgent":
            counter_to_save = player[PLAYER].Q_values
            with open(mdp_weights_path, 'wb') as outputfile:
                pickle.dump(counter_to_save, outputfile)
    print("end save pickles")


def parse_agent(agents_type):
    """
    Parse the agents types
    :param agents_type: A list that is containing two agent types
    :return: A list of the players
    """
    agents = []
    for i in range(len(agents_type)):
        if agents_type[i] == HEURISTIC:
            agents.append(["player_{}".format(i), "H"])
        elif agents_type[i] == ALPHA_BETA:
            agents.append(["player_{}".format(i), "A"])
        elif agents_type[i] == EXPECTIMAX:
            agents.append(["player_{}".format(i), "E"])
        elif agents_type[i] == MDP:
            agents.append(["player_{}".format(i), "MDP"])
        elif agents_type[i] == POMDP:
            agents.append(["player_{}".format(i), "POMDP"])
        elif agents_type[i] == MANUAL:
            agents.append(["player_{}".format(i), "M"])
        else:
            print("wrong usage: agent wasn't recognised")
            exit(1)
    return agents


def parse_num_of_games(num_of_games):
    """
    Extract the number of games
    :param num_of_games: suppose to be a positive int
    :return: number of games to be played
    """
    if num_of_games.isdigit():
        num_of_games = int(num_of_games)
        if num_of_games > 0:
            return num_of_games
    print("the number of games must be a positive int")
    exit(1)


def parse_levels_for_tree_agent(levels):
    """
    Extract the levels in which the tree will grow
    :param levels: How deep will the recursion go
    :return: levels
    """
    if 1 <= levels <= 3:
        return levels
    print("the levels parameter must be between 1 and 3")
    exit(1)


def parse_optional_agruments(arguments):
    """
    Extract the levels,discount and epsilon parameters if they exists
    :param arguments: an unknown number of parameters
    :return: levels,discount and epsilon parameters if they exists
    """
    levels = discount = epsilon = None
    for param in arguments:
        if param.startswith("-levels="):
            levels = parse_levels_for_tree_agent(int(param[LEVELS_INDEX:]))
        elif param.startswith("-discount="):
            discount = float(param[DISCOUNT_INDEX:])
        elif param.startswith("-epsilon="):
            epsilon = float(param[EPSILON_INDEX:])
    # give them the default value
    if levels is None:
        levels = 2
    if discount is None:
        discount = 0.1
    if epsilon is None:
        epsilon = 0.05
    return levels, discount, epsilon


def parser():
    """
    Parse the script parameters
    :return: players, number_of_games, levels, discount, epsilon
    """
    if len(sys.argv) < 4:
        print("wrong usage: two players must enter the game and the number of games must be specified")
        exit(1)

    if len(sys.argv) > 7:
        print("wrong usage of the script parameters")
    players = parse_agent(sys.argv[1:3])
    number_of_games = parse_num_of_games(sys.argv[3])
    levels = discount = epsilon = None
    if len(sys.argv) > 4:
        arguments = sys.argv[4:]
        levels, discount, epsilon = parse_optional_agruments(arguments)

    return players, number_of_games, levels, discount, epsilon


def test_alphabeta_vs_reflex(num_of_iterations):
    players, number_of_games, levels, discount, epsilon = parser()
    winning_percentages = [0]*num_of_iterations
    timed_out_counter = 0
    for i in range(num_of_iterations):
        print("Start iteration number %d" % (i+1))
        game = GameManager(players, number_of_games, levels, discount, epsilon, print_mode=False)
        game.run_game()  # run the test
        game.print_scoring_table()
        winning_percentages[i-1] = game.get_player_score(0)/number_of_games  # insert alphabeta agent index
        timed_out_counter += game.get_player(0).get_timed_out_counter()
        print("Finish iteration number %d" % (i + 1))
    print("The average alpha beta winning percentage is %6.2f" % (sum(winning_percentages) / num_of_iterations))
    print("The average number of timed out actions each game is %6.2f" % (timed_out_counter/(number_of_games*num_of_iterations)))
    pyplot.plot(range(1, len(winning_percentages)+1), winning_percentages)
    pyplot.xlabel("Iteration number")
    pyplot.ylabel("Alpha-Beta winning percentage")
    pyplot.title("Alpha Beta with depth %d vs reflex agent\n%d games in each iteration" % (levels, number_of_games))
    pyplot.show()


def load_and_train_MDP():
    counter_weights = list()
    counter_weights.append(check_pickle_file_path(mdp_weights_path))
    counter_weights.append(check_pickle_file_path(pomdp_weights_path))
    players = [["Ido", "H"], ["Shachar", "POMDP"]]
    number_of_games = 50
    number_of_training = 1000
    game = GameManager(players, number_of_games, levels=2, epsilon=0.05, discount=0.1, print_mode=False, counter_weights_list=counter_weights)

    for i in range(1, 1001):
        train_MDP_agent(game, number_of_training)
        if i % 30 == 0:
            save_weights_to_pickle_file(game)


def run_from_parser():
    players, number_of_games, levels, discount, epsilon = parser()
    game = GameManager(players, number_of_games, levels, discount, epsilon, print_mode=True)
    game.run_game()  # run the test
    game.print_scoring_table()


if __name__ == '__main__':
    # load_and_train_MDP()
    # run_from_parser()
    test_alphabeta_vs_reflex(10)







