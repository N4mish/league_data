import pymongo

champions = {}
client = pymongo.MongoClient("mongodb://localhost:27017/")
rift = client.LeagueData.SummonersRift
team = 0
bigdcounter = 0
for match in rift.find({}):
    win1 = True if match['info']['teams'][0]['win'] == True else False
    win2 = not win1
    for i in range(0, 10):
        if i == 0:
            print("Team 1:")
            team = 0 
        elif i == 5:
            print("\nTeam 2")
            team = 1
        champ = match['info']['participants'][i]['championName']
        if champ == "Gangplank" and match['info']['participants'][i]['summonerName'] == "DankDanzo":
            bigdcounter += 1

        if not (champ in champions):
            if ((i < 5 and win1) or (i >= 5 and win2)):
                champions[champ] = [1, 1]
            else: 
                champions[champ] = [0, 1]
        else: 
            if (i < 5 and win1) or (i >= 5 and win2):
                champions[champ][0] += 1
            champions[champ][1] += 1

        print(match['info']['participants'][i]['championName'], end=' ')
    
    print("\n")

winrates = {}
champions = dict(sorted(champions.items(), key=lambda item: item[1], reverse = True)) #sort by games played
for champ in champions: 
    winrates[champ] = champions[champ][0]/champions[champ][1]

print(winrates)
#winrates = dict(sorted(winrates.items(), key=lambda item: item[1], reverse=True)) #sort by winrate

for champ in winrates: 
    print(f"{champ}: {round(winrates[champ]*100, 2)}% in {champions[champ][1]} games")

print(f"BIG D = {bigdcounter} ")