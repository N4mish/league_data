import pymongo

champions = {}
client = pymongo.MongoClient("mongodb://localhost:27017/")
rift = client.LeagueData.SummonersRift
team = 0
bigdcounter = 0
for match in rift.find({}):
    win = True if match['info']['teams'][0]['win'] == True else False
    for i in range(0, 10):
        if i == 0:
            print("Team 1:")
            team = 0 
        elif i == 5:
            print("\nTeam 2")
            team = 1
            if not win: 
                win = True
        champ = match['info']['participants'][i]['championName']
        if champ == "Gangplank" and match['info']['participants'][i]['summonerName'] == "DankDanzo":
            bigdcounter += 1

        if not (champ in champions):
            if win:
                champions[champ] = [1, 1]
            else: 
                champions[champ] = [0, 1]
        else: 
            if win:
                champions[champ][0] += 1
            champions[champ][1] += 1

        print(match['info']['participants'][i]['championName'], end=' ')
    
    print("\n")

winrates = {}
for champ in champions: 
    winrates[champ] = champions[champ][0]/champions[champ][1]

winrates = dict(sorted(winrates.items(), key=lambda item: item[1], reverse=True))

for champ in winrates: 
    print(f"{champ}: {round(winrates[champ]*100, 2)}% in {champions[champ][1]} games")

print(f"BIG D = {bigdcounter} ")