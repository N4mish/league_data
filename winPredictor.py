#importing the libraries
import pymongo
import torch
import torch.nn as nn
import torch.optim as optim

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler  
from sklearn.metrics import confusion_matrix, classification_report


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
    gameDuration = []

    winCol = []
    for match in rift.find({}):
        totalMatches += 1
        win1 = True if match['info']['teams'][0]['win'] == True else False
        win2 = not win1
        #updated gd15
        matchFrames = match['timeline']['info']['frames']

        # Gold Difference @ 15
        if len(matchFrames) > 15:
            frames = matchFrames[15]['participantFrames']
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

        # Game duration
        gameDuration.append(len(matchFrames))
        gameDuration.append(len(matchFrames))
        # Won or not
        winCol.append(1 if win1 else 0)
        winCol.append(1 if win2 else 0)
    return pd.DataFrame(data={'gd': gd15,'fd': firstDragon,'fba': firstBaron, 'dur': gameDuration, 'win': winCol})
    #return pd.DataFrame(data={'gd': gd15, 'fb': firstBlood, 'fd': firstDragon, 'fh': firstHerald,
    #     'ft': firstTower, 'fba': firstBaron, 'dur': gameDuration, 'win': winCol})

    ## test data    
class TestData(Dataset):
    
    def __init__(self, X_data):
        self.X_data = X_data
        
    def __getitem__(self, index):
        return self.X_data[index]
        
    def __len__ (self):
        return len(self.X_data)

class TrainData(Dataset):
    
    def __init__(self, X_data, y_data):
        self.X_data = X_data
        self.y_data = y_data
        
    def __getitem__(self, index):
        return self.X_data[index], self.y_data[index]
        
    def __len__ (self):
        return len(self.X_data)

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

def main():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    rift = client.LeagueData.challenger
    champs = readFile()
    df = preprocess(champs)
    print(df)
    # separate into datasets in and out
    X = df.iloc[:, 0:-1]
    y = df.iloc[:, -1]

    # setup train and test databases, 33% split
    # "For neural networks to train properly, we need to standardize the input values. 
    # We standardize features by removing the mean and scaling to unit variance."
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=69) 
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    EPOCHS = 11
    BATCH_SIZE = 64
    LEARNING_RATE = 0.001

    print(y_train.shape)
    ## train data
    train_data = TrainData(torch.from_numpy(np.array(X_train).astype(np.float32)), torch.from_numpy(np.array(y_train).astype(np.float32)))

    ## test data
    test_data = TestData(torch.FloatTensor(X_test))
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    train_loader = DataLoader(dataset=train_data, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(dataset=test_data, batch_size=1)

    model = BinaryClassification()
    model.to(device)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # Tells pytorch that you're in training mode 
    model.train()
    for e in range(1, EPOCHS+1):
        epoch_loss = 0
        epoch_acc = 0
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            
            y_pred = model(X_batch)
            
            loss = criterion(y_pred, y_batch.unsqueeze(1))
            acc = binary_acc(y_pred, y_batch.unsqueeze(1))
            
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            epoch_acc += acc.item()
            print(f'Epoch {e+0:03}: | Loss: {epoch_loss/len(train_loader):.5f} | Acc: {epoch_acc/len(train_loader):.3f}')
    # WINDOWS_PATH = "C:\Users\Administrator\Documents\VSCode\league_data"
    MAC_PATH = "/Users/namishkukreja/VSCode/league_data/model.pt"
    # torch.save(model.state_dict(), "newModel.pt")            
    y_pred_list = []

    model.eval()
    with torch.no_grad():
        for X_batch in test_loader:
            X_batch = X_batch.to(device)
            y_test_pred = model(X_batch)
            y_test_pred = torch.sigmoid(y_test_pred)
            y_pred_tag = torch.round(y_test_pred)
            y_pred_list.append(y_pred_tag.cpu().numpy())
    y_pred_list = [a.squeeze().tolist() for a in y_pred_list]
    confusion_matrix(y_test, y_pred_list)
    print(classification_report(y_test, y_pred_list))
    

def binary_acc(y_pred, y_test):
    y_pred_tag = torch.round(torch.sigmoid(y_pred))

    correct_results_sum = (y_pred_tag == y_test).sum().float()
    acc = correct_results_sum/y_test.shape[0]
    acc = torch.round(acc * 100)
    
    return acc

if __name__ == "__main__":
    main()



"""
dead code
in preprocess:
    top = []
    jungle = []
    mid = []
    bot = []
    support = []
    top.append(champs[match['info']['participants'][0]['championName']])
    jungle.append(champs[match['info']['participants'][1]['championName']])
    mid.append(champs[match['info']['participants'][2]['championName']])
    bot.append(champs[match['info']['participants'][3]['championName']])
    support.append(champs[match['info']['participants'][4]['championName']])
    top.append(champs[match['info']['participants'][5]['championName']])
    jungle.append(champs[match['info']['participants'][6]['championName']])
    mid.append(champs[match['info']['participants'][7]['championName']])
    bot.append(champs[match['info']['participants'][8]['championName']])
    support.append(champs[match['info']['participants'][9]['championName']])
    return pd.DataFrame(data={'top': top, 'jungle': jungle, 'mid': mid, 'bot': bot, 'support': 
            support, 'goldDiff': gd15, 'win': winCol})
"""