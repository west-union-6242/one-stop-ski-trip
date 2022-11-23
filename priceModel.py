import pandas as pd
import numpy as np
import re
import sklearn.model_selection as msel
import sklearn.ensemble as ens
import sklearn.metrics as met

class priceModel:

    model = None
    title_rank = ["cottage","penthouse","chalet","villa","cabin","lodge","house","townhouse","breakfast","condo","apartment","apt","loft"]
    
    def transformTitle(self, title):
        title = str(title).lower()
        rank = 0
        for j in self.title_rank:
            if j in title:
                break
            rank += 1
        if rank >= len(self.title_rank):
            rank = len(self.title_rank) / 2
        else:
            rank = len(self.title_rank) - rank
        return float(rank)
    
    def transformRoomType(self, roomtype):
        roomtype = str(roomtype).lower()
        if "entire" in roomtype or "whole" in roomtype:
            roomtype = 1
        else:
            roomtype = 0
        return roomtype
    
    def transformRating(self, rating):
        try:
            rating = float(rating)
            if np.isnan(rating):
                rating = float(2.5)
            return rating
        except Exception as e:
            return float(2.5)
    
    def __init__(self, path, r = 404):
        try:
            df = pd.read_csv(path, encoding = "ISO-8859-1", header = None)
            x = df.to_numpy()[:,:8]
            y = df.to_numpy()[:,-1]
        
            #transform price
            invalid = []
            count = 0
            price = 0
            for i in range(len(y)):
                res = re.search(r'\$\d{3}', str(y[i]).lower())
                if res != None:
                    price = str(res.group())
                    price = float(price[1:])
                    y[i] = price
                else:
                    invalid.append(count)
                count += 1
        
            #transform input variables
            for i in range(x.shape[0]):
                aa = float(x[i,1])
                bb = float(x[i,2])
                if np.isnan(aa) or np.isnan(bb):
                    raise Exception("lat/lon not a number")
                x[i,1] = aa
                x[i,2] = bb
                x[i,3] = self.transformTitle(x[i,3])
                x[i,4] = int(x[i,4])
                x[i,5] = self.transformRoomType(x[i,5])
                x[i,6] = self.transformRating(x[i,6])
            x = x[:,[1,2,3,4,5,6]]
        
            y = np.delete(y, invalid)
            x = np.delete(x, invalid, axis=0)
        
            print("x shape:", x.shape)
            print("y shape:", y.shape)
        
            x_train, x_test, y_train, y_test = msel.train_test_split(x, y, test_size = 0.2, shuffle = True, random_state = r)
            rf_reg = ens.RandomForestRegressor(random_state = r)
            rf_reg.fit(x_train, y_train)
            y_predict_train = rf_reg.predict(x_train)
            y_predict_test = rf_reg.predict(x_test)
            train_mse = met.mean_squared_error(y_train, y_predict_train)
            test_mse = met.mean_squared_error(y_test, y_predict_test)
            print("train_mse:", train_mse)
            print("test_mse:", test_mse)
    
            self.model = rf_reg
        except Exception as e:
            print("priceModel init failed:", e)
        return None

    def predict(self, row):
        try:
            row = np.array(row)
            aa = float(row[1])
            bb = float(row[2])
            if np.isnan(aa) or np.isnan(bb):
                raise Exception("lat/lon not a number")
            row[1] = aa
            row[2] = bb
            row[3] = self.transformTitle(row[3])
            row[4] = int(row[4])
            row[5] = self.transformRoomType(row[5])
            row[6] = self.transformRating(row[6])
            row = row[[1,2,3,4,5,6]]
            return self.model.predict([row])[0]
        except Exception as e:
            print("priceModel predict failed:", e)
            return np.round(((np.random.rand() * 800) + 200), 2)

pm = priceModel("data/trainingdata_price1.csv")
print(pm.predict(["Vail, Colorado, United States","39.64169","-106.39195","Great Location! Spacious Studio with FREE Shuttle, Rentals and More","2","Entire serviced apartment","","https://www.airbnb.com/rooms/34402668"]))

