import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def read_player_names(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def write_player_names(filename, player_list):
    with open(filename, 'w') as file:
        for player in player_list:
            file.write(player + '\n')

def get_stats_url(username, playlist='competitive'):
    playlist_suffix = '' if playlist == 'competitive' else f'?playlist={playlist}'
    return f'https://tracker.gg/valorant/profile/riot/{username}/overview{playlist_suffix}'

def add_remove_player(player_list, action):
    while True:
        player = input(f"Enter the player you want to {action} (or type 'done' to finish): ")
        if player.lower() == 'done':
            break
        player = player.replace(' ', '%20').replace('#', '%23')
        if action == 'add':
            if player not in player_list:
                player_list.append(player)
                print(f"{player} has been added to the list.")
            else:
                print(f"{player} is already in the list.")
        elif action == 'remove':
            if player in player_list:
                player_list.remove(player)
                print(f"{player} has been removed from the list.")
            else:
                print(f"{player} is not in the list.")
        elif action == 'clear':
            player_list.clear()
            print("Player list has been cleared.")
            break  # Exit the loop after clearing the list
    write_player_names(player_filename, player_list)

def get_choice(options):
    while True:
        choice = input("Choice: ")
        if choice in options:
            return choice
        print(f"Invalid choice. Please enter one of {options}.")

def get_stat(soup, class_name, title=None):
    elem = soup.find('span', {'class': class_name, 'title': title}) if title else soup.find('div', {'class': class_name})
    return elem.find_next_sibling('span').text.strip() if elem and elem.find_next_sibling('span') else 'N/A'

def get_competitive_rank(soup):
    rank_elem = soup.find('div', {'class': 'value'})
    return ' '.join([str(x).strip() for x in rank_elem.contents]).replace('[', '').replace(']', '') if rank_elem else 'N/A'

def get_premier_rank(soup):
    premier_rank_elem = soup.find('div', {'class': 'flex flex-row font-medium gap-1 items-center text-12 text-disabled'})
    if premier_rank_elem:
        img_elem = premier_rank_elem.find('img')
        region = img_elem['src'].split('/')[-1].split('_')[1].replace('.png', '').replace('_', ' ')
        rank_text = premier_rank_elem.get_text(strip=True)
        return f"{region} : {rank_text}"
    return 'N/A'

player_filename = 'player_names.txt'
urls = read_player_names(player_filename)
columns = ['Player', 'Rank', 'Damage/Round', 'K/D Ratio', 'Headshot%', 'Win%', 'Tracker Score']
df = pd.DataFrame(columns=columns)

while True:
    print("Enter the number corresponding to the action you want:")
    print("1. Competitive Stats\n2. Premier Stats\n3. Add/Remove Players\n4. Quit")
    choice = get_choice(['1', '2', '3', '4'])
    if choice == '3':
        while True:
            print("Enter the number corresponding to the action you want to perform:")
            print("1. Add a Player\n2. Remove a Player\n3. Clear List\n4. Continue")
            player_choice = get_choice(['1', '2', '3', '4'])
            if player_choice == '3':
                add_remove_player(urls, 'clear')
            elif player_choice in ['1', '2']:
                add_remove_player(urls, 'add' if player_choice == '1' else 'remove')
            else:
                break
    elif choice == '4':
        break
    else:
        break

for username in urls:
    # Generate the URL based on the user's choice
    url = get_stats_url(username, 'competitive' if choice == '1' else 'premier')
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract the Tracker Score
    tracker_score_elem = soup.find('div', {'class': 'label'}, string='Tracker Score')
    tracker_score = tracker_score_elem.find_next_sibling('div', {'class': 'value'}).text.strip() if tracker_score_elem else 'N/A'
    
    # Choose the appropriate function based on the choice
    get_rank_function = get_competitive_rank if choice == '1' else get_premier_rank
    rank = get_rank_function(soup)
    
    username_display = username.replace('%20', ' ').replace('%23', '#')
    stats = [username_display, rank, get_stat(soup, 'name', 'Damage/Round'), get_stat(soup, 'name', 'K/D Ratio'), get_stat(soup, 'name', 'Headshot %'), get_stat(soup, 'name', 'Win %'), tracker_score]
    df = pd.concat([df, pd.Series(stats, index=columns)], ignore_index=True)
    
    print(f"\nStats for {username_display} ({'Competitive' if choice == '1' else 'Premier'}):")
    for stat in zip(columns[1:], stats[1:]):
        print(f"{stat[0]}: {stat[1]}")
