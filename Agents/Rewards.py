from TakiGame.GameLogic.State import TwoPlayerState
TERMINAL_STATE_SCORE = 100


def total_cards_dropped_reward(state: TwoPlayerState, action, next_state: TwoPlayerState)->int:
    if len(next_state.cur_player_cards) == 0:
        # if true, current game is over, check who is the winner
        if state.cur_player_index == next_state.cur_player_index:
            return TERMINAL_STATE_SCORE
        else:
            return -TERMINAL_STATE_SCORE
    return (len(state.get_cur_player_cards()) - len(next_state.get_cur_player_cards()))*10

