#!/usr/bin/env python
import pandas as pd
import numpy as np
import json

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_pokemon_details(pokemon_csv_file_name: str):
    """Reads a csv file of tabular pokemon data and returns Pandas dataframe"""
    pokemon_details = pd.read_csv('pokemon.csv')
    pokemon_details.set_index('name', drop=True, inplace=True)
    pokemon_details.loc[pokemon_details['type_1']=='Fight','type_1'] = 'Fighting'

    return pokemon_details


def get_type_details(type_csv_file_name: str):
    """Reads a csv file of tabular pokemon type data and returns Pandas dataframe"""
    types = pd.read_csv('types.csv')
    types.set_index('type', drop=True, inplace=True)

    return types


def get_team_advantages(battle_team: list, pokemon_details, types) -> set:
    """
    For a specified battle team, gets all type advantages
    and returns them as a set
    """
    team_strengths = set()

    for pokemon in battle_team:
        type_1 = pokemon_details[pokemon_details.index==pokemon]['type_1'].values[0]
        type_2 = pokemon_details[pokemon_details.index==pokemon]['type_2'].values[0]
        strong_against = types[types.index==type_1][['super_1', 'super_2', 'super_3', 'super_4', 'super_5']].values.tolist()[0]

        if type_2 is not np.nan:
            strong_against_2 = types[types.index==type_2][['super_1','super_2','super_3','super_4','super_5']].values.tolist()[0]
            strong_against = strong_against + strong_against_2

        strong_against = set([strength for strength in strong_against if strength is not np.nan and strength != '--'])
        team_strengths = team_strengths.union(strong_against)

    return team_strengths


def build_battle_team(battle_team: list, pokemon_details, types) -> None:
    """
    Given a specific list of acceptable pokemon, puts together all
    potential combinations of pokemon into different battle teams of
    size six. If the battle team has advantages against all potential
    pokemon types, then it logs the battle team to a flat file.
    """
    pokemon_list = list(pokemon_details.index)

    if len(battle_team) < 6:
        for pokemon in pokemon_list:
            if pokemon not in battle_team:
                build_battle_team(battle_team + [pokemon], pokemon_details, types)
    else:
        team_advantages = get_team_advantages(battle_team, pokemon_details, types)
        if len(team_advantages) >= 15:
            logging.info("Successful combo!: {}".format(battle_team))
            with open('file.txt', 'a+') as outfile:
                battle_team = {'battle_team': battle_team,
                               'num_advantages': len(team_advantages)}
                outfile.write(json.dumps(battle_team))
                outfile.write('\n')

    return None


if __name__=="__main__":

    pokemon_details = get_pokemon_details('pokemon.csv')
    types = get_type_details('types.csv')

    battle_team = []
    build_battle_team(battle_team, pokemon_details, types)
