import requests

def requestSummonerData(region, summonerName, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summonerName + "?api_key=" + APIKey
    response = requests.get(URL)
    return response.json()

def getMatchHistory(region, puuid, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/by-puuid/" + puuid + "/ids" + "?api_key=" + APIKey
    return requests.get(URL).json()
    
def getMatch(region, matchID, APIKey):
    URL = "https://" + region + ".api.riotgames.com/lol/match/v5/matches/" + matchID + "?api_key=" + APIKey
    return requests.get(URL).json()

def main():
    print("Regions: 'BR1 EUN1 EUW1 JP1 KR LA1 LA2 NA1 OC1 RU TR1'\n")
    region = input('Enter Region: ')
    summonerName = input('Enter Summoner Name: ')
    APIKey = input('Enter your API Key: ')
    responseJSON = requestSummonerData(region, summonerName, APIKey)

    # print("\nId: ", responseJSON['id'])
    # print("Account Id: ", responseJSON['accountId'])
    print("PUUID: ", responseJSON['puuid'])
    # print("Profile Icon Id: ", responseJSON['profileIconId'])
    # print("Revision Date: ", responseJSON['revisionDate'])
    print("Name: ", responseJSON['name'])
    print("Summoner Level : ", responseJSON['summonerLevel'])

    matchHistory = getMatchHistory("AMERICAS", responseJSON['puuid'], APIKey)
    deathsMoreThanTen = 0
    matches = {}
    for i in range(0, 10):
        matches[i] = getMatch("AMERICAS", matchHistory[i], APIKey)
        

    for i in range(0, 10):
        if matches[i]["info"]["participants"][0]["deaths"] >= 5:
            deathsMoreThanTen += 1

    print("Int counter: " + str((deathsMoreThanTen/10)*100) + "%")



if __name__ == "__main__":
    main()