import os
import re
import csv
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms
from google.appengine.api import urlfetch
from google.appengine.api import users
from google.appengine.api import mail
from app import models
 
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import datetime
import random


def index(request):
  user();
  return render_to_response('app/index.html',{'a':random.randint(1,10),},)


#####################################################################
####                                                             ####
####   Function:For Register Login User & Login Time
####     Using Each Function
####           
####   Purpose:
####      Save User & DateTime into datastore
####                                            
####                                                             ####
#####################################################################
def user():
  user = users.get_current_user()

  query = db.Query(models.User).filter('user_id =', user.user_id())
  e = query.get()
      
  #Aleady this AppleID of SKU exists => Check the Price only...
  if e:
    time = datetime.datetime.now()
    time += datetime.timedelta(0,0,0,0,0,9)
    e.datetime = time
  
  else:
    e = models.User()
    e.email = user.email()
    e.user_id = user.user_id()
    e.nickname = user.nickname()
    time = datetime.datetime.now()
    time += datetime.timedelta(0,0,0,0,0,9)
    e.datetime = time
    
    user_address = "Admin<araseyuta@gmail.com>"
    sender_address = "Admin<araseyuta@gmail.com>"
    subject = "[Newsstand Analytics Test]%s started using! "% user.email()
    body = """
      %s has started using of [Newsstand Analytics Test]
           """% user.email()
    mail.send_mail(sender_address, user_address, subject, body)
  e.put() 





#####################################################################
####                                                             ####
####   Function:For Calclation Total Sale Each Apps
####     URL: /totalsale/
####           
####   Purpose:
####      GET:Show the Form in order to Upload TSV file(AppleReport)
####                                            
####      POST:
####        1:Load TSV File & Load SKU list from Datastore
####        2:Calclate each SKU and each subscriptin units in the target file
####        3:multiple each SKU Units and SKU cost (to estimate total sales each SKU)
####        4:Summing each SKU sales to parent SKU
####                                            
####                                                             ####
#####################################################################
def totalsales(request):
  if request.method == 'GET':
    user();
    return render_to_response('app/totalsales.html',{'a':random.randint(1,10),},)

  elif request.method == 'POST':
    NS = {};
    SKUlist = [];
    ParentSKU={};
    SKU2PriceDict={};
    SKU2ParentDict={};

    query = models.SKU.all().order('SKU')
    #Make list of SKU
    for e in query:
      if e.SKU == 'SKU':
        continue;
      #if SKU is ns_ . . .  => Add to ParentSKUlist
      if e.SKU[0:3] == "ns_":
        ParentSKU[e.SKU] = 0;

      #if SKU is not ns_ . . .  => Add to SKUlist
      else:
        SKUlist.append(e.SKU);
        SKU2PriceDict[e.SKU] = e.price;
        SKU2ParentDict[e.SKU] =e.ParentIdentifier;

    #Make Dictionary of SKU
    for SKU in SKUlist:
      NS[SKU] = 0;
    
    #check selecting file    
    while True:
      try:
        r = request.FILES['file']
        break;

      except:
        return render_to_response('app/totalsales.html',{'try':'Prease select your AppleReport. . .',},)
#      except Exception as e:
#        return render_to_response('app/totalsales.html',{'try':'Prease select your AppleReport. . .','e':e},)


    #Load TSV file (OF APPLE REPORT)
    r = request.FILES['file'];
    lines = r.readlines();

    count = 0;    
    #Load Each Record. . .
    for line in lines:
      count = count +1;
      AppleReport = line[:-1].split('\t');
      if len(AppleReport)<18:
        continue;
      SKU = AppleReport[2];
      Unit = AppleReport[7];
      
      #if SKU colm means AppDownloadCount -> Add the Units. . .       
      for SKUMatch in SKUlist:
        if SKU == SKUMatch:
          NS[SKU] = NS[SKU] + int(Unit);
        
        
    #After Adding All Recoad of Units -->  Calc The Price of Each SKU
    for SKU in SKUlist:
      NS[SKU] = NS[SKU] * SKU2PriceDict[SKU];

    #Calc the Each Apps -->  Calc The Price of Each SKU
    for SKU in SKUlist:
      ParentSKU[SKU2ParentDict[SKU]]= ParentSKU[SKU2ParentDict[SKU]] + NS[SKU];

                    
    return render_to_response('app/totalsales.html',
        {
         'POST':True,
         'r':r.name,
         'NS':ParentSKU.items(),
    },)


#####################################################################
####                                                             ####
####   Function:For Calclation of App Download count
####     URL: /app/
####           
####   Purpose:
####      GET:Show the Form in order to Upload TSV file(AppleReport)
####                                            
####      POST:
####        1:Load TSV File & Load SKU list from Datastore
####        2:Checking the Each Record of AppleReport
####          >if SKU( such as ns_application_name) is listed :: Add the Units
####                                            
####                                                             ####
#####################################################################
def app(request):
  if request.method == 'GET':
    user();
    return render_to_response('app/app.html',{'a':random.randint(1,10),},)

  elif request.method == 'POST':
    NS = {};
    SKUlist=[];
    
    query = models.SKU.all().order('SKU')
    #Make list of SKU
    for e in query:
      if e.SKU[0:3] == "ns_":
        SKUlist.append(e.SKU);
    
    #Make Dictionary of SKU
    for SKU in SKUlist:
      NS[SKU] = 0;
    
    #check selecting file    
    while True:
      try:
        r = request.FILES['file']
        break;

      except:
        return render_to_response('app/app.html',{'try':'Prease select your AppleReport. . .',},)
#      except Exception as e:
#        return render_to_response('app/app.html',{'try':'Prease select your AppleReport. . .','e':e},)
    
    #Load TSV file (OF APPLE REPORT)
    r = request.FILES['file'];
    lines = r.readlines();
    count = 0;
    
    #Load Each Record. . .
    for line in lines:
      count = count +1;
      AppleReport = line[:-1].split('\t');
      if len(AppleReport)<18:
        continue;
      SKU = AppleReport[2];
      Unit = AppleReport[7];
      
      #if SKU colm means AppDownloadCount -> Add the Units. . .       
      if SKU[0:3] == "ns_":
        for SKUMatch in SKUlist:
          if SKU == SKUMatch:
            if AppleReport[6] == "1F":
              NS[SKU] = NS[SKU] + int(Unit);
                      
    return render_to_response('app/app.html',
        {
         'POST':True,
         'r':r.name,
         'NS':NS.items(),
    },)
    


#####################################################################
####                                                             ####
####   Function:For Calclation of Weekly Report
####     URL: /sales/
####           
####   Purpose:
####      GET:Show the Form in order to Upload TSV file(AppleReport)
####                                            
####      POST:
####        1:Load TSV File & Load SKU list from Datastore
####        2:Checking the Each Record of AppleReport
####          >if SKU is listed :: Add the Units
####        3:After adding Units all of records, Calc the Price
####                                                             ####
#####################################################################
def sales(request):
  if request.method == 'GET':
    user();
    return render_to_response('app/sales.html',{'a':random.randint(1,10),},)

  elif request.method == 'POST':
    POST = True;
    NS = {};
    SKUlist=[];
    SKU2PriceDict = {};
    query = models.SKU.all().order('SKU')

    #Make list of SKU
    for e in query:
      if e.SKU == "SKU":
        continue;
      if e.SKU[0:3] == "ns_":
        continue;
      SKUlist.append(e.SKU);
      SKU2PriceDict[e.SKU] = e.price;

    #Make Dictionary of SKU
    for SKU in SKUlist:
      NS[SKU] = {'SKU':SKU,
                 'New':{'price':0,'units':0},
                 'Renewal':{'price':0,'units':0}
                }
    
    #check selecting file
    while True:
      try:
        r = request.FILES['file']
        break;
      
      except:
        return render_to_response('app/sales.html',{'try':'Prease select your AppleReport. . .',},)
#      except Exception as e:
#        return render_to_response('app/sales.html',{'try':'Prease select your AppleReport. . .','e':e},)

    #Load TSV file (OF APPLE REPORT)
    r = request.FILES['file'];
    lines = r.readlines();
    count = 0;
    
    #Load Each Record. . .
    for line in lines:
      count = count +1;
      AppleReport = line[:-1].split('\t');
      SKU = AppleReport[2];
      Unit = AppleReport[7];
      Subscription = AppleReport[18];
      
      #if Subscription colm is NULL -> Skip. . . 
      if Subscription == 'New':
        Subscription = Subscription
      elif Subscription == 'Renewal':  
        Subscription = Subscription              
      else:
        continue

      #if SKU colm means Header -> Skip. . .       
      if SKU == "SKU":
        continue;

      #if SKU colm means AppDownloadCount -> Skip. . .       
      if SKU[0:3] == "ns_":
        continue;
        
      #Check, is SKU in a list? -> IF exists, Add the Units 
      for SKUMatch in SKUlist: 
        if SKU == SKUMatch:
          NS[SKU][Subscription]['units'] = NS[SKU][Subscription]['units'] + int(Unit);

    #After Adding All Recoad of Units --> Calculate the Price. . .
    for SKU in SKUlist:
      NS[SKU]['New']['price'] = NS[SKU]['New']['units'] * SKU2PriceDict[SKU];
      NS[SKU]['Renewal']['price'] = NS[SKU]['Renewal']['units'] * SKU2PriceDict[SKU];
      
    
    return render_to_response('app/sales.html',
        {
         'POST':POST,
         'r':r.name,
         'NS':NS.items(),
    },)




#####################################################################
####                                                             ####
####   Function:For Register New SKU
####     URL: /register/
####           
####   Purpose:
####      GET:Show the Form in prder to Upload CSV file
####                                            
####      POST:
####        1:Load CSV File
####        2:Search AppleID of SKU In Datastore
####          >if New :: Add to the datastore
####          >if Already exists :: Check price only
####                                                             ####
#####################################################################
def register(request):
  if request.method == 'GET':
    user();
    return render_to_response('app/register.html',{'a':random.randint(1,10),},)

  elif request.method == 'POST':
    POST = True;
    SKUlist = [];
    NewSKUlist = [];
    
    #check selecting file    
    while True:
      try:
        r = request.FILES['file']
        break;
      except:
        return render_to_response('app/register.html',{'try':'Prease select your AppleReport. . .',},)
#      except Exception as e:
#        return render_to_response('app/register.html',{'try':'Prease select your AppleReport. . .','e':e},)

    #OpenFile
    r = request.FILES['file'];
    lines = r.readlines();
    
    #Check Return code
    if len(lines)==1:
      lines = lines[0].split(chr(13));

    if len(lines)==1:
      lines = lines[0].split(chr(10));
    
    value = 1;#for Debug

    #Read each line => and Check AppleID in datastore
    for line in lines:
      AppleReport = line.split(',');
      
      if len(AppleReport)<18:
        continue;
      
      if AppleReport[14] == 'Apple Identifier':
        continue;

      query = db.Query(models.SKU).filter('AppleID =', int(AppleReport[14]))
      e = query.get()
      
      #Aleady this AppleID of SKU exists => Check the Price only...
      if e:
        e.price = int(AppleReport[15])
        
        value = value + 1;
      
      #Fine New AppleID of SKU => Save to Datastore
      else:
        e = models.SKU()
        e.SKU = AppleReport[2]
        e.price = int(AppleReport[15])
        e.ParentIdentifier = AppleReport[17]
        e.AppleID = int(AppleReport[14])
        
        NewSKUlist.append(e);
        value = value + 1;


      #Both OLD and NEW, Put to the Datastore and Push to the SKULIST...
      e.put()
      SKUlist.append(e)

    
    return render_to_response('app/register.html',{
      'POST':POST,
      'r':r.name,
      'NewSKUlist':NewSKUlist,
      'SKUlist':SKUlist,
    },)
