from django.http import HttpResponseRedirect,HttpResponse
from django.shortcuts import get_object_or_404,render

import requests,json,re
import pandas as pd
import numpy as np

shiny_IP = "http://127.0.0.1:4511"
targetfn = "../shinyapp/targetfn.txt"

def index(request):
    return render(request,'homepage/index.html')

def display(request):

    if request.method == 'POST':
        search_id = request.POST.getlist('textfield',None)
        print(search_id)

##        kwset = []

##        for index,item in enumerate(search_id):
##            if len(item) == 0:
##                item = initial_search_id[index]
##            else:
##                item = item
##            kwset.append(item)
            
        (dy,au,kw,fenxi) = search_id

        # import pinyin list
        pinyindict = {}
        with open('pinyinlist.txt') as wf:
            for line in wf:
                ws = line.rstrip().split()
                pinyindict[ws[0]] = ws[1]
                
        ############### analysis 1
        charcountdict = {}
        if str(fenxi) == '1':
            # first, parse keywords
            kwlist = kw.split(' ')
            #
            if len(dy) == 0:
                dylist = ['4','7','8','13']
            else:
                dylist = dy.split(' ')
                
            if len(au) == 0:
                counti = 0
                
                # no input from author; start searching as normal
                for k in kwlist:
                    if k in pinyindict:
                        kpinyin = pinyindict[k]
                    else:
                        kpinyin = k
                    for d in dylist:
                        response = requests.get("https://api.sou-yun.com/api/poem?key="+str(k)+"&scope=3&dynasty="+str(d)+"&jsontype=true")
                        poem_json = response.json()                       
                        if poem_json == None:
                            PoemCount = 0
                        else:
                            PoemCount = poem_json['Count']
                        charcountdict[counti+1] = {'Dynasty':d,'Author':"All","Keyword":k, 'KeywordPinyin':kpinyin,'PoemCount':PoemCount}
                        counti += 1
            else:
                aulist = au.split(' ')
                
                counti = 0
                
                # search by author
                for k in kwlist:
                    if k in pinyindict:
                        kpinyin = pinyindict[k]
                    else:
                        kpinyin = k                    
                    for a in aulist:
                        response = requests.get("https://api.sou-yun.com/api/poem?key="+str(k) + ' ' + str(a)+"&scope=0&jsontype=true")
                        poem_json = response.json()                       
                        if poem_json == None:
                            PoemCount = 0
                        else:
                            PoemCount = poem_json['Count']
                        charcountdict[counti+1] = {'Dynasty':"NotApplicable",'Author':a,"Keyword":k,'KeywordPinyin':kpinyin,'PoemCount':PoemCount}
                        counti += 1

            outputdf = pd.DataFrame.from_dict(charcountdict, orient='index')
            outputdf.to_csv("../shinyapp/poemcount.txt",sep=",",encoding="utf-8")           

        ############### analysis 2
        Shidict = {}
        if str(fenxi) == '2':
            # first, parse keywords
            kwlist = kw.split(' ')
            #
            if len(dy) == 0:
                dylist = ['4','7','8','13']
            else:
                dylist = dy.split(' ')
                
            if len(au) == 0:
                vocab = {}
                
                # no input from author; start searching as normal
                for k in kwlist:
                    if k in pinyindict:
                        kpinyin = pinyindict[k]
                    else:
                        kpinyin = k
                    for d in dylist:
                        response = requests.get("https://api.sou-yun.com/api/poem?key="+str(k)+"&scope=3&dynasty="+str(d)+"&jsontype=true")
                        poem_json = response.json()                       
                        if poem_json == None:
                            continue
                        else:
                            ShiDatalist = poem_json['ShiData']
                            for index,ShiData in enumerate(ShiDatalist):
                                Clauseslist = [i['Content'] for i in ShiData['Clauses']]
                                Clauseslen = len(Clauseslist)
                                Clausescontent = "".join(Clauseslist[0:min(8,Clauseslen)])
                                for c in Clausescontent:
                                    if c in ["。","，","？","！","；","："]:
                                        continue
                                    if c in vocab:
                                        vocab[c] += 1
                                    else:
                                        vocab[c] = 1
                                        
                    freq5w = sorted(vocab, key=lambda k: vocab[k],reverse = True)[:5]

                    for freqindex,fw in enumerate(freq5w):
                        if fw in pinyindict:
                            fwpinyin = pinyindict[fw]
                        else:
                            fwpinyin = fw                       
                        Shidict[freqindex+1] = {'Dynasty':d,'Author':"All","Keyword":k, 'KeywordPinyin':kpinyin,'freqword':fw,'freqwordpinyin':fwpinyin,'freq':vocab[fw],'order':freqindex}
                    
            else:
                aulist = au.split(' ')
                
                vocab = {}
                
                # search by author
                for k in kwlist:
                    if k in pinyindict:
                        kpinyin = pinyindict[k]
                    else:
                        kpinyin = k
                    if len(k) == 0:
                        k = "none"
                        kpinyin="none"
                    for a in aulist:
                        response = requests.get("https://api.sou-yun.com/api/poem?key="+ str(a)+"&scope=1&jsontype=true")
                        poem_json = response.json()                       
                        if poem_json == None:
                            continue
                        else:
                            ShiDatalist = poem_json['ShiData']
                            for index,ShiData in enumerate(ShiDatalist):
                                Clauseslist = [i['Content'] for i in ShiData['Clauses']]
                                Clauseslen = len(Clauseslist)
                                Clausescontent = "".join(Clauseslist[0:min(8,Clauseslen)])
                                for c in Clausescontent:
                                    if c in ["。","，","？","！","；","："]:
                                        continue                                    
                                    if c in vocab:
                                        vocab[c] += 1
                                    else:
                                        vocab[c] = 1
                                        
                    freq5w = sorted(vocab, key=lambda k: vocab[k],reverse = True)[:10]

                    for freqindex,fw in enumerate(freq5w):
                        if fw in pinyindict:
                            fwpinyin = pinyindict[fw]
                        else:
                            fwpinyin = fw                       
                        Shidict[freqindex+1] = {'Dynasty':"NotApplicable",'Author':a,"Keyword":k, 'KeywordPinyin':kpinyin,'freqword':fw,'freqwordpinyin':fwpinyin,'freq':vocab[fw],'order':freqindex}
 

            outputdf = pd.DataFrame.from_dict(Shidict, orient='index')
            outputdf.to_csv("../shinyapp/freqwords.txt",sep=",",encoding="utf-8")           
            
  #      shiDict = {}
        
##        response = requests.get("https://api.sou-yun.com/api/poem?key="+str(au)+"&scope=1&dynasty="+str(dy)+"&jsontype=true")
##        poem_json = response.json()
##        print(poem_json.keys())
##        ShiDatalist = poem_json['ShiData']
##
##        for index,ShiData in enumerate(ShiDatalist):
##            Dynasty = ShiData['Dynasty']
##            Author = ShiData['Author']
##
##            if "Type" in ShiData:
##                Type = ShiData['Type']
##            else:
##                Type = "unknown"
##            
##            if "Rhyme" in ShiData:
##                Rhyme = ShiData['Rhyme']
##            else:
##                Rhyme = "unknown"
##
##            Title = ShiData['Title']['Content']
##            Clauseslist = [i['Content'] for i in ShiData['Clauses']]
##            Clauseslen = len(Clauseslist)
##            Clausescontent = "".join(Clauseslist[0:min(8,Clauseslen)])
##
##            shiDict[index] = {'Dynasty':Dynasty,'Author':Author,'Type':Type,'Rhyme':Rhyme,\
##                              'Title':Title, 'ClausesLen':Clauseslen, 'Content':Clausescontent}
##
##        outputdf = pd.DataFrame.from_dict(shiDict, orient='index')
##        outputdf.to_csv(targetfn,sep="|",encoding="utf-8")
            
        return HttpResponseRedirect(shiny_IP)

    else:        
        return render(request,'homepage/display.html')
