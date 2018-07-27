from TakiGame.GameLogic.State import TwoPlayerState

def total_cards_dropped_reward(state:TwoPlayerState,action,next_state:TwoPlayerState)->int:
    return (len(next_state.get_cur_player_cards()) - len(state.get_cur_player_cards()))*10

