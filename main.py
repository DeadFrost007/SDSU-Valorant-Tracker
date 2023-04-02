import requests
from bs4 import BeautifulSoup
import pandas as pd

urls = [
    'https://tracker.gg/valorant/profile/riot/SDSU%20DeadFrost%23Simp/overview',
    'https://tracker.gg/valorant/profile/riot/SDSU%20azure%23jacks/overview?playlist=competitive',
    'https://tracker.gg/valorant/profile/riot/SDSU%20MiniMan%23mini/overview',
    'https://tracker.gg/valorant/profile/riot/SDSU%20Beans%23SDSU/overview',
    'https://tracker.gg/valorant/profile/riot/SDSU%20Endemmic%236568/overview'
]

# Define the columns for the DataFrame
columns = ['Player', 'Rank', 'Damage/Round', 'K/D Ratio', 'Headshot%', 'Win%']

# Create an empty DataFrame with the columns
df = pd.DataFrame(columns=columns)

for url in urls:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Use dictionary comprehension to map the stat titles to the corresponding elements
    stat_elems = {elem['title']: elem.find_next_sibling('span').text.strip() for elem in soup.find_all('span', {'title': True})}

    # Extract the username from the URL and replace any "%20" with a space
    username = url.split('/')[-2].replace('%20', ' ')

    # Find the element containing the rank and extract the text
    rank_elem = soup.find('div', {'class': 'label'}, string='Rating')
    rank = rank_elem.find_next_sibling('div', {'class': 'value'}).text.strip() if rank_elem else 'N/A'

    # Use list comprehension to get the stats in the order defined by the columns
    stats = [username, rank, stat_elems.get('Damage/Round', 'N/A'), stat_elems.get('K/D Ratio', 'N/A'), stat_elems.get('Headshot%', 'N/A'), stat_elems.get('Win %', 'N/A')]

    # Concatenate the stats for the player to the DataFrame
    df = pd.concat([df, pd.Series(stats, index=columns)], ignore_index=True)

    print(f"Stats for {username}:")
    for stat in zip(columns[1:], stats[1:]):
        print(f"{stat[0]}: {stat[1]}")
    print()  # Print an empty line for readability

# Export the DataFrame to an Excel file
df.to_excel('valstats.xlsx', index=False)
