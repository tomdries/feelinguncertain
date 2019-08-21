#By Tom Driessen. Some helper functions

import matplotlib.pyplot as plt

def tlx_from_string(wl_string):
    """Takes a string with 6 numbers ranging from 0 (0%) to 20 (100%)
        Returns: Nasa TLX score"""
    a = wl_string.split(" ")
    a = [x for x in a if x != '']
    a = [float(x) for x in a]
    a = np.array(a)
    if len(a) == 6:
        tlx = np.multiply(np.average(a), 5)
        return tlx
    else:
        print('Check string! Length is not 6.')


def vdl(participant, exp_key):
    """Return (usefulness, satisfaction)"""
    scores=[]

    for i in range(8,17):
        question = f"{key}{i}" # noucfog8, noucfog9...

        # 3 6 and 8 are mirrored
        score = -float(quest_raw.loc[quest_raw['id'] == participant][question])+3
        if i in [10, 13, 15]: # these questions are mirrored
            score = -score
        scores.append(score)

    usefulness = sum(scores[x] for x in [0, 2, 4, 6, 8]) / 5
    satisfaction = sum(scores[x] for x in [1, 3, 5, 7]) / 4
    return (usefulness, satisfaction)



def select_experiment(quest_df, conditions, questions):
    df = []
    indices = []
    for q in questions:
        for c in conditions:      
            indices.append(f"{c}{q}")
    likert_cols = ["SD", "D", "N", "A", "SA"]
    df = quest_df[indices]
    df_out = pd.DataFrame( columns=likert_cols,
                         index=indices)
    
    # Count frequency of SD, D, N and A, SA an NA 
    for key in df.keys():
        for i in range(1,6):          
            try:
                count = df[key].value_counts()[i]
            except:
                count = 0
            
            
            df_out.loc[key, likert_cols[i-1]] = count 
            likert_df = df_out
    return likert_df


def plot_likert(likert_df):
    dummy = likert_df.iloc[::-1]  #Had to reverse it
    likert_colors = ['white', 'firebrick','lightcoral','gainsboro','cornflowerblue', 'darkblue']
    middles = dummy[["SD", "D"]].sum(axis=1)+dummy["N"]*.5
    longest = middles.max()
    complete_longest = int(dummy.sum(axis=1).max())
    dummy.insert(0, '', (middles - longest).abs())
    

    dummy.plot.barh(stacked=True, color=likert_colors, edgecolor='none', legend=False, figsize = (6,20))

    z = plt.axvline(longest, linestyle='--', color='black', alpha=.5)
    z.set_zorder(-1)

    plt.xlim(-0.25*complete_longest, 2.25*complete_longest)
    xvalues = range(0,2*complete_longest+1,7)

    xlabels = [str(x-longest) for x in xvalues]
    plt.xticks(xvalues, xlabels)