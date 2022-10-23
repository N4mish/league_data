from urllib import response
import requests, pymongo

def requestSummonerData(region, summonerName, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()

def requestSummonerDataByID(region, summonerID, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/" + summonerID + "?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()

def getMatchHistory(region, puuid, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids" + "?api_key=" + APIKey + "&count=100&start=100"
    return requests.get(URL).json()
    
def getMatch(region, matchID, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/" + matchID + "?api_key=" + APIKey
    return requests.get(URL).json()

def getChallengerQueue(region, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5?api_key=" + APIKey
    return requests.get(URL).json()

def getMatchTimeline(region, matchID, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/" + matchID + "/timeline" + "?api_key=" + APIKey
    return requests.get(URL).json()

def main():
    print("Regions: 'BR1 EUN1 EUW1 JP1 KR LA1 LA2 NA1 OC1 RU TR1'\n")
    # region = input('Enter Region: ')
    # summonerName = input('Enter Summoner Name: ')
    # APIKey = input('Enter your API Key: ')
    region = "NA1"
    summonerName = "0so Bear"
    APIKey = "RGAPI-8a56ee88-8b41-4389-b1d0-1cb15de55949"
    responseJSON = requestSummonerData(region, summonerName, APIKey)
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # databases
    # aram = client.LeagueData.ARAM
    # ranked = client.LeagueData.Ranked
    rift = client.LeagueData.SummonersRift
    # challenger = client.LeagueData.challenger


    # print("\nId: ", responseJSON['id'])
    # print("Account Id: ", responseJSON['accountId'])
    # print("PUUID: ", responseJSON['puuid'])
    # print("Profile Icon Id: ", responseJSON['profileIconId'])
    # print("Revision Date: ", responseJSON['revisionDate'])
    # print("Name: ", responseJSON['name'])
    # print("Summoner Level : ", responseJSON['summonerLevel'])

    cq = getChallengerQueue(region, APIKey)
    count = 0

    #get non duplicate challenger games
    entries = cq['entries']
    currentProgress = 20
    # for i in range(0, currentProgress):
    #     entries.pop(i)

    # for player in entries:
    #     summonerName = player['summonerId']
    #     responseJSON = requestSummonerDataByID(region, summonerName, APIKey)
    #     matchHistory = getMatchHistory("AMERICAS", responseJSON['puuid'], APIKey)
    #     print(len(matchHistory))
    #     for i in range(0, 99):
    #         print(f"{i} {matchHistory[i]}")
    #         match = getMatch("AMERICAS", matchHistory[i], APIKey)
    #         cursor = challenger.find({ "_id" : matchHistory[i]})
    #         point = next(cursor, None)
    #         print(point)
    #         print(match['info']['queueId'])
    #         if match['info']['queueId'] == 420 and point == None:
    #             print("inserting")
    #             challenger.insert_one({"_id": matchHistory[i], "metadata": match['metadata'], "info": match['info']})
    #             count += 1

    #summonerName = player['summonerId']
    responseJSON = requestSummonerData(region, summonerName, APIKey)
    print(responseJSON)
    matchHistory = getMatchHistory("AMERICAS", responseJSON['puuid'], APIKey)
    print(len(matchHistory))
    progress = 0
    for i in range(progress, 99):
        print(f"{i} {matchHistory[i]}")
        match = getMatch("AMERICAS", matchHistory[i], APIKey)
        cursor = rift.find({ "_id" : matchHistory[i]})
        point = next(cursor, None)
        print(point)
        print(match['info']['queueId'])
        if (match['info']['queueId'] == 420 or match['info']['queueId'] == 400) and point == None:
            print("inserting")
            timeline = getMatchTimeline("AMERICAS", matchHistory[i], APIKey)
            if not len(timeline) == 1:
                rift.insert_one({"_id": matchHistory[i], "metadata": match['metadata'], "info": match['info'], "timeline": timeline})
                count += 1
    print(count)




if __name__ == "__main__":
    main()