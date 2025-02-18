import streamlit as st
st.set_page_config(layout="wide")
import os
import json
from PIL import Image

import pandas as pd
import time as tm
import os
import plotly

import time
import requests
from datetime import datetime, timedelta

API_KEY = 'RGAPI-f5672a44-e896-46f0-a8e9-3f6afe819b79'

axo='wBk00t9-kh2cqBqW1Vk2N7XuYXOGW9g40uLNf8_bNGvEbm6erOlZ0CzEsiSkKYFKZ4mTIA9SN3BvUg'
maxou='8-3RjS7qonoe4jnZ0r7aimehAVc1B2eusvnTD5_RFe43sL7ci6u9WMQwlgC4RMxpuoLVT5iCapY1Kw'
druust='VWA4wNDoutiB2QlJjYJBb75LX097ZQUT-jYxcu5MSDe5_G9EJ0My7wrotHsy3RW8ywUFzX9ekFptmQ'
dan='qtzVLEw5NZxPu8v8lAmRXBQHBUgahfu3jwNghfYT2njtsNi_RReRXc8IxWyhDuoCp98qd80Ppo4ONg'
poly='yLiS_46rBuUzrB1bnNjcCFMSuZX1_pngso519a5BapGBT2OnnYyuuNBIDnXeQwsUlW0HpOE7tU4azw'





def request(url):
    while True:
        request = requests.get(url)
        # Works
        if request.status_code == 200:
            break
        # No data found
        elif request.status_code == 404:
            return(404)
        # Too much requests
        elif request.status_code == 429:
            print("Too much requests.")
            time.sleep(120)
    return request # Retourne la requete

def get_rank_by_summonerName(gameName=None, tagLine=None, api_key=None):
    # Obtenir le PUUID depuis Riot ID
    account_info = get_puuid(gameName=gameName, tagLine=tagLine, api_key=api_key)
    puuid = account_info['puuid']
    
    # Obtenir l'ID du Summoner à partir du PUUID
    link = f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}'
    response = request(link)
    summoner_id = response.json()['id']

    # Pause pour respecter les limites de taux
    time.sleep(1.2)

    # Obtenir les informations de rang via l'ID du Summoner
    link = f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}'
    response = request(link)    
    # Chercher le rang Solo/Duo
    for queue in response.json():
        if queue['queueType'] == 'RANKED_SOLO_5x5':
            return {
                'tier': queue['tier'],
                'rank': queue['rank'],
                'leaguePoints': queue['leaguePoints'],
                'wins': queue['wins'],
                'losses': queue['losses']
            }
    return None

def generer_leaderboard():
    players = [
        ('Dr Dre', 'Axo'),
        ('50 Cent', 'Maxou'),
        ('Eminem', 'Drust'),
        ('UNGOLiANT', '001'),
        ('Snoop Dogg', 'PLYCK')
    ]

    data = {}

    for game_name, tag_line in players:
        try:
            # Obtenir les informations de rang
            rank_data = get_rank_by_summonerName(gameName=game_name, tagLine=tag_line, api_key=API_KEY)
            
            # Obtenir l'historique des matchs pour les 7 derniers jours
            account_info = get_puuid(gameName=game_name, tagLine=tag_line, api_key=API_KEY)
            puuid = account_info['puuid']
            end_time = int(datetime.utcnow().timestamp())
            start_time = int((datetime.utcnow() - timedelta(days=7)).timestamp())
            match_history_url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={start_time}&endTime={end_time}&start=0&count=100&api_key={API_KEY}'
            response = request(match_history_url)
            matches = response.json()

            # Analyser les victoires et défaites
            wins, losses = 0, 0
            for match_id in matches:
                match_url = f'https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={API_KEY}'
                response = request(match_url)
                match_details = response.json()
                
                for participant in match_details['info']['participants']:
                    if participant['puuid'] == puuid:
                        if participant['win']:
                            wins += 1
                        else:
                            losses += 1
                        break
            
            # Ajouter les données au dictionnaire
            rank_data['recent_wins'] = wins
            rank_data['recent_losses'] = losses
            data[f"{game_name}#{tag_line}"] = rank_data

        except Exception as e:
            print(f"Erreur pour le joueur {game_name}#{tag_line}: {str(e)}")
            data[f"{game_name}#{tag_line}"] = None

    # Créer le DataFrame
    df = pd.DataFrame(data).transpose()

    return df

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


    chall_response = requests.get(root + chall + '?api_key=' + API_KEY )
    chall_df = pd.DataFrame(chall_response.json()['entries']).sort_values('leaguePoints', ascending=False).reset_index(drop=True)
    gm_df= pd.DataFrame()
    masters_df = pd.DataFrame()
    if (top > 300): 
        gm_response = requests.get(root + gm + '?api_key=' + API_KEY )
        gm_df = pd.DataFrame(gm_response.json()['entries']).sort_values('leaguePoints', ascending=False).reset_index(drop=True)
    if (top > 1000):
        masters_response = requests.get(root + masters + '?api_key=' + API_KEY )
        masters_df = pd.DataFrame(masters_response.json()['entries']).sort_values('leaguePoints', ascending=False).reset_index(drop=True)
    
    ladder = pd.concat([chall_df, gm_df, masters_df])[:top].reset_index(drop=True)
    ladder = ladder.drop(columns='rank').reset_index(drop=False).rename(columns={'index':'rank'})
    
    ladder['rank'] += 1
    
    return ladder

def get_match_history(puuid=None, start=0, count=20):
    root = 'https://europe.api.riotgames.com/'
    endpoint = f'lol/match/v5/matches/by-puuid/{puuid}/ids?type=tourney&start={start}&count={count}'

    response = requests.get(root + endpoint + '&api_key=' + API_KEY)
    
    return response.json()


def get_match_data_from_id(matchId=None):
    root = 'https://europe.api.riotgames.com/'
    endpoint = f'lol/match/v5/matches/{matchId}'

    response = requests.get(root + endpoint + '?api_key=' + API_KEY)
    
    return response.json()

def get_match_data_from_id_at15(matchId=None):
    root = 'https://europe.api.riotgames.com/'
    endpoint = f'lol/match/v5/matches/{matchId}/timeline'

    response = requests.get(root + endpoint + '?api_key=' + API_KEY)
    
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



# def get_last_week_time():
#     end_time = datetime.datetime.now()
#     start_time = end_time - datetime.timedelta(days=7)
#     return start_time.timestamp(), end_time.timestamp()

# def get_match_history_last_week(puuid=None, startTime=get_last_week_time()[0], endTime=datetime.datetime.now().timestamp(), start=0, count=20):
    
#     startTime = int(startTime)
#     endTime = int(endTime)
    
#     root = 'https://europe.api.riotgames.com/'
#     endpoint = f'lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={startTime}&endTime={endTime}&queue=420&start=0&count=100'
    


#     response = requests.get(root + endpoint + '&api_key=' + API_KEY)
    
#     return response.json()

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




# Répertoire contenant les icônes des champions
champ_icons = 'champ_icons'
item_icons = 'item_icons'

# Fonction principale
def main():
    st.title("Suivi des Performances")
    menu = ["Suivi Scrim", "Suivi SoloQ", "Stats", "Winrates"]
    choice = st.sidebar.selectbox("Choisissez une catégorie", menu)

    if choice == "Suivi Scrim":
        handle_scrim()
    elif choice == "Suivi SoloQ":
        handle_soloq()
    elif choice == "Stats":
        handle_stats()
    elif choice == "Winrates":
        handle_winrates()

# Fonction pour gérer la catégorie Scrim
import streamlit as st
import pandas as pd
import json
import os
import plotly.graph_objects as go  # Pour le graphique

def handle_scrim():
    st.subheader("Suivi des Scrims")
    scrim_path = 'json_matchs'

    if not os.path.exists(scrim_path):
        st.warning("Aucun scrim trouvé. Veuillez ajouter des fichiers JSON dans le dossier 'json_matchs'.")
        return

    scrim_files = [f for f in os.listdir(scrim_path) if f.endswith('.json')]
    if not scrim_files:
        st.warning("Aucun fichier de scrim disponible.")
        return

    for scrim_file in scrim_files:
        if st.button(f"Afficher le Scrim : {scrim_file}"):
            with open(os.path.join(scrim_path, scrim_file), 'r') as f:
                data = json.load(f)
        
            # ---------------------------------------
            # Infos générales : patch, durée
            # ---------------------------------------
            patch = data['gameVersion'].split('.')[0] + '.' + data['gameVersion'].split('.')[1]
            
            game_duration_ms = data["gameDuration"]
            game_duration_seconds = game_duration_ms // 1000
            minutes = game_duration_seconds // 60
            seconds = game_duration_seconds % 60

            st.write(f"**Patch** : {patch}")
            st.write(f"**Durée** : {minutes}:{seconds:02d}")

            # ---------------------------------------
            # Extraction des données par participant
            # ---------------------------------------
            participants_data = []
            for participant in data['participants']:
                pseudo   = participant.get('NAME', '')
                champion = participant.get('SKIN', '')
                kills    = int(participant.get('CHAMPIONS_KILLED', 0))
                deaths   = int(participant.get('NUM_DEATHS', 0))
                assists  = int(participant.get('ASSISTS', 0))
                cs       = participant.get('Missions_CreepScore', '0')
                items    = [participant.get(f"ITEM{i}", "") for i in range(7)]

                gold_earned   = int(participant.get("GOLD_EARNED", 0))
                damage_dealt  = int(participant.get("TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", 0))
                turret_kills  = int(participant.get("TURRET_TAKEDOWNS", 0))
                drakes        = int(participant.get("DRAGON_KILLS", 0))
                heralds       = int(participant.get("RIFT_HERALD_KILLS", 0))
                barons        = int(participant.get("BARON_KILLS", 0))
                grubs         = int(participant.get("HORDE_KILLS", 0))
                vision_score  = int(participant.get("VISION_SCORE", 0))
                win_str       = participant.get("WIN", "Fail")   # "Win" ou "Fail"

                participants_data.append({
                    "Joueur": pseudo,
                    "Champion": f'<img src="https://ddragon.leagueoflegends.com/cdn/14.5.1/img/champion/{champion}.png" style="height: 50px;">',
                    "K": kills,
                    "D": deaths,
                    "A": assists,
                    "K/D/A": f"{kills}/{deaths}/{assists}",
                    "CS": cs,
                    "Items": " ".join(
                        f'<img src="https://ddragon.leagueoflegends.com/cdn/14.5.1/img/item/{item}.png" style="height: 30px;">'
                        for item in items if item
                    ),
                    "Team": participant.get("TEAM", ""),            # "100" (Blue) ou "200" (Red)
                    "Role": participant.get("TEAM_POSITION", ""),   # TOP/JUNGLE/MIDDLE/BOTTOM/UTILITY
                    "Gold": gold_earned,
                    "Damage": damage_dealt,
                    "TurretKills": turret_kills,
                    "Drakes": drakes,
                    "Heralds": heralds,
                    "Barons": barons,
                    "Grubs": grubs,
                    "VisionScore": vision_score,
                    "WinStr": win_str
                })

            df = pd.DataFrame(participants_data)

            # ---------------------------------------
            # Séparer data Blue / Red
            # ---------------------------------------
            blue_side = df[df["Team"] == "100"]
            red_side  = df[df["Team"] == "200"]

            # ---------------------------------------
            # DataFrames stats globales
            # ---------------------------------------
            def build_team_stats(team_df):
                """
                Calcule un résumé global (tour, drakes, gold, etc.) pour l'équipe.
                """
                turrets = team_df["TurretKills"].sum()
                grubs   = team_df["Grubs"].sum()
                drakes  = team_df["Drakes"].sum()
                heralds = team_df["Heralds"].sum()
                barons  = team_df["Barons"].sum()

                total_gold   = team_df["Gold"].sum()
                total_vision = team_df["VisionScore"].sum()

                total_kills  = team_df["K"].sum()
                total_deaths = team_df["D"].sum()
                if total_deaths == 0:
                    kd_str = f"{total_kills}/0"
                else:
                    kd_str = f"{total_kills}/{total_deaths}"

                # Victoire / Défaite
                team_win = team_df["WinStr"].unique()  # ex: array(["Win"]) ou array(["Fail"])
                if "Win" in team_win:
                    result = "Win"
                else:
                    result = "Fail"

                return pd.DataFrame([{
                    "Tourelles prises": turrets,
                    "Grubs": grubs,
                    "Drakes": drakes,
                    "Heralds": heralds,
                    "Nashors": barons,
                    "Gold total": total_gold,
                    "Victoire ?": result,
                    "Vision score cumulé": total_vision,
                    "K/D total": kd_str
                }])

            # Construction
            df_blue_stats = build_team_stats(blue_side)
            df_red_stats  = build_team_stats(red_side)

            # Affichage côte à côte
            st.markdown("### Statistiques globales par équipe")
            col_team1, col_team2 = st.columns(2)
            with col_team1:
                st.markdown("**Blue Side**")
                st.dataframe(df_blue_stats, hide_index=True)

            with col_team2:
                st.markdown("**Red Side**")
                st.dataframe(df_red_stats, hide_index=True)



            # ---------------------------------------
            # Détails par joueur 
            # ---------------------------------------
            st.markdown("### Détails par joueur")

            # Selon vos JSON, vérifiez si la 1ère moitié = Blue side, 2nde = Red side
            # Sinon, fiez-vous plutôt à la colonne Team == "100" / "200"
            df_team1 = df.iloc[:5]
            df_team2 = df.iloc[5:]

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Blue Side  ")
                st.write(
                    df_team1.drop(columns=[
                        "Team","Role","Gold","Damage","TurretKills","Drakes",
                        "Heralds","Barons","Grubs","VisionScore","WinStr"
                    ]).to_html(escape=False, index=False),
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown("#### Red Side ")
                st.write(
                    df_team2.drop(columns=[
                        "Team","Role","Gold","Damage","TurretKills","Drakes",
                        "Heralds","Barons","Grubs","VisionScore","WinStr"
                    ]).to_html(escape=False, index=False),
                    unsafe_allow_html=True
                )
                
            # ---------------------------------------
            # Répartition des golds par rôle
            # ---------------------------------------
            st.markdown("### Répartition des golds par rôle")

            def compute_gold_distribution(team_df):
                """
                Retourne un DataFrame avec la somme de gold par rôle, et % par rapport au total.
                """
                roles_order = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
                total_gold  = team_df["Gold"].sum()
                distribution = []

                for role in roles_order:
                    role_gold = team_df.loc[team_df["Role"] == role, "Gold"].sum()
                    pct = (role_gold / total_gold * 100) if total_gold > 0 else 0
                    distribution.append({
                        "Rôle": role,
                        "Gold": role_gold,
                        "Pourcentage (%)": f"{pct:.2f}"
                    })
                return pd.DataFrame(distribution)

            df_blue_gold = compute_gold_distribution(blue_side)
            df_red_gold  = compute_gold_distribution(red_side)

            col_gold_1, col_gold_2 = st.columns(2)
            with col_gold_1:
                st.markdown("**Blue Side**")
                st.dataframe(df_blue_gold)

            with col_gold_2:
                st.markdown("**Red Side**")
                st.dataframe(df_red_gold)

            # ---------------------------------------
            # Graphique : Degats par role 
            # ---------------------------------------
            st.markdown("### Comparaison des dégâts par rôle (Blue vs Red)")
            roles_order = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]

            blue_damage = [blue_side.loc[blue_side["Role"] == r, "Damage"].sum() for r in roles_order]
            red_damage  = [red_side.loc[red_side["Role"] == r, "Damage"].sum()  for r in roles_order]

            fig = go.Figure(data=[
                go.Bar(name='Blue side', x=roles_order, y=blue_damage, marker_color='blue'),
                go.Bar(name='Red side',  x=roles_order, y=red_damage,  marker_color='red')
            ])
            fig.update_layout(
                barmode='group',
                title='Dégâts infligés par rôle (Blue vs Red)',
                xaxis_title='Rôle',
                yaxis_title='Dégâts totaux'
            )
            st.plotly_chart(fig)

            # ---------------------------------------
            # Bouton retour
            # ---------------------------------------
            if st.button("Retour au menu"):
                st.experimental_rerun()


# Fonction pour gérer la catégorie SoloQ
def handle_soloq():
    st.subheader("Suivi des SoloQ")
    
    display_soloq_profile()

# Fonction pour afficher le profil SoloQ
def display_soloq_profile():
    df1 = generer_leaderboard()
    
    st.dataframe(df1)

def display_item_icon(item_id, inline=False):
    """Displays item icon with smaller size."""
    icon_path = os.path.join(item_icons, f"{item_id}.png")
    if os.path.exists(icon_path):
        st.image(icon_path, width=30 if inline else 50)  # Smaller size for inline
    else:
        st.write("?")


#suivi_scrim/json_matchs
def handle_stats():
    st.subheader("Pick History Scrims")

    # Chemin vers le dossier contenant les fichiers JSON
    scrim_path = 'json_matchs'  # Remplacez par le chemin de votre dossier JSON

    # Vérifiez si le dossier existe
    if not os.path.exists(scrim_path):
        st.warning("Aucun dossier trouvé pour les fichiers JSON.")
        return

    # Récupérez tous les fichiers JSON du dossier
    scrim_files = [f for f in os.listdir(scrim_path) if f.endswith('.json')]

    # Liste des joueurs spécifiés avec leurs rôles
    specified_players = [
        ("Axo Bad Boy", "Jungle"),
        ("MaxouTigrou", "Top"),
        ("JMGG Druust", "Bottom"),
        ("hqShadow02", "Middle"),
        ("Updated Robot", "Utility"),
    ]

    # Dictionnaires pour stocker les champions joués et les résultats
    player_champions = {player: [] for player, role in specified_players}

    # Parcourez tous les fichiers JSON
    for scrim_file in scrim_files:
        file_path = os.path.join(scrim_path, scrim_file)
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Récupérez les champions joués et les résultats (victoire/défaite)
        for participant in data["participants"]:
            player_name = participant["NAME"]
            if player_name in player_champions:
                player_champions[player_name].append({
                    "Champion": participant["SKIN"],
                    "Win": 1 if participant["WIN"] == "Win" else 0
                })

    # Comptez les occurrences de chaque champion par joueur et calculez le Win Rate
    player_champions_stats = {}
    for player, champions in player_champions.items():
        if champions:
            df = pd.DataFrame(champions)
            # Compter les occurrences et calculer le Win Rate
            champion_stats = (
                df.groupby("Champion")
                .agg(
                    Games=("Champion", "count"),
                    Wins=("Win", "sum")
                )
                .reset_index()
            )
            champion_stats["Win Rate"] = (champion_stats["Wins"] / champion_stats["Games"] * 100).round(1)
            # Ajouter les URLs des icônes des champions
            champion_stats["Icon"] = "https://ddragon.leagueoflegends.com/cdn/14.5.1/img/champion/" + champion_stats["Champion"] + ".png"
            champion_stats = champion_stats[["Icon", "Games", "Win Rate"]]
            player_champions_stats[player] = champion_stats

    # Ajuster les largeurs des colonnes pour occuper toute la page
    col_tab1, col_tab2, col_tab3, col_tab4, col_tab5 = st.columns([1, 1, 1, 1, 1])

    # Parcourez chaque joueur et affichez leurs champions dans les colonnes correspondantes
    for (player, role), col in zip(specified_players, [col_tab1, col_tab2, col_tab3, col_tab4, col_tab5]):
        with col:
            # Afficher le rôle et le nom du joueur
            st.markdown(f"<h3 style='text-align: center;'>{player}</h3>", unsafe_allow_html=True)
            
            # Afficher les champions joués avec leur Win Rate
            if player in player_champions_stats:
                champion_data = player_champions_stats[player]
                # Transformer en HTML pour afficher les images et ajouter le Win Rate
                champion_data_html = champion_data.to_html(
                    escape=False,
                    formatters={
                        "Icon": lambda x: f'<img src="{x}" style="height: 50px;">',
                    },
                    index=False,
                )
                st.write(champion_data_html, unsafe_allow_html=True)
            else:
                st.write("Aucun champion joué")



def handle_winrates():
    st.subheader("Calcul du Winrate Scrim")
    
    # Liste des membres de l'équipe
    team_members = ["MaxouTigrou", "Axo Bad Boy", "hqShadow02", "JMGG Druust", "Updated Robot"]
    
    # Chemin vers les fichiers JSON des matchs
    scrim_path = 'json_matchs'
    
    # Vérifier si le dossier existe
    if not os.path.exists(scrim_path):
        st.warning("Aucun dossier trouvé pour les fichiers JSON.")
        return
    
    # Récupérer tous les fichiers JSON du dossier
    scrim_files = [f for f in os.listdir(scrim_path) if f.endswith('.json')]
    
    if not scrim_files:
        st.warning("Aucun fichier de match trouvé.")
        return
    
    # Initialiser les compteurs pour l'équipe
    total_games = 0
    total_wins = 0
    
    # Initialiser les statistiques pour toutes les valeurs possibles de 0 à 6
    horde_stats = {i: {"Games": 0, "Wins": 0} for i in range(0, 7)}
    
    for scrim_file in scrim_files:
        file_path = os.path.join(scrim_path, scrim_file)
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Vérifier si tous les membres de l'équipe sont présents dans la partie
        team_horde_kills = 0
        team_result = []
        
        for participant in data["participants"]:
            if participant["NAME"] in team_members:  # Filtrer uniquement les joueurs spécifiés
                team_result.append(participant["WIN"] == "Win")
                team_horde_kills += int(participant["HORDE_KILLS"])  # Ajouter les Horde Kills au total de l'équipe
        
        # Si tous les membres de l'équipe sont présents
        if len(team_result) == len(team_members):
            total_games += 1
            if all(team_result):  # Si tous les joueurs de l'équipe ont gagné
                total_wins += 1
            
            # Mettre à jour les statistiques pour cette somme
            if team_horde_kills in horde_stats:
                horde_stats[team_horde_kills]["Games"] += 1
                if all(team_result):  # Si l'équipe entière a gagné
                    horde_stats[team_horde_kills]["Wins"] += 1
    
    # Calculer le winrate par somme de Horde Kills
    for horde_kills_sum in horde_stats:
        games = horde_stats[horde_kills_sum]["Games"]
        wins = horde_stats[horde_kills_sum]["Wins"]
        horde_stats[horde_kills_sum]["Winrate (%)"] = round((wins / games) * 100, 2) if games > 0 else 0.0
    
    # Convertir les statistiques en DataFrame
    df_horde_winrates = pd.DataFrame.from_dict(horde_stats, orient="index")
    df_horde_winrates.reset_index(inplace=True)
    df_horde_winrates.rename(columns={"index": "Grubs", "Games": "Total Games", "Wins": "Total Wins"}, inplace=True)
    
    # Calculer le winrate global de l'équipe
    winrate = round((total_wins / total_games) * 100, 2) if total_games > 0 else 0.0
    
    # Afficher les résultats globaux
    st.metric("Total de parties", total_games)
    st.metric("Total de victoires", total_wins)
    st.metric("Winrate (%)", f"{winrate}%")
    
    # Afficher le tableau des Winrates par Somme des Horde Kills
    st.write("### Tableau des Winrates/Grubs")
    st.dataframe(df_horde_winrates, hide_index=True)












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
