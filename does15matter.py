import pymongo

counter = 0;
totalMatches = 0;
client = pymongo.MongoClient("mongodb://localhost:27017/")
rift = client.LeagueData.SummonersRift
team = 0
bigdcounter = 0
for match in rift.find({}):
    totalMatches += 1
    win1 = True if match['info']['teams'][0]['win'] == True else False
    win2 = not win1
    if len(match['timeline']['info']['frames']) >= 15:
        frames = match['timeline']['info']['frames'][15]['participantFrames']
        team1Gold = 0;
        team2Gold = 0;
        for i in range(1, 6):
            team1Gold += frames[str(i)]['totalGold'];
        for i in range(6, 11):
            team2Gold += frames[str(i)]['totalGold'];
        diff = team1Gold - team2Gold
        if (diff > 0 and win1) or (diff < 0 and win2):
            counter += 1
    
print(f"Games are won {round((counter/totalMatches), 2) * 100} % of the time with a gold lead @ 15.")
    
# winrates = {}
# champions = dict(sorted(champions.items(), key=lambda item: item[1], reverse = True)) #sort by games played
# for champ in champions: 
#     winrates[champ] = champions[champ][0]/champions[champ][1]

# print(winrates)
#winrates = dict(sorted(winrates.items(), key=lambda item: item[1], reverse=True)) #sort by winrate

# for champ in winrates: 
#     print(f"{champ}: {round(winrates[champ]*100, 2)}% in {champions[champ][1]} games")

# print(f"BIG D = {bigdcounter} ")