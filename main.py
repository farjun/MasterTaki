# here we will define all main functions we want to run
from TakiGame.GameLogic.GameManager import GameManager, PLAYER, PLAYER_TYPE
import pickle
import os
from collections import Counter
import sys
from matplotlib import pyplot
import numpy as np

approximate_weights_path = './weights/APPROXIMATE_weights.pickle'

HEURISTIC = "-heuristic"
ALPHA_BETA = "-alpha"
EXPECTIMAX = "-expectimax"
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
            if path == approximate_weights_path:
                c = [pickle.load(outputfile), pickle.load(outputfile)]

    return c


def train_MDP_agent(game, number_of_training_for_session=100):
    """
    trains the mdp agent for one session of number_of_traning_for_session games
    :param game:
    :param number_of_traning_for_session:
    :return: the number of new state-action combination he saw during the session
    """
    game.players[1][PLAYER].init_repeat_counter()
    print("Weights before current training: \n", game.players[1][PLAYER].get_weights_with_names())

    for i in range(number_of_training_for_session):
        game.run_single_game(True)

    print("Weights after current training: \n", game.players[1][PLAYER].get_weights_with_names())
    game.players[1][PLAYER].decay_alpha()


def save_weights_to_pickle_file(game):
    print("start save pickles")
    for player in game.players.values():
        if player[PLAYER_TYPE] == "FeatureAgent":
            counter_to_save = player[PLAYER].Q_values
            iteration_number = player[PLAYER].t
            with open(approximate_weights_path, 'wb') as outputfile:
                pickle.dump(counter_to_save, outputfile)
                pickle.dump(iteration_number, outputfile)
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
    # give them the default value
    levels = 2
    discount = 0.1
    epsilon = 0.05
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
    arguments = sys.argv[4:]
    levels, discount, epsilon, print_mode = parse_optional_arguments(arguments)

    return players, number_of_games, levels, discount, epsilon, print_mode


def test_and_plot(num_of_iterations):
    counter_weights = load_counter_weights()
    players, number_of_games, levels, discount, epsilon, print_mode = parser()
    winning_percentages = [0] * num_of_iterations
    game = None
    for i in range(num_of_iterations):
        print("Start iteration number %d" % (i + 1))
        game = GameManager(players, number_of_games, levels, discount, epsilon, print_mode=print_mode, counter_weights_list=counter_weights)
        game.run_game()  # run the test
        game.print_scoring_table()
        winning_percentages[i] = game.get_player_score(0) / number_of_games  # insert reinforcement agent index
        print("Finish iteration number %d" % (i + 1))
    player_1_type = game.get_player_type(0)
    player_2_type = game.get_player_type(1)
    print("The average %s winning percentage is %6.2f" % (player_1_type, sum(winning_percentages) / num_of_iterations))
    pyplot.plot(range(1, len(winning_percentages) + 1), winning_percentages)
    pyplot.xlabel("Iteration number")
    pyplot.ylabel("%s winning percentage" % player_1_type)
    title = "%s vs %s\n%d games in each iteration" % (player_1_type, player_2_type,number_of_games)
    if player_1_type == "AlphaBetaPruning" or player_2_type == "AlphaBetaPruning":
        title += "\nAlpha Beta with depth " + str(levels)
    pyplot.title(title)
    pyplot.show()


def load_counter_weights():
    counter_weights = list()
    counter_weights.append(check_pickle_file_path(approximate_weights_path))
    return counter_weights


def load_and_train_reinforcement():
    counter_weights = load_counter_weights()
    players = [["Ido", "H"], ["Shachar", "APPROX"]]
    number_of_games = 100
    number_of_training = 1000
    number_of_iterations_before_testing = 5
    winning_percentages = []
    game = GameManager(players, number_of_games, levels=2, epsilon=0.05, discount=0.1, print_mode=False, counter_weights_list=counter_weights)

    for i in range(1, 10001):
        print("Start train session")
        previous_weights = game.get_player(1).get_weights()
        train_MDP_agent(game, number_of_training)
        current_weights = game.get_player(1).get_weights()
        print("End train session")
        if i % number_of_iterations_before_testing == 0:
            save_weights_to_pickle_file(game)
            test_game = game = GameManager(players, number_of_games, levels=2, epsilon=0.05, discount=0.1, print_mode=False, counter_weights_list=load_counter_weights())
            test_game.run_game()
            test_game.print_scoring_table()
            winning_percentages.append(test_game.get_player_score(1) / number_of_games)  # insert reinforcement agent index
        if np.linalg.norm(current_weights - previous_weights) < 5:
            print("Weights converged after %d training iterations" % i)
            break
    number_of_training_games_played = [i*number_of_iterations_before_testing*number_of_training for i in range(1, len(winning_percentages)+1)]
    pyplot.plot(number_of_training_games_played, winning_percentages)
    pyplot.xlabel("Number of training games played")
    pyplot.ylabel("Reinforcement winning percentage")
    pyplot.title("Feature agent winning percentage against Heuristic agent\nAs function of number of training games")
    pyplot.show()


def run_from_parser():
    counter_weights = load_counter_weights()
    players, number_of_games, levels, discount, epsilon, print_mode = parser()
    game = GameManager(players, number_of_games, levels, discount, epsilon, print_mode=print_mode, counter_weights_list=counter_weights)
    game.run_game()  # run the test
    game.print_scoring_table()


if __name__ == '__main__':
    # load_and_train_reinforcement()
    run_from_parser()
    # test_and_plot(10)







