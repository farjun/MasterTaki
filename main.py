# here we will define all main functions we want to run
from Agents.MarkovAgents.MdpAgent import MDPAgent
from TakiGame.GameLogic.GameManager import GameManager
def run_MDP_agent(game):
    """

    :return:
    """

    mdp_agent = MDPAgent(game)
    game.run_game()
    game.print_scoring_table()

if __name__ == '__main__':
    players = [["Ido", "H"], ["Omer", "E"]]
    number_of_games = 2
    game = GameManager(players, number_of_games, print_mode=True)

    run_MDP_agent(game)
