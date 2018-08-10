# here we will define all main functions we want to run
from TakiGame.GameLogic.GameManager import GameManager, PLAYER, PLAYER_TYPE
import pickle
import os
from collections import Counter
import sys
from matplotlib import pyplot

mdp_weights_path = './weights/MDP_weights.pickle'
pomdp_weights_path = './weights/POMDP_weights.pickle'
approximate_weights_path = './weights/APPROXIMATE_weights.pickle'

HEURISTIC = "-heuristic"
ALPHA_BETA = "-alpha"
EXPECTIMAX = "-expectimax"
MDP = "-mdp"
POMDP = "-pomdp"
MANUAL = "-manual"
APPROX = "-approximate"
DISCOUNT = "-discount="
EPSILON = "-epsilon="
LEVELS = "-levels="
PRINT_MODE = "-print_mode="


def check_pickle_file_path(path):
    if path == approximate_weights_path:
        c = None
    else:
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
    game.players[1][PLAYER].init_repeat_counter()
    if game.players[1][PLAYER_TYPE] == "FeatureAgent":
        print("Weights before current training: ", game.players[1][PLAYER].get_weights())

    for i in range(number_of_training_for_session):
        game.run_single_game(True)

    if game.players[1][PLAYER_TYPE] == "FeatureAgent":
        print("Weights after current training: ", game.players[1][PLAYER].get_weights())
    else:
        print("Number of NON repeated state-action updates: ", game.players[1][PLAYER].get_non_repeat_counter())
        print("Number of repeated state-action updates: ", game.players[1][PLAYER].get_repeat_counter())


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

        if player[PLAYER_TYPE] == "FeatureAgent":
            counter_to_save = player[PLAYER].Q_values
            with open(approximate_weights_path, 'wb') as outputfile:
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
        elif agents_type[i] == APPROX:
            agents.append(["player_{}".format(i), "APPROX"])
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


def parse_optional_arguments(arguments):
    """
    Extract the levels,discount and epsilon parameters if they exists
    :param arguments: an unknown number of parameters
    :return: levels,discount and epsilon parameters if they exists
    """
    levels = discount = epsilon = None
    print_mode = False
    for param in arguments:
        if param.startswith(LEVELS):
            levels = parse_levels_for_tree_agent(int(param[len(LEVELS):]))
        elif param.startswith(DISCOUNT):
            discount = float(param[len(DISCOUNT):])
        elif param.startswith(EPSILON):
            epsilon = float(param[len(EPSILON):])
        elif param.startswith(PRINT_MODE):
            print_mode = param[len(PRINT_MODE):] == "True"
    return levels, discount, epsilon, print_mode


def parser():
    """
    Parse the script parameters
    :return: players, number_of_games, levels, discount, epsilon
    """
    if len(sys.argv) < 4:
        print("wrong usage: two players must enter the game and the number of games must be specified")
        exit(1)

    if len(sys.argv) > 8:
        print("wrong usage of the script parameters")
    players = parse_agent(sys.argv[1:3])
    number_of_games = parse_num_of_games(sys.argv[3])
    print_mode = False
    if len(sys.argv) > 4:
        arguments = sys.argv[4:]
        levels, discount, epsilon, print_mode = parse_optional_arguments(arguments)
    else:
        # give them the default value
        levels = 2
        discount = 0.1
        epsilon = 0.05

    return players, number_of_games, levels, discount, epsilon, print_mode


def test_alphabeta_vs_reflex(num_of_iterations):
    players, number_of_games, levels, discount, epsilon, print_mode = parser()
    winning_percentages = [0]*num_of_iterations
    timed_out_counter = 0
    for i in range(num_of_iterations):
        print("Start iteration number %d" % (i+1))
        game = GameManager(players, number_of_games, levels, discount, epsilon, print_mode=print_mode)
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


def load_counter_weights():
    counter_weights = list()
    #counter_weights.append(check_pickle_file_path(mdp_weights_path))
    #counter_weights.append(check_pickle_file_path(pomdp_weights_path))
    counter_weights.append(check_pickle_file_path(approximate_weights_path))
    return counter_weights


def load_and_train_reinforcement(approximate=False):
    counter_weights = [None,None,None]
    #counter_weights = load_counter_weights()
    if approximate:
        players = [["Ido", "H"], ["Shachar", "APPROX"]]
    else:
        players = [["Ido", "H"], ["Shachar", "H"]]
    number_of_games = 100
    number_of_training = 1000
    game = GameManager(players, number_of_games, levels=2, epsilon=0.05, discount=0.1, print_mode=False, counter_weights_list=counter_weights)

    for i in range(1, 1001):
        print("Start train session")
        train_MDP_agent(game, number_of_training)
        print("End train session")
        if i % 10 == 0:
            save_weights_to_pickle_file(game)
            test_game = game = GameManager(players, number_of_games, levels=2, epsilon=0.05, discount=0.1, print_mode=False, counter_weights_list=load_counter_weights())
            test_game.run_game()
            test_game.print_scoring_table()


def run_from_parser():
    counter_weights = load_counter_weights()
    players, number_of_games, levels, discount, epsilon, print_mode = parser()
    game = GameManager(players, number_of_games, levels, discount, epsilon, print_mode=print_mode, counter_weights_list=counter_weights)
    game.run_game()  # run the test
    game.print_scoring_table()


if __name__ == '__main__':
    load_and_train_reinforcement(True)
    # run_from_parser()
    # test_alphabeta_vs_reflex(5)







