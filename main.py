# here we will define all main functions we want to run
from TakiGame.GameLogic.GameManager import GameManager, PLAYER, PLAYER_TYPE
import pickle
import os
from collections import Counter

mdp_weights_path = './weights/MDP_weights.pickle'
pomdp_weights_path = './weights/POMDP_weights.pickle'


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
    pre_session_number_of_state_observed = len(set([state for state, action in game.players[1][PLAYER].Q_values]))
    print("starting new session with current learned states : ", pre_session_number_of_state_observed)

    for i in range(number_of_training_for_session):
        game.run_single_game(True)

    post_session_number_of_state_observed = len(set([state for state, action in game.players[1][PLAYER].Q_values]))
    print("ended new session with current learned states : ", post_session_number_of_state_observed)
    print("Difference in this iteration: ", post_session_number_of_state_observed - pre_session_number_of_state_observed)

    return post_session_number_of_state_observed - pre_session_number_of_state_observed


def save_weights_to_pickle_file(game):
    for player in game.players.values():
        if player[PLAYER_TYPE] == "POMDPAgent":
            counter_to_save = player[PLAYER].Q_values
            with open(pomdp_weights_path, 'wb') as outputfile:
                pickle.dump(counter_to_save, outputfile)

        if player[PLAYER_TYPE] == "MDPAgent":
            counter_to_save = player[PLAYER].Q_values
            with open(mdp_weights_path, 'wb') as outputfile:
                pickle.dump(counter_to_save, outputfile)


if __name__ == '__main__':
    counter_weights = list()
    counter_weights.append(check_pickle_file_path(mdp_weights_path))
    counter_weights.append(check_pickle_file_path(pomdp_weights_path))
    # players, number_of_games = readCommand( sys.argv[1:] ) # Get game components based on input
    players = [["Ido", "H"], ["Shachar", "POMDP"]]
    number_of_games = 150
    number_of_training = 1000
    game = GameManager(players, number_of_games, print_mode=True, counter_weights_list=counter_weights)

    new_states_observed = 100
    #while new_states_observed >= 100:
    for i in range(1):
        new_states_observed = train_MDP_agent(game)
        save_weights_to_pickle_file(game)

    game.run_game()  # run the test
    game.print_scoring_table()
    print(len(game.players[1]))