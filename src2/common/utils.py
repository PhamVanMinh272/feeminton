def count_turns_on_games(game_records: str):
    """
    Example:
        1. Anna Bob - Kim Kong
    Return:
        {
        'Anna': 1,
        'Bob': 1,
        'Kim': 1,
        'Kong': 1,
        }
    """
    game_records = game_records.strip()
    games = game_records.split("\n")
    turns_on_games = 0
    persons_turn_count = {}
    for game in games:
        person_names = get_person_names_on_game(game)
        for person_name in person_names:
            if person_name in persons_turn_count:
                persons_turn_count[person_name] += 1
            else:
                persons_turn_count[person_name] = 1
    return persons_turn_count

def get_person_names_on_game(game_record: str):
    print(game_record)
    # remove special characteristic in game_record, keep alphabet character only
    import re
    # [^a-zA-Z0-9 ] matches everything EXCEPT letters, numbers, and spaces
    cleaned_text = re.sub(r'[^a-zA-Z ]', '', game_record).strip()

    print(cleaned_text)
    cleaned_text = " ".join(cleaned_text.split())
    print(cleaned_text)
    person_names = cleaned_text.split(" ")
    print(person_names)
    return person_names


if __name__ == '__main__':
    game_records_data = """
    1. Anna Bob - Kim Kong
    2. Anna Chin - Kim Kong
    """
    rs = count_turns_on_games(game_records_data)
    print(rs)
