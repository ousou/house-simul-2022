import csv
import random
import argparse
from collections import Counter
import numpy as np


def read_races(file_name):
    race_to_lean = {}
    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            race, lean = row
            race = race.strip()
            lean = lean.strip()
            race_to_lean[race] = lean
            line_count += 1
        print(f'Processed {line_count} lines.')
        print(f'race_to_lean size {len(race_to_lean)}')
    return race_to_lean


def simulate_one_race(dem_probs):
    dem_wins = 0
    for race_prob in dem_probs:
        if random.random() < race_prob:
            dem_wins += 1
    return dem_wins

def create_race_dem_probs(race_to_lean, lean_prob):
    race_to_dem_prob = {}
    for race, lean in race_to_lean.items():
        if lean.lower() == "toss-up":
            race_to_dem_prob[race] = 0.5
        elif lean.lower() == "lean-d":
            race_to_dem_prob[race] = lean_prob
        elif lean.lower() == "lean-r":
            race_to_dem_prob[race] = 1 - lean_prob
        else:
            raise RuntimeError(f"Unknown lean {lean} for race {race}")
    return race_to_dem_prob

def simulate_outcome(race_to_dem_prob, dem_seats_needed, simulations):
    dem_total_wins = 0
    dem_seat_win_counter = Counter()
    for _  in range(simulations):
        dem_seat_wins = simulate_one_race(race_to_dem_prob.values())
        if dem_seat_wins >= dem_seats_needed:
            dem_total_wins += 1
        dem_seat_win_counter[dem_seat_wins] += 1
    print("dem_seats_needed", dem_seats_needed)
    print("dem_total_wins", dem_total_wins)
    print("dem_seat_win_counter", dem_seat_win_counter)
    exact_probs = calculate_exact_dem_win_probabilities(race_to_dem_prob.values())
    print("exact_probs", exact_probs)
    exact_win_prob = sum(exact_probs[:len(exact_probs) - dem_seats_needed])
    print("exact_win_prob", exact_win_prob)
    return dem_total_wins / simulations

def do_simulation(race_file_name, dem_seats_needed, lean_prob, simulations):
    race_to_lean = read_races(race_file_name)
    race_to_dem_prob = create_race_dem_probs(race_to_lean, lean_prob)
    dem_win_prob = simulate_outcome(race_to_dem_prob, dem_seats_needed, simulations)
    return dem_win_prob

def calculate_exact_dem_win_probabilities(dem_probs):
    dem_prob_list = []
    for dem_prob in dem_probs:
        dem_prob_list.append([dem_prob, 1 - dem_prob])
    full_probs = dem_prob_list[0]
    for next in dem_prob_list[1:]:
        full_probs = np.convolve(full_probs, next)

    return full_probs


def parse_arguments():
    parser = argparse.ArgumentParser(description='House win simulator')
    parser.add_argument('--race_file_name', type=str, default='races.csv')
    parser.add_argument('--lean_prob', type=float, default=0.8,
                        help='Win probability for a lean race')
    parser.add_argument('--simulations', type=int, default=100000, metavar='N',
                        help='Number of simulations to run')
    parser.add_argument('--dem_seats_needed', type=int, metavar='N',
                        help='How many seats democrats need to win')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    print(f"Arguments: {args}")
    dem_win_prob = do_simulation(race_file_name=args.race_file_name,
                                 dem_seats_needed=args.dem_seats_needed,
                                 lean_prob=args.lean_prob,
                                 simulations=args.simulations)
    print(f"Dem win prob: {dem_win_prob}")
