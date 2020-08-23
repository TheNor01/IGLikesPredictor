# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 14:52:30 2020

@author: Aldo&Giorgio
"""


import pandas as pd
import numpy as np

import array
import imageio
import json
from pprint import pprint


import tensorflow as tf
import keras as kf

#print("v1  " + tf.__version__)
#print("v2  " + kf.__version__)



#Importo libreria (locale)




from InstagramAPI import InstagramAPI


username="aldo.fiorito"
API = InstagramAPI(username, "spaceboy99?")
API.login()
#API.getProfileData()

#Prendere tutti i POST
import time
myposts=[]
has_more_posts = True
max_id=""


#DATI GREZZI
while has_more_posts:
    API.getSelfUserFeed(maxid=max_id)
    if API.LastJson['more_available'] is not True:
        has_more_posts = False #stop condition
        print ("stopped")
    
    max_id = API.LastJson.get('next_max_id','')
    myposts.extend(API.LastJson['items']) #merge lists
    time.sleep(2) # per evitare flooding nei server




with open('query.json', 'w') as outfile:
    json.dump(myposts, outfile)


i = 0;
import json

otherPosts = []

input_file = open ('query.json')
json_array = json.load(input_file)

for item in json_array:
    otherPosts.append(item)

print("len {}".format( len(otherPosts)))

myposts_sorted = sorted(otherPosts, key=lambda k:
k['like_count'],reverse=True) 
top_posts=myposts_sorted[:len(otherPosts)]


print("\n \n \n")
print(top_posts)



reList = []
likeList = []

#filtro foto semplici
while i  < len(top_posts):
 #print("Json = {}".format(i))
     print(i)
     try:  
         photo = top_posts[i]["image_versions2"]["candidates"][0]["url"]
         reList.append(photo)
         i+=1
     except KeyError :
         print("NON E' UNA SEMPLICE IMMAGINE")
         i+=1
 
 
print(reList) #DEFINITIVA , Contiene semplici foto

import os
if not os.path.exists('./Photos'):
    os.makedirs('./Photos')
    
if not os.path.exists('./NewPhotos'):
    os.makedirs('./NewPhotos')

#Cancello le vecchie foto
import os, shutil
folder = './Photos'
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))
'''
'''


#SALVO LE FOTO IN LOCALE
i=0
from urllib import request
while i < len(reList ):
    f = open('./Photos/0000000%d.jpg'%(i), 'wb')
    f.write(request.urlopen(reList[i]).read())
    like = top_posts[i]["like_count"]    #prendo il numero di likes
    likeList.append(like)
    f.close()
    i+=1

print("ENDED" )
print(len(likeList))
print(len(reList)) 





column_names = ["images", "objects", "likes"]  # creo un dataframe con immagine , oggetti presenti e likes
df = pd.DataFrame(columns = column_names)
'''


#Ora devo analizzare gli oggetti presenti nelle foto
'''
from imageai.Detection import ObjectDetection
import os

execution_path = os.getcwd()

detector = ObjectDetection()
detector.setModelTypeAsRetinaNet()
detector.setModelPath( os.path.join(execution_path , "resnet50_coco_best_v2.0.1.h5"))  # mi affido al modello
detector.loadModel()



#Creo delle foto con gli oggetti evidenziati
i = 0
while i < len(likeList):
    detections = detector.detectObjectsFromImage(input_image=os.path.join(execution_path ,'./Photos/0000000%d.jpg'%(i)), output_image_path=os.path.join(execution_path ,'./NewPhotos/0000000%d.jpg'%(i)))
    for eachObject in detections:
         print(eachObject["name"] , " : " , eachObject["percentage_probability"])
         df = df.append({'images':reList[i],'objects':eachObject["name"],'likes':likeList[i]},ignore_index=True)
    i+=1
print(df)




#Tolgo i duplicati
df=df.sort_values('likes').drop_duplicates(subset=['images', 'objects'], keep='last')
print(df)
df.to_csv("output.csv",index=False)

#raggruppo per oggetti e ne faccio la media dei likes
df = pd.read_csv('output.csv')
df1=df.groupby('objects', as_index=False)['likes'].mean().round(0)
print(df1)

#devo dare dei pesi
numOfRows = len(df1.index)
print(" \n \n \n",numOfRows)
unici=df1['likes'].nunique()
print("UNICI",unici)


singleWeigth=int(100/numOfRows)
print("PESO:",singleWeigth)
df1=df1.sort_values(by='likes', ascending=True)



df1["Weigths"] = np.nan
df1 = df1.reset_index(drop=True)

print(df1)


i=0

#Creo una sorta di media pesata, do pù peso a gli oggetti che hanno preso tanti like e valorizzo meno quelli che ne hanno presi pochi

peso=singleWeigth
while i < numOfRows:
    doppione=False
    if(pd.isna(df1.loc[i,"Weigths"])):
        df1.loc[i,'Weigths'] = peso
        j=i+1
        likeCounter=df1.loc[i,'likes']
        currentWeigth=singleWeigth
        print("I:",i)
        print("LikeC",likeCounter)
        while j < numOfRows:
            #print("WHILE2")
            newLike=df1.loc[j,'likes']
            print("newLike",newLike)
            if(pd.isna(df1.loc[j,"Weigths"])):
                if(likeCounter==newLike):
                 df1.loc[j,'Weigths'] = peso
                 doppione=True
            j+=1
    if(doppione==False):        
        peso=peso+singleWeigth
    print(peso)
    i+=1    
print(df1)

#Chiedere quanti oggetti saranno inseriti dalla lista            
Oggetti = df1['objects'].tolist()
print(Oggetti)

while True:
    try:
        numObs = int(input("Quanti oggetti saranno presenti? "))
        if numObs > 0:
            break
        else:
            print ('Inserire almeno un valore')
    except ValueError:
        print ('Input non corretto')


i=0
myObs=[]
while i < numObs:
    while True:
        try:
            object=input("Inserisci un oggetto desiderato presente nella lista -> ")
            if(object in Oggetti):
              i+=1
              myObs.append(object)
              if(i==numObs):
               break
            else:
             print ('Oggetto non presente')
        except ValueError:
            print ('Input was not a digit - please try again.')          
            
            
print(myObs)
dataObs = df1['objects'].values.tolist()
myWeigth=[]
myLikes=[]
i=0
while i < len(myObs):
    index = dataObs.index(myObs[i])
    myWeigth.append(df1.iloc[index]['Weigths'])
    myLikes.append(df1.iloc[index]['likes'])
    i+=1

print("Like :",myLikes)
print("Pesi :",myWeigth)


for g in range(len(myLikes)):
   myLikes[g] = myLikes[g] *myWeigth[g] / sum(myWeigth)
predictLike = int(sum(myLikes))
print(predictLike)


#FINE
