from TakiGame.GameLogic.State import TwoPlayerState
TERMINAL_STATE_SCORE = 100


def total_cards_dropped_reward(state: TwoPlayerState, action, next_state: TwoPlayerState)->int:

    return (len(state.get_cur_player_cards()) - len(next_state.get_cur_player_cards()))*10

