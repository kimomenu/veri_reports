
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from datetime import datetime
from odpslides.presentation import Presentation


# import data
data=pd.DataFrame()
data=pd.read_csv('veri_data_export.csv')




# select data only about glucose
filtered=data[['base_time_string','base_type','glucose_value']].loc[data['base_type']=='glucose']


# create list of dates
filtered['date_only']=filtered['base_time_string'].str[:10]
list_dates=filtered['date_only'].unique()

## create column with hours
filtered['hour']=filtered['base_time_string'].str[11:]

# use datetime as index
filtered=filtered.set_index('base_time_string')

#create empty list for statistics
stats=pd.DataFrame()

# fill stats tables with data from filtered dataframe
for day in list_dates:
    stats.at[day,'mean']=round(filtered.query(f"date_only == '{day}' "  )['glucose_value'].mean(),1)
    stats.at[day,'std_dev']=round(filtered.query(f"date_only == '{day}' "  )['glucose_value'].std(),1)
    stats.at[day,'max']=round(filtered.query(f"date_only == '{day}' "  )['glucose_value'].max(),1)
    stats.at[day,'min']=round(filtered.query(f"date_only == '{day}' "  )['glucose_value'].min(),1)    

#print results
print('Glucose values mean standard_deviation max and min values')
print('\n')
#print(stats)



### Event flagger

filtered=filtered.reset_index()

# count minuts over 140
limit=140 #mg/dl glucose
itercount=0
event=0

stats[f"mins glucose> {limit}"]=np.nan

for pos in filtered.index:
    val=filtered.at[pos,'glucose_value']
    
    #add interval of 15 mins over limit
    if val>limit:
        print(f"Glucose value {filtered.at[pos,'glucose_value']} at {filtered.at[pos,'base_time_string']} ")
        #print(data.iloc[val])
        itercount=itercount+1
        event=event+1
    else:
        #records number of 15min intervals after event is done
        if event>0:
            date_limit_exceed=filtered.at[pos,'date_only']
            
            #this detects multiple events
            if not pd.isna(stats.at[date_limit_exceed,f"mins glucose> {limit}"]):
                event=int(event+float(stats.at[date_limit_exceed,f"mins glucose> {limit}"][14:17])/15)
                #print(event)
                #print(float(stats.at[date_limit_exceed,f"mins glucose> {limit}"][13:16]))
            
            print(f"Events lasted {event*15} minutes")
            print("\n")
            
            stats.at[date_limit_exceed,f"mins glucose> {limit}"]=str(f"Events lasted {event*15}  minutes")
            
        event=0
    
print('end loop')
print(itercount)
print(stats)








### Plotter creator


# crea list of figures
figures_list=pd.DataFrame()


for target in list_dates:
    
    #declaracio grafic
    fig, ax = plt.subplots(figsize=(12, 6))
    x=filtered.query(f"date_only == '{target}' "  )['hour']
    y=filtered.query(f"date_only == '{target}' "  )['glucose_value']
    ax.plot(x,y);
    
    #linies horitzontals
    ax.xaxis.set_major_locator(ticker.MultipleLocator(8))
    plt.grid(True)
    
    #noms eixos
    plt.xlabel("Hora")
    plt.ylabel("Glucose mg/dL")
    
    #titol
    plt.title(label=target, fontsize=25,color="blue")
    #min max vertical
    plt.ylim(50, 200)
    
    #limits glucosa
    plt.axhline(y=140,linewidth=2, color='#d62728')
    plt.axhline(y=70, linewidth=2, color='#d62728')
    
    #informacio estadistica
    textstr= '\n'.join((
    r'Average %.2f mg/dL' % (stats.at[target,'mean'], ),
    r'Min %.2f mg/dL' % (stats.at[target,'min'], ),
    r'Max %.2f mg/dL' % (stats.at[target,'max'], ),
    r'Std dev %.2f' % (stats.at[target,'std_dev'], ),
    str(stats.at[target,f"mins glucose> {limit}"  ])  ))

    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.8, 0.2, textstr, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=props)
    
    #area vermella sobre excessos 140
    threshold=140
    ax.fill_between(x, 0, 1, where=y > threshold,
                color='red', alpha=0.25, transform=ax.get_xaxis_transform())
    
    #plt.rcParams["figure.figsize"]=(20,10)
    plt.savefig(f"figures/plot {target}.png")
    plt.show()
    plt.close()
    
    #guarda nom arxiu per a powerpoint
    figures_list.at[target,'image']=f"plot {target}.png"



#### Powerpoint export module



P = Presentation(title_font_color='blue', subtitle_font_color='black',
                 footer='Glucose Reports', show_date=True,
                 date_font_color='i',
                 footer_font_color='i',
                 page_number_font_color="i")

P.add_title_chart( title='Glucose Reports', subtitle='Month Year')

for date in figures_list.index:
    P.add_titled_image( title='Daily data',
                        image_file=f"figures/{figures_list.at[date,'image']}",
                        pcent_stretch_center=95, pcent_stretch_content=95)

P.save( filename='Export slides glucose.odp', launch=1 )
