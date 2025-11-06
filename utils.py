def print_game_state(solver):
    print(f"Turn {solver.turn} | Possible: {len(solver.kb.possible)}")
    if len(solver.kb.possible) <= 10:
        print(f"Candidates: {', '.join(sorted(solver.kb.possible))}")