from django.shortcuts import render

from django.http import HttpResponse

from django.http import HttpResponse

from .models import Question
from django.template import loader
from django.shortcuts import render
from django import forms
import logging
import numpy as np
#from scipy import * 
import matplotlib.pyplot as plt  
import pandas as pd
import os  
from pylab import *
#import scipy.linalg as lg 


# In[35]:

def read_all_file(path=None):
    allnames=[]
    for f in os.listdir(path):
        ext=os.path.splitext(f)[1]
        if ext.lower() not in ['.csv']:
            continue
        allnames.append(f)
    len_=len(allnames)
    return allnames,len_
 

def import_data():
    path='C:\\Users\\Lab\\Conversation_bluemix\\datasets'
    allnames, len_=read_all_file(path) 
    for num in arange(len(allnames)):
        name=os.path.join(path,allnames[num])	
        if allnames[num]=='S1.csv': # .csv
            S1=np.genfromtxt(name,delimiter=',')
            row,col=S1.shape
            S1=S1[1:row,:] 
        else:
            t=np.genfromtxt(name,delimiter=',')  
            t=t.reshape((2740,1))
            t=t[1:2741,:] 
    return S1, t 


# In[36]:

def index_static_overload(t,S1,p_1,dev0,deltime,simTime):
#Post-fault Over Load Index
#This index is used to observe if the post-fault flows surpass the network capacity, 
#by monitoring the power flows through the transmission lines right after an outage occurs. 
#[Sindex]=static_overload(t,t1,Signal,w,p,d);
# INPUTS
#t - Time vector
#S - Apparent power flow 
# p - Exponent
#d - Deviation allowed of power flow from nominal value, e.g. 10 for +10#    
#OUTPUTS
#Sindex -Overload index
#OVERLOAD 
    pre0=5 
# static_overload.m:23
    post0=100 
# static_overload.m:24
    dev0=dev0 / 100.0
    nl=shape(S1)[1]
    wf_i=ones((1,nl)) 
    Snom=mean(S1[0:pre0,:],0)
    Smax=Snom*(1+dev0) 
    Spost=S1[(S1.shape[0]-post0-1):S1.shape[0],:]
    Smean=mean(Spost,0) 
    # Remove lines out of service
    xxx=[]
    for i in arange(0,nl):
        if abs(Smean[i]) < 1e-2:
            xxx.append(i)
            S1[:,i]=0
            Smean[i]=0
            Snom[i]=0            
    index_red=[]
    indx=[]
    over_line=[]
    rid=[]
    ridh=[]
    i2h=[]
    for i in arange(0,nl):
        indxs_loc=wf_i[0,i]*(abs(Smean[i])/abs(Smax[i]))**p_1
        index_red.append(indxs_loc) 
        if indxs_loc >= 1:
            indx.append(indxs_loc)
            over_line.append(i)
        else:
            indx.append(1)
        rid.append(index_red[i]**(1/float(p_1))) 
        if rid[i]<=1:
            ridh.append(1)
            i2h.append(1)
        else:
            ridh.append(rid[i])
            i2h.append(index_red[i])   
    Fx=[]
    FFx=[]
    for i in arange(0,size(rid)):
        Fx.append(rid[i])
        FFx.append(i)
    F=r_[FFx,Fx]
    F=F.T.copy() 
    fx=[]
    ffx=[]
    for i in arange(0, len(over_line)):
        fx.append(ridh[over_line[i]])
        ffx.append(over_line[i])
    f=r_[ffx,fx]
    f=f.T.copy()
    i2h=np.nan_to_num(i2h)# change the nan to 0    
    Over_S=sum(i2h)/float(nl) 
    
    t1=simTime-3*deltime;
    t2=simTime-2*deltime;
    t3=simTime-deltime;
    t4=simTime;
    S=S1  
    lines=shape(S)
    
    # Sampling three equal intervals towards the end of the simulation for 'k-th' line
    SS1=[];tt1=[];
    SS2=[];tt2=[];
    SS3=[];tt3=[];
    Slope1=[]
    Slope2=[]
    Slope3=[]
    mean_slope=zeros((3,lines[1]))
    slope_change1=zeros((lines[1],2))
    variation=[]
    mm=[]
    for k in arange(0,lines[1]): 
        SS1_each_k=[];tt1_each_k=[]
        SS2_each_k=[];tt2_each_k=[]
        SS3_each_k=[];tt3_each_k=[]
        Slope1_each=[]
        Slope2_each=[]
        Slope3_each=[]
        for i in arange(0,size(t)):
            if t[i,0] > t1 and t[i,0] <=t2: 
                SS1_each_k.append(S[i,k])
                tt1_each_k.append(t[i,0])
            elif t[i,0] > t2 and t[i,0] <=t3:
                SS2_each_k.append(S[i,k])
                tt2_each_k.append(t[i,0])   
            elif  t[i,0] > t3 and t[i,0] <=t4:
                SS3_each_k.append(S[i,k])
                tt3_each_k.append(t[i,0])    
        SS1.append(SS1_each_k)
        tt1.append(tt1_each_k)
        SS2.append(SS2_each_k)
        tt2.append(tt2_each_k)
        SS3.append(SS3_each_k)
        tt3.append(tt3_each_k)
        count1=len(SS1_each_k)
        count2=len(SS2_each_k)
        count3=len(SS3_each_k)
        for i in arange(1,count1):
            Slope1_each.append((SS1_each_k[i]-SS1_each_k[i-1])/(tt1_each_k[i]-tt1_each_k[i-1]))
            if Slope1_each[i-1]==Inf or Slope1_each[i-1]==-Inf:
                Slope1_each.append(0)
        for i in arange(1,count2):
            Slope2_each.append((SS2_each_k[i]-SS2_each_k[i-1])/(tt2_each_k[i]-tt2_each_k[i-1]))
            if Slope2_each[i-1]==Inf or Slope2_each[i-1]==-Inf:
                Slope2_each.append(0) 
        for i in arange(1,count3):
            Slope3_each.append((SS3_each_k[i]-SS3_each_k[i-1])/(tt3_each_k[i]-tt3_each_k[i-1])) 
        Slope1.append(Slope1_each) 
        Slope2.append(Slope2_each) 
        Slope3.append(Slope3_each) 
        # Calculation of mean slope of the interval for 'k-th' line
        mean_slope[0,k]= mean(Slope1_each) 
        mean_slope[1,k]= mean(Slope2_each)
        mean_slope[2,k]= mean(Slope3_each) 
        # Calculation of slope variation between the intervals for 'k-th' line 
        slope_change1[k,0]=mean_slope[1,k]-mean_slope[0,k]
        slope_change1[k,1]=mean_slope[2,k]-mean_slope[1,k]
        # Calculation of the difference between the slope variation for 'k-th' line  
        variation.append(abs(slope_change1[k,1]-slope_change1[k,0]))
    # Assigning all the lines to an array
    for m in arange(0,lines[1]):
        mm.append(m) 
    G=c_[reshape(mm,[lines[1],1]),reshape(variation,[lines[1],1])]
    # loop to find the lines in which the power change/variation is high
    GG=[]
    gg=[]
    for i in arange(0,lines[1]):
        if variation[i]>2.5:
            GG.append(variation[i])
            gg.append(mm[i])
    c1=len(gg)
    if c1>0:
        g=c_[reshape(gg,[c1,1]), reshape(GG,[c1,1])]
    else:
        g=c_[0,0]
    steady_state_lines=[]
    for i in arange(0,lines[1]):
        if slope_change1[i,0]>0 and slope_change1[i, 1]<0 or abs(slope_change1[i,1]) <= abs(slope_change1[i,0]) and variation [i]< 0.01:
            steady_state_lines.append(i)
    Slines=len(steady_state_lines)
    if Slines==0:
        steady_state_lines=0    

    return Over_S,i2h,ridh,F,f,G,g,steady_state_lines 
 
logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")
	
	
def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)	
 

def index(request):
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
        'latest_question_list': latest_question_list,
    }
    return HttpResponse(template.render(context, request))
 
def test(request):
    context = {}
    template = loader.get_template('polls/test.html')
    return  HttpResponse(template.render(context, request))
	
def submit(request):
    number= request.GET['number']
    type=['Line Trip','Generator Trip','Three Phase Short Circuit','Load Change']
    angles=['1.1 degree','2.3 degree','0.9 degree', '1.2 degree']
    context = {
        'number': type[int(number)],
         'angle': angles[int(number)],
    }
    template = loader.get_template('polls/submit.html')
    return  HttpResponse(template.render(context, request))

def static_overload(request):
    answer=request.GET['number']
    S1,t=import_data()
    p=3
    d=10
    simTime=max(t)
    Faulttime=10
    deltime=10
    if answer=='yes':
        f_x,i2h,ridh,F,f,G,g,steady_state_lines = index_static_overload(t,S1,p,d,deltime,simTime)
    else:
        f_x=0
    context = {
             'index': f_x,
    }
    template = loader.get_template('polls/static_overload.html')
    return  HttpResponse(template.render(context, request))

  
from django.shortcuts import get_object_or_404, render

from .models import Question
# ...
def detail(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/detail.html', {'question': question})
	
	
