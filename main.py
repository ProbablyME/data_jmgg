import streamlit as st
import os
import json
from PIL import Image
import requests
##----------------------------------

import pandas as pd
import time as tm
import os
import requests
import plotly

API_KEY = 'RGAPI-f5672a44-e896-46f0-a8e9-3f6afe819b79'


def get_puuid(gameName=None, tagLine=None, api_key=None):
    

    link = f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}?api_key={api_key}'

    response = requests.get(link)
    
    return response.json()

def get_riotidbyPuuid(puuid=None, api_key=None):
    
    link = f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={api_key}'

    response = requests.get(link)
    
    return f"{response.json()['gameName']}"

##{response.json()['tagLine']}

def get_puuid_by_summonerId(summonerId=None, api_key=None):
    link = f'https://europe.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}?api_key={api_key}'
    
    response = requests.get(link)
    
    return response.json()['puuid']



def get_ladder(top=3000):
    
    root = 'https://europe.api.riotgames.com/'
    chall = 'lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'
    gm = 'lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5'
    masters = 'lol/league/v4/masterleagues/by-queue/RANKED_SOLO_5x5'


    chall_response = requests.get(root + chall + '?api_key=' + api_key )
    chall_df = pd.DataFrame(chall_response.json()['entries']).sort_values('leaguePoints', ascending=False).reset_index(drop=True)
    gm_df= pd.DataFrame()
    masters_df = pd.DataFrame()
    if (top > 300): 
        gm_response = requests.get(root + gm + '?api_key=' + api_key )
        gm_df = pd.DataFrame(gm_response.json()['entries']).sort_values('leaguePoints', ascending=False).reset_index(drop=True)
    if (top > 1000):
        masters_response = requests.get(root + masters + '?api_key=' + api_key )
        masters_df = pd.DataFrame(masters_response.json()['entries']).sort_values('leaguePoints', ascending=False).reset_index(drop=True)
    
    ladder = pd.concat([chall_df, gm_df, masters_df])[:top].reset_index(drop=True)
    ladder = ladder.drop(columns='rank').reset_index(drop=False).rename(columns={'index':'rank'})
    
    ladder['rank'] += 1
    
    return ladder

def get_match_history(puuid=None, start=0, count=20):
    root = 'https://europe.api.riotgames.com/'
    endpoint = f'lol/match/v5/matches/by-puuid/{puuid}/ids?type=tourney&start={start}&count={count}'

    response = requests.get(root + endpoint + '&api_key=' + api_key)
    
    return response.json()


def get_match_data_from_id(matchId=None):
    root = 'https://europe.api.riotgames.com/'
    endpoint = f'lol/match/v5/matches/{matchId}'

    response = requests.get(root + endpoint + '?api_key=' + api_key)
    
    return response.json()

def get_match_data_from_id_at15(matchId=None):
    root = 'https://europe.api.riotgames.com/'
    endpoint = f'lol/match/v5/matches/{matchId}/timeline'

    response = requests.get(root + endpoint + '?api_key=' + api_key)
    
    return response.json()


def process_match_json(match_json, puuid):
    ##Architecture
    metadata = match_json['metadata']

    match_id = metadata['matchId']
    participants = metadata['participants']
    info = match_json['info']
    players = info['participants']
    teams = info['teams']
    player = players[participants.index(puuid)]
    perks = player['perks']
    stats = perks['statPerks']
    styles = perks['styles']
        
    primary = styles[0]
    secondary = styles[1]

    defense = stats['defense']
    flex = stats['flex']
    offense = stats['offense']

    game_creation = info['gameCreation']
    game_duration = info['gameDuration']
    game_start_timestamp = info['gameStartTimestamp']
    game_end_timestamp = info['gameEndTimestamp']
    patch = info['gameVersion']

    kills = player['kills']
    deaths = player['deaths']
    assists = player['assists']
    first_blood = player['firstBloodKill']

    champ_level = player['champLevel']
    champion_id = player['championId']
    champion_transform = player['championTransform']
    champion_name = player['championName']
    gold_earned = player['goldEarned']
    cs = player['neutralMinionsKilled']
    item0 = player['item0']
    item1 = player['item1']
    item2 = player['item2']
    item3 = player['item3']
    item4 = player['item4']
    item5 = player['item5']
    objectives_stolen = player['objectivesStolen']
    objectives_stolen_assist = player['objectivesStolenAssists']
    participant_id = player['participantId']
    player_puuid = player['puuid']
    riot_name = player['riotIdGameName']
    riot_tag = player['riotIdTagline']
    summoner1Id = player['summoner1Id']
    summoner2Id = player['summoner2Id']
    summonerId = player['summonerId']
    summonerName = player['summonerName']
    total_damage_dealt_to_champions = player['totalDamageDealtToChampions']
    total_damage_shielded_on_teammates = player['totalDamageShieldedOnTeammates']
    total_damage_taken = player['totalDamageTaken']
    total_heals_on_teammates = player['totalHealsOnTeammates']
    total_minions_killed = player['totalMinionsKilled']
    total_time_cc_dealt = player['totalTimeCCDealt']
    wards_placed = player['wardsPlaced']
    wards_killed = player['wardsKilled']
    vision_score = player['visionScore']
    win = player['win']


    vision_wards_bought_in_game = player['visionWardsBoughtInGame']
    role = player['role']
    lane = player['lane']




    primary_style = primary['style']
    secondary_style = secondary['style']

    primary_keystone = primary['selections'][0]['perk']
    primary_perk_1 = primary['selections'][1]['perk']
    primary_perk_2 = primary['selections'][2]['perk']
    primary_perk_3 = primary['selections'][3]['perk']


    secondary_perk_1 = secondary['selections'][0]['perk']
    secondary_perk_2 = secondary['selections'][1]['perk']
    # secondary_perk_3 = secondary['selections'][2]['perk']
    for team in teams:
        # bans = team['bans']
        if team['teamId'] == player['teamId']:
        
            obj = team['objectives']
            baron = obj['baron']
            dragon = obj['dragon']
            grubs = obj['horde']
            riftHerald = obj['riftHerald']
            tower = obj['tower']
            inhibitor = obj['inhibitor']
        
        # for obj in [baron, dragon, grubs, riftHerald, tower, inhibitor]:
        #     first = obj['first']
        #     obj_kills = obj['kills']

    match_df = pd.DataFrame({
        'match_id': [match_id],
        'participants': [participants],
        'defense': [defense],
        'flex': [flex],
        'offense': [offense],
        'info' : [info],
        'game_creation': [game_creation],
        'game_duration': [game_duration],
        'game_start_timestamp': [game_start_timestamp],
        'game_end_timestamp': [game_end_timestamp],
        'patch': [patch],
        'kills': [kills],
        'deaths': [deaths],
        'assists': [assists],
        'first_blood': [first_blood],
        'champ_level': [champ_level],
        'champion_id': [champion_id],
        'champion_transform': [champion_transform],
        'champion_name' : [champion_name],
        'gold_earned': [gold_earned],
        'cs': [cs],
        'item0': [item0],
        'item1': [item1],
        'item2': [item2],
        'item3': [item3],
        'item4': [item4],
        'item5': [item5],
        'objectives_stolen': [objectives_stolen],
        'objectives_stolen_assist': [objectives_stolen_assist],
        'participant_id': [participant_id],
        'player_puuid': [player_puuid],
        'riot_name': [riot_name],
        'riot_tag': [riot_tag],
        'summoner1Id': [summoner1Id],
        'summoner2Id': [summoner2Id],
        'summonerId': [summonerId],
        'summonerName': [summonerName],
        'total_damage_dealt_to_champions': [total_damage_dealt_to_champions],
        'total_damage_shielded_on_teammates': [total_damage_shielded_on_teammates],
        'total_damage_taken': [total_damage_taken],
        'total_heals_on_teammates': [total_heals_on_teammates],
        'total_minions_killed': [total_minions_killed],
        'total_time_cc_dealt': [total_time_cc_dealt],
        'wards_placed': [wards_placed],
        'wards_killed': [wards_killed],
        'vision_score': [vision_score],
        'win': [win],
        'vision_wards_bought_in_game': [vision_wards_bought_in_game],
        'role': [role],
        'primary_style': [primary_style],
        'secondary_style': [secondary_style],
        'primary_keystone': [primary_keystone],
        'primary_perk_1': [primary_perk_1],
        'primary_perk_2': [primary_perk_2],
        'primary_perk_3': [primary_perk_3],
        'secondary_perk_1': [secondary_perk_1],
        'secondary_perk_2': [secondary_perk_2],
        'lane':[lane],
        
        
        #IMPORTANT
        'players':[players]
        
        
        
        # 'baron': [baron],
        # 'dragon': [dragon],
        # 'grubs': [grubs],
        # 'riftHerald': [riftHerald],
        # 'tower': [tower],
        # 'inhibitor': [inhibitor]
    })
    return match_df

def get_direct_opponent(match_id= None, match_json = None, participantId= 0, puuid= None):
    players = process_match_json(match_json=match_json, puuid=puuid)['players']
    if participantId <= 5:
        return players[0][participantId+4]
    return players[0][participantId-6]

        
def json_extract(obj, key):
    arr = []
    def extract(obj, arr, key):
        if isinstance(obj, dict):
            for k,v in obj.items(): #k = key and v = value
                if k==key:
                    arr.append(v)
                elif isinstance(v, (dict, list)):
                    extract(v, arr, key)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
                
        return arr
    
    values = extract(obj, arr, key)
    return values

def get_rank_by_summonerName(gameName=None, tagLine=None, api_key=None):
    # First get PUUID from Riot ID
    account_info = get_puuid(gameName=gameName, tagLine=tagLine, api_key=api_key)
    puuid = account_info['puuid']
        
    # Get Summoner ID using PUUID
    link = f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}'
    response = requests.get(link)
    summoner_id = response.json()['id']
        
    # Get rank information using Summoner ID
    link = f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}'
    response = requests.get(link)
        
    # Find Solo/Duo queue rank
    for queue in response.json():
        if queue['queueType'] == 'RANKED_SOLO_5x5':
            return {
                    'tier': queue['tier'],
                    'rank': queue['rank'],
                    'leaguePoints': queue['leaguePoints'],
                    'wins': queue['wins'],
                    'losses': queue['losses']
                }
        
    return None  # Return None if no Solo/Duo rank found


def create_leaderboard(rank_data_list):
    """
    Creates a leaderboard from a list of rank data dictionaries.
    Each dictionary should contain tier, rank, leaguePoints, wins, losses.
    Returns a sorted pandas DataFrame.
    """
    # Create a dictionary to map tiers to numeric values for sorting
    tier_values = {
        'CHALLENGER': 9,
        'GRANDMASTER': 8, 
        'MASTER': 7,
        'DIAMOND': 6,
        'EMERALD': 5,
        'PLATINUM': 4,
        'GOLD': 3,
        'SILVER': 2,
        'BRONZE': 1,
        'IRON': 0
    }
    
    # Create a dictionary to map ranks to numeric values
    rank_values = {
        'I': 4,
        'II': 3,
        'III': 2,
        'IV': 1
    }
    
    # Convert rank data to DataFrame
    df = pd.DataFrame(rank_data_list)
    
    # Add numeric values for sorting
    df['tier_value'] = df['tier'].map(tier_values)
    df['rank_value'] = df['rank'].map(rank_values)
    
    # Calculate win rate
    df['win_rate'] = (df['wins'] / (df['wins'] + df['losses']) * 100).round(2)
    
    # Sort by tier, rank, and LP
    df_sorted = df.sort_values(
        by=['tier_value', 'rank_value', 'leaguePoints'],
        ascending=[False, False, False]
    )
    
    # Drop the numeric columns used for sorting
    df_sorted = df_sorted.drop(['tier_value', 'rank_value'], axis=1)
    
    # Reorder columns for better display
    column_order = ['tier', 'rank', 'leaguePoints', 'wins', 'losses', 'win_rate']
    df_sorted = df_sorted[column_order]
    
    return df_sorted

##-------------------------------------------------

def generer_leaderboard():
    players = [
    ('Dr Dre', 'Axo'),
    ('50 Cent', 'Maxou'), 
    ('Eminem', 'Drust'),
    ('UNGOLiANT', '001'),
    ('Snoop Dogg', 'PLYCK')
    ]

    axo, maxou, druust, dan, poly = None, None, None, None, None

    for i, (game_name, tag_line) in enumerate(players):
        try:

                
            if i == 0:
                axo = get_rank_by_summonerName(gameName=game_name, tagLine=tag_line, api_key=API_KEY)
            elif i == 1:
                maxou = get_rank_by_summonerName(gameName=game_name, tagLine=tag_line, api_key=API_KEY)
            elif i == 2:
                druust = get_rank_by_summonerName(gameName=game_name, tagLine=tag_line, api_key=API_KEY)
            elif i == 3:
                dan = get_rank_by_summonerName(gameName=game_name, tagLine=tag_line, api_key=API_KEY)
            elif i == 4:
                poly = get_rank_by_summonerName(gameName=game_name, tagLine=tag_line, api_key=API_KEY)
                
        except Exception as e:
            print(f"Error getting data for {game_name}#{tag_line}: {str(e)}")

    # Create a dictionary with all player data
    data = {
        'Axo': axo,
        'Maxou': maxou, 
        'Druust': druust,
        'Dan': dan,
        'Poly': poly
    }

    # Create DataFrame and transpose it
    df = pd.DataFrame(data).transpose()

    return df



# Répertoire contenant les icônes des champions
champ_icons = 'suivi_scrim/champ_icons'
item_icons = 'suivi_scrim/item_icons'

# Fonction principale
def main():
    st.title("Suivi des Performances")
    menu = ["Suivi Scrim", "Suivi SoloQ", "Stats"]
    choice = st.sidebar.selectbox("Choisissez une catégorie", menu)

    if choice == "Suivi Scrim":
        handle_scrim()
    elif choice == "Suivi SoloQ":
        handle_soloq()
    elif choice == "Stats":
        handle_stats()
# Fonction pour gérer la catégorie Scrim
def handle_scrim():
    st.subheader("Suivi des Scrims")
    scrim_path = 'suivi_scrim/json_matchs'
    
    if not os.path.exists(scrim_path):
        st.warning("Aucun scrim trouvé. Veuillez ajouter des fichiers JSON dans le dossier 'json_matchs/scrims'.")
        return
    
    scrim_files = [f for f in os.listdir(scrim_path) if f.endswith('.json')]
    if not scrim_files:
        st.warning("Aucun fichier de scrim disponible.")
        return

    for scrim_file in scrim_files:
        if st.button(f"Afficher le Scrim : {scrim_file}"):
            display_match_data(os.path.join(scrim_path, scrim_file))

# Fonction pour gérer la catégorie SoloQ
def handle_soloq():
    st.subheader("Suivi des SoloQ")
    
    display_soloq_profile()

# Fonction pour afficher le profil SoloQ
def display_soloq_profile():
    st.dataframe(generer_leaderboard())
    
    
    
def display_match_data(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    champions = [participant['SKIN'] for participant in data['participants']]
    kills = [participant['CHAMPIONS_KILLED'] for participant in data['participants']]
    deaths = [participant['NUM_DEATHS'] for participant in data['participants']]
    assists = [participant['ASSISTS'] for participant in data['participants']]
    items = [[participant[f"ITEM{j}"] for j in range(7)] for participant in data['participants']]

    # Display Head-to-Head Layout
    st.write("**Team Head-to-Head**")
    for i in range(5):  # Assuming 5 players per team
        row = st.columns([3, 1, 3])  # Column layout for head-to-head
        with row[0]:  # Team 1 Player
            display_champion_row(champions[i], kills[i], deaths[i], assists[i], items[i])
        with row[1]:  # VS Separator
            st.markdown("<h4 style='text-align: center;'>VS</h4>", unsafe_allow_html=True)
        with row[2]:  # Team 2 Player
            display_champion_row(champions[i + 5], kills[i + 5], deaths[i + 5], assists[i + 5], items[i + 5])

        # Add a horizontal line after each row
        st.markdown("<hr>", unsafe_allow_html=True)
    
    # Bouton pour retourner au menu de base
    if st.button("Retour au menu"):
        st.experimental_rerun()


def display_champion_row(champion, kills, deaths, assists, items):
    """Helper function to display champion, items, and stats in a row."""
    st.image(os.path.join(champ_icons, f"{champion}.png"), width=50, caption=champion)
    item_cols = st.columns(len(items))  # Create smaller columns for items
    for idx, item_id in enumerate(items):
        with item_cols[idx]:
            display_item_icon(item_id, inline=True)
    # Add K/D/A stats
    st.write(f"{kills}/{deaths}/{assists}")

def display_item_icon(item_id, inline=False):
    """Displays item icon with smaller size."""
    icon_path = os.path.join(item_icons, f"{item_id}.png")
    if os.path.exists(icon_path):
        st.image(icon_path, width=30 if inline else 50)  # Smaller size for inline
    else:
        st.write("?")



# Fonction pour gérer la catégorie Stats
def handle_stats():
    st.subheader("Statistiques des Champions")
    scrim_path = 'json_matchs'

    if not os.path.exists(scrim_path):
        st.warning("Aucun fichier JSON de scrim trouvé. Veuillez ajouter des fichiers JSON dans le dossier 'json_matchs'.")
        return

    scrim_files = [f for f in os.listdir(scrim_path) if f.endswith('.json')]
    if not scrim_files:
        st.warning("Aucun fichier JSON de scrim disponible.")
        return

    # Récupération des données des champions
    champion_stats = collect_champion_stats(scrim_path, scrim_files)

    if champion_stats.empty:
        st.warning("Aucune donnée de champion trouvée.")
        return

    # Affichage des statistiques des champions
    st.dataframe(champion_stats)


# Fonction pour collecter les statistiques des champions
def collect_champion_stats(scrim_path, scrim_files):
    champion_data = {}

    for scrim_file in scrim_files:
        file_path = os.path.join(scrim_path, scrim_file)
        with open(file_path, 'r') as f:
            data = json.load(f)

        participants = data['participants']
        for participant in participants:
            champion = participant['SKIN']
            win = participant['WIN']  # Suppose que WIN est un booléen dans les JSON
            if champion not in champion_data:
                champion_data[champion] = {'Games Played': 0, 'Wins': 0, 'Losses': 0}
            champion_data[champion]['Games Played'] += 1
            if win:
                champion_data[champion]['Wins'] += 1
            else:
                champion_data[champion]['Losses'] += 1

    # Conversion en DataFrame
    champion_stats = pd.DataFrame.from_dict(champion_data, orient='index')
    champion_stats['Win Rate (%)'] = (champion_stats['Wins'] / champion_stats['Games Played'] * 100).round(2)

    # Réorganisation des colonnes
    champion_stats = champion_stats.reset_index().rename(columns={'index': 'Champion'})
    champion_stats = champion_stats[['Champion', 'Games Played', 'Wins', 'Losses', 'Win Rate (%)']]

    return champion_stats

# Exécuter l'application
if __name__ == "__main__":
    main()
