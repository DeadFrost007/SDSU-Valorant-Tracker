import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import unquote
import pandas as pd

urls = [
    'https://tracker.gg/valorant/profile/riot/SDSU%20DeadFrost%23Simp/overview',
    'https://tracker.gg/valorant/profile/riot/SDSU%20azure%23jacks/overview?playlist=competitive',
    'https://tracker.gg/valorant/profile/riot/SDSU%20MiniMan%23mini/overview',
    'https://tracker.gg/valorant/profile/riot/SDSU%20Beans%23SDSU/overview',
    'https://tracker.gg/valorant/profile/riot/SDSU%20Endemmic%236568/overview'
]

# Define the columns for the DataFrame
columns = ['Player', 'Damage/Round', 'K/D Ratio', 'Headshot%', 'Win%']

# Create an empty DataFrame with the columns
df = pd.DataFrame(columns=columns)

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the element containing the "Damage/Round" stat
    damage_per_round_elem = soup.find('span', {'title': 'Damage/Round'})
    if damage_per_round_elem:
        damage_per_round = damage_per_round_elem.find_next_sibling('span').text.strip()
    else:
        damage_per_round = "N/A"

    # Find the element containing the "K/D Ratio" stat
    kd_ratio_elem = soup.find('span', {'title': 'K/D Ratio'})
    if kd_ratio_elem:
        kd_ratio = kd_ratio_elem.find_next_sibling('span').text.strip()
    else:
        kd_ratio = "N/A"

    # Find the element containing the "Headshot%" stat
    headshot_percentage_elem = soup.find('span', {'title': 'Headshot%'})
    if headshot_percentage_elem:
        headshot_percentage = headshot_percentage_elem.find_next_sibling('span').text.strip()
    else:
        headshot_percentage = "N/A"

    # Find the element containing the "Win %" stat
    win_percentage_elem = soup.find('span', {'title': 'Win %'})
    if win_percentage_elem:
        win_percentage = win_percentage_elem.find_next_sibling('span').text.strip()
    else:
        win_percentage = "N/A"

    # Extract the username from the URL and replace any "%20" with a space
    username = unquote(url.split('/')[-2]).replace('%20', ' ')

    # Add the stats for the player to the DataFrame
    df = pd.concat([df, pd.DataFrame({
        'Player': username,
        'Damage/Round': damage_per_round,
        'K/D Ratio': kd_ratio,
        'Headshot%': headshot_percentage,
        'Win%': win_percentage
    }, index=[0])], ignore_index=True)

    print(f"Stats for {username}:")
    print(f"Damage/Round: {damage_per_round}")
    print(f"K/D Ratio: {kd_ratio}")
    print(f"Headshot%: {headshot_percentage}")
    print(f"Win%: {win_percentage}")
    print()  # Print an empty line for readability

# Export the DataFrame to an Excel file
df.to_excel('valstats.xlsx', index=False)

