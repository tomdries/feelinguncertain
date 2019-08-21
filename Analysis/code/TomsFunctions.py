# By Tom Driessen. Some more helper functions to keep the jupyter notebooks less cluttered.

import pandas as pd
import numpy as np
from os import listdir
import matplotlib.pyplot as plt
from scipy import stats

import pickle


def save_obj(obj, name, path = 'obj/'):
    with open(path + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name, path = 'obj/'):
    with open(path + name + '.pkl', 'rb') as f:
        return pickle.load(f)
    
def slice_df(df, col, lb = -np.inf, ub = np.inf):
    # slice dataframe between lowerbound (lb) and upper bound (ub) 
    # in colum (col) of dataframe (df)
    return df.loc[(df[col] < ub) & (df[col] > lb)]

def load_recordings(participant, run, participantfolder):
     # Load python and silab recording files

    info = load_obj('stored_info') #information about individual recordings

    pairs = info[participant]['pairs'] # informations of what files belong to what recording
    fn_si = pairs.loc[pairs['run'] == run, 'filename_s'].iloc[0] # silab recording filename
    fn_py = pairs.loc[pairs['run'] == run, 'filename_p'].iloc[0] # python recording filenamt

    path_si = f'{participantfolder}/{participant}/silab/{fn_si}' # complete path of file
    path_py = f'{participantfolder}/{participant}/pyrec/{fn_py}' # complete path of file 

    # load files into dataframe
    file_si = pd.read_csv(path_si) 
    file_py = pd.read_csv(path_py, index_col = 0)
    
    return file_si, file_py

def f(x):
	# helper function for later function
    key = x['nearestF']
    key = f'v{key}'

    if key == 'v':
        return np.nan
    else:
        return x[key]

def f_ttp(x):
    # another helper
    s = x['sNearestF']
    vEgo = x['vEgo']
    vNearestF = x['vNearestF']

    if vEgo <= vNearestF:
        ttpF = 1e9
    else:
        ttpF = s / (vEgo - vNearestF)
    return ttpF


def getTTP_F(participant, run, participantfolder):


    # load silab and pythonrecordings
    si, py = load_recordings(participant, run, participantfolder)


    # For vehicles ahead:
    # Replace 0 with NaN in (StLongSAN, StLongSANL, StLongSANR)
    distF = si[['MeasurementTime', 'StLongSAN', 'StLongSANL', 'StLongSANR']]
    distF = distF.replace(0, np.nan)

    # take closest distance min(StLongSAN, StLongSANL, StLongSANR)
    min_distF = distF[['StLongSANL', 'StLongSAN', 'StLongSANR']].min(axis = 1, skipna = True)
    nearestF = distF[['StLongSANL', 'StLongSAN', 'StLongSANR']].idxmin(axis=1) #nearest vehicle
    nearestF = nearestF.apply(lambda x: str(x)[6:])
    nearestF = pd.DataFrame({'nearestF': nearestF})


    # velocity of closest vehicle

    # mindir = argmin(StLongSAN, StLongSANL, StLongSANR)
    # ttp = smin / v(mindir) 


    # For vehicles behind:

    vF = pd.concat([si[['MeasurementTime','vEgo', 'vSAN', 'vSANL', 'vSANR']], nearestF], axis = 1)

   

    vNearestF = pd.DataFrame({'vNearestF': vF.apply(f, axis = 1)})
    vF = pd.concat([vF, vNearestF], axis = 1)



    sF = pd.DataFrame({'sNearestF': min_distF})
    dfF = pd.concat([vF, sF], axis = 1)

    
    ttpF = pd.DataFrame({'ttpF': dfF.apply(f_ttp, axis=1)})
    dfF = pd.concat([dfF, ttpF], axis =1)

    return dfF

def ttp_fog_front(run, stamps, participantfolder):
    ttp9dict = {}
    participants = load_obj('participants')    
    #ttp9list =[np.nan]*len(stamps)
    
    #ttp9list = []
    r = run
    i_p = 0

    #create figure frame
    fig, axes = plt.subplots(14,8, figsize = (9,25), sharey = True)
    
    
    # go through participants
    for p in participants:
        print(p) #print current participant to get a sense of the progress

        ttp9list = []
        nearestto9list = []
        stampsprun = stamps.loc[(stamps['participant']== p) & (stamps['run'] == r)]

        # select only trials where vehicle approached from front (has 'F' in it)
        frontidx = stampsprun.apply(lambda x: 'F' in x['direction'], axis = 1)
        stampsF = stampsprun[frontidx]
        stampsF = list(stampsF['t_pass']) 
        stampsF = [stampsF[0] - 15000] + stampsF
       
        
        #for all time stamps in stamsF
        for i in range(len(stampsF)-1):
            if np.isnan(stampsF[i+1]):
                ttp9list.append(np.nan)
                nearestto9list.append(np.nan)
                continue
            else:
                sliced = slice_df(getTTP_F(p,r,participantfolder), 'MeasurementTime', stampsF[i], stampsF[i + 1])
                #find ttp9 stamp
                h = sliced['ttpF'].fillna(40)
                g = np.array([9] * len(h))
                idx9 = np.argwhere(np.diff(np.sign(h - g))).flatten()

                try: # try to find an intersection with TTP=9 line
                    ttp9stamp = sliced.iloc[min(idx9)]['MeasurementTime']
                    ttp9idx = min(idx9)
                    ttp9prev = sliced.iloc[min(idx9)-1]['ttpF']
                    ttp9next = sliced.iloc[min(idx9)+1]['ttpF']
            
                    
                    
                    if (abs(9-ttp9next) > 2):
                        
                        ttp9stamp = np.nan
                        ttp9idx = max(idx9)
                        ttp9stamp = sliced.iloc[max(idx9)]['MeasurementTime']
                    
                    nearestto9idx = np.argsort(abs(sliced['ttpF'].fillna(40) - 9)).iloc[0]
                    

                    nearestto9 = sliced['ttpF'].iloc[nearestto9idx]
                    


                except: 
                    
                    ttp9stamp = np.nan
                    nearestto9 = np.nan
                
                ttp9list.append(ttp9stamp)
                nearestto9list.append(nearestto9)

                #add axes to plot frame
                sliced['ttpF'].plot(ax=axes[i_p,i])
                axes[i_p, i].set_ylim([0,20])

                axes[i_p, i].axhline(9, color = 'g')
                axes[i_p, i].set_title(p)
                axes[i_p, i].get_xaxis().set_ticks([])
                try:     
                    axes[i_p,i].axvline(ttp9idx+sliced.index[0], color = 'green')
                except:
                    pass

        i_p +=1
        
        # Organize output
        fig.suptitle(run)
        stamps.iloc[frontidx[frontidx].index, 13] = ttp9list
        stamps.iloc[frontidx[frontidx].index, 14] = nearestto9list
        
    return stamps


