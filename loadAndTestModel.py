from sklearn import datasets
from sklearn.utils import resample
import torch
import torch.nn as nn
import pandas as pd
import pymongo
from torch.utils.data import Dataset, DataLoader
import numpy as np

class BinaryClassification(nn.Module):
    def __init__(self):
        super(BinaryClassification, self).__init__()
        # Number of input features is 12.
        self.layer_1 = nn.Linear(4, 64) 
        self.layer_2 = nn.Linear(64, 64)
        self.layer_out = nn.Linear(64, 1) 
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.1)
        self.batchnorm1 = nn.BatchNorm1d(64)
        self.batchnorm2 = nn.BatchNorm1d(64)
        
    def forward(self, inputs):
        x = self.relu(self.layer_1(inputs))
        x = self.batchnorm1(x)
        x = self.relu(self.layer_2(x))
        x = self.batchnorm2(x)
        x = self.dropout(x)
        x = self.layer_out(x)
        
        return x

class TestData(Dataset):
    def __init__(self, X_data):
        self.X_data = X_data
        
    def __getitem__(self, index):
        return self.X_data[index]
        
    def __len__ (self):
        return len(self.X_data)
        
def readFile():
    champs = {}
    i = 0
    with open('lolChamps.txt') as f:
        for line in f.readlines():
            champs[line.strip()] = i
            i += 1
    return champs

def preprocess(champs):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    rift = client.LeagueData.newChallenger

    totalMatches = 0
    """
    normal gold difference
    first blood
    first herald/first dragon
    first tower
    first baron
    """
    gd15 = []
    firstBlood = []
    firstHerald = []
    firstDragon = []
    firstTower = []
    firstBaron = []

    winCol = []
    for match in rift.find({}):
        totalMatches += 1
        win1 = True if match['info']['teams'][0]['win'] == True else False
        win2 = not win1
        #updated gd15
        match15 = match['timeline']['info']['frames']

        # Gold Difference @ 15
        if len(match15) > 15:
            frames = match15[15]['participantFrames']
            team1Gold = 0;
            team2Gold = 0;
            for i in range(1, 6):
                team1Gold += frames[str(i)]['totalGold'];
            for i in range(6, 11):
                team2Gold += frames[str(i)]['totalGold'];
        gd15.append(team1Gold-team2Gold)
        gd15.append(team2Gold-team1Gold)

        # stores the current first boolean variable
        currentFirst = match['info']['teams'][0]['objectives']['champion']['first'] 
        # First Blood
        firstBlood.append(1 if currentFirst else 0) 
        firstBlood.append(1 if not currentFirst else 0) 

        # First Herald
        currentFirst = match['info']['teams'][0]['objectives']['riftHerald']['first']        
        firstHerald.append(1 if currentFirst else 0) 
        firstHerald.append(1 if not currentFirst else 0) 

        # First Dragon
        currentFirst = match['info']['teams'][0]['objectives']['dragon']['first']         
        firstDragon.append(1 if currentFirst else 0) 
        firstDragon.append(1 if not currentFirst else 0) 

        # First Tower
        currentFirst = match['info']['teams'][0]['objectives']['tower']['first']          
        firstTower.append(1 if currentFirst else 0) 
        firstTower.append(1 if not currentFirst else 0) 

        # First Baron
        currentFirst = match['info']['teams'][0]['objectives']['baron']['first']        
        firstBaron.append(1 if currentFirst else 0) 
        firstBaron.append(1 if not currentFirst else 0) 

        # Won or not
        winCol.append(1 if win1 else 0)
        winCol.append(1 if win2 else 0)
    return pd.DataFrame(data={'gd': gd15, 'fb': firstBlood, 'fd': firstDragon, 'fh': firstHerald,
            'ft': firstTower, 'fba': firstBaron, 'win': winCol})

def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    y_pred_list = []
    print("Input test data.")
    goldDifference = [input("Gold Difference @ 15 minutes (can be positive or negative)")]
    # firstBlood = [input("First Blood (0 or 1): ")]
    firstDragon = [input("First Dragon (0 or 1): ")]
    # firstHerald = [input("First Herald (0 or 1): ")]
    # firstTower = [input("First Tower (0 or 1): ")]
    firstBaron = [input("First Baron (0 or 1): ")]
    gameDuration = [input("Total Game Duration: ")]
    X = pd.DataFrame(data={'gd': goldDifference, 'fd': firstDragon, 'fba': firstBaron, 'dur': gameDuration})
    print(X)
    test_data = TestData(torch.from_numpy(np.array(X).astype(np.float32)))
    test_loader = DataLoader(dataset=test_data, batch_size=1)
    model = BinaryClassification()
    model.eval()
    model.load_state_dict(torch.load("newModel.pt"))
    test_loader = DataLoader(dataset=test_data, batch_size=1)
    with torch.no_grad():
        for X_batch in test_loader:
            X_batch = X_batch.to(device)
            y_test_pred = model(X_batch)
            y_test_pred = torch.sigmoid(y_test_pred)
            y_pred_tag = torch.round(y_test_pred)
            y_pred_list.append(y_pred_tag.cpu().numpy())
    y_pred_list = [a.squeeze().tolist() for a in y_pred_list]
    print(y_pred_list)

if __name__ == "__main__":
    main()