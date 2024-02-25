import datetime
import pandas as pd
import joblib
import os   
import tkinter as tk
import numpy as nb 
from datetime import timedelta
from math import sin, cos, pi
                       
class reader:
 
    wp01 = []
    om01 = [] 
    om36=[]
    travelling = []
    om36df = []
    wp01df = []
    om01df = []    
    travellingdf = []
    latestFiles=[]
    
    def __init__(self):
        self.warnings=[]
        self.pickCalc = []

    def clearArrays(self):
        self.om36=[]
        self.wp01=[]
        self.om01=[]
        self.om36df=[]
        self.wp01df=[]
        self.om01df=[]
        self.travelling = []
        self.travellingdf =[]



    def toteCheck(self,travel):
        pickedom01 = ['Travelling Totes (30+):'] 
        prepicks = ['Pre-picks (30+):']

    
        for index, row in travel.iterrows():
            if row['Travel Duration *']>=30:
                if isinstance(row['Dest *'],str):
                    if'TRY' in row['Dest *']:
                        prepicks.append([f'Tote: {row["Tote id *"]}',f'Prio: {row["Prio Date *"]}'])
                       
                    else:
                        pickedom01.append([f'Tote: {row["Tote id *"]}',f'Prio: {row["Prio Date *"]}'])

        return [pickedom01,prepicks]
    
    def latestComWo(self,filledNa):
        comsDropped = ['Coms Dropped till:']
        com = filledNa.dropna(subset=['prio date actual'])
        com = com[(com['disp strat'] == 'COM') & ~com['group'].str.contains('picking')  & ~com['group'].str.contains('startable')]
        
        datesArray=[]
        
        for index, row in com.iterrows():
            try:
                datesArray.append(datetime.datetime.strptime(row['prio date actual'], "%d/%m/%Y %I:%M:%S %p"))
            except ValueError:
                # If parsing with the specified format fails, use a fallback format
                datesArray.append(datetime.datetime.strptime(row['prio date actual'], "%d/%m/%Y").replace(hour=0, minute=0, second=0, microsecond=0))

        comsDropped.append(str(min(datesArray)))
        return comsDropped
    
    def latecomWo(self,filterwp01,timeHighestPick):
        priodatewp01 = ['Late COM WO:'] 
        for index, row in filterwp01.iterrows():
            if 'COM' in row['disp strat']:
                if row['prio date actual'] != '':

                    date_format = "%d/%m/%Y %I:%M:%S %p"
                    current_time = datetime.datetime.strptime(self.wp01[-1].split('_')[0], "%Y-%m-%d-%H-%M-%S")

                    try:
                        datetime_object = datetime.datetime.strptime(row['prio date actual'], date_format)
                    except ValueError:
                        format_str = '%d/%m/%Y'
                        datetime_object = datetime.datetime.strptime(row['prio date actual'], format_str)
                        datetime_object = datetime_object.replace(hour=0, minute=0, second=0, microsecond=0)
                    dateDifference = datetime_object - current_time

                    if dateDifference.total_seconds() < timeHighestPick*60*60: 
                        if 'pick' not in row['group']:
                            if 'startable' not in row['group']:
                                if 'consolid' not in row['disp strat']:
                                    priodatewp01.append([f'Route: {row["rouRef"]}',f'Prio: {row["prio date actual"]}',f'Reason: {row["wo not startable reason"]}'])
        return priodatewp01
    
    def blockedWp01(self,filteredblockedwp01):
        blockedWOwp01 = ['Blocked WO COM:']

        for i , r in filteredblockedwp01.iterrows():
            if r['rouRef_wp01late'] == '':
                continue
            blockedWOwp01.append([f'Route: {r["rouRef_wp01late"]}',f'Prio: {r["prio date actual_wp01late"]}',f'Reason: {r["wo not startable reason_wp01late"]}'])
        
        return blockedWOwp01
    
    def comReloc(self, mergedReloc,wp01):
        relocation = ['Reloc: (2hrs+)']
        filterReloc = wp01[wp01['reloc age [min]'] > 60]
        for j,k in filterReloc.iterrows():
            relocation.append([f'Route: {k["rouRef"]}',f'Prio: {k["prio date actual"]}',f'Reloc Time: {k["reloc age [min]"]}'])
        for j,k in mergedReloc.iterrows():
            relocation.append([f'Route: {k["rouRef"]}',f'Prio: {k["prio date actual"]}'])
        return relocation
    

    def palBlocked(self,om01):
        om01PalBlockReason = ['Pal Stack Blocked:']
        for index, row in om01[-1].iterrows():
            if isinstance(row['PalType'],str):
                
                    if isinstance(row['Priodate'],str):
                        date_format = '%d/%m/%Y %H:%M:%S' 
                        try:
                            datetime_object = datetime.datetime.strptime(row['Priodate'], date_format)

                        except ValueError:
                            format_str = '%d/%m/%Y'
                            datetime_object = datetime.datetime.strptime(row['Priodate'], format_str)
                            datetime_object = datetime_object.replace(hour=0, minute=0, second=0, microsecond=0)
                        current_time = datetime.datetime.strptime(self.om01[-1].split('_')[0], "%Y-%m-%d-%H-%M-%S")
                        dateDifference = datetime_object - current_time


                        focusom01 = om01[len(om01)-3][om01[len(om01)-3]['PalWoRef'] == row['PalWoRef']]
                        focusom01 = focusom01.fillna('NaN')
                        if (row['Pal Block reason *'] == focusom01['Pal Block reason *']).any():
                            om01PalBlockReason.append([f'WO: {row["PalWoRef"]}',f'Reason: {row["Pal Block reason *"]}',f'Prio: {row["Priodate"]}'])
        return om01PalBlockReason
    
    def palletizerProgression(self,mergedPalletWo):
        palletWo = ['Blocked AIO(1hr+):']
        for i,j in mergedPalletWo.iterrows():  
                palletWo.append([f'WO: {j["PalWoRef"]}',f'Prio: {j["Priodate_late"]}'])
        return palletWo
    
    def pickCalculator(self,om36,om36File):
        sixamCheck = ['Com Needed:']

        date_format = "%d/%m/%Y %H:%M:%S" 
        filtered_df = om36[(om36['Route State'] == '(80) Assigned') & (om36['Route Type'] == '(2) Despatch')]

        earliest_date = datetime.datetime.strptime(filtered_df['Route Departure Date'].min(), date_format)
        latest_date = datetime.datetime.strptime(filtered_df['Route Departure Date'].max(), date_format)

        hourly_interval = timedelta(hours=1)
        currentdateTime = earliest_date + timedelta(minutes=abs(earliest_date.minute - 60))

        pickArray=[]
        while currentdateTime <= latest_date:
            picks=0
            for index,row in filtered_df.iterrows():
                if datetime.datetime.strptime(row['Route Departure Date'],date_format) <= currentdateTime:
                    picks += int(row['COM # UM Open'])
            if picks > 0:
                pickArray.append([currentdateTime,picks])
            dateCalc = datetime.datetime.strptime(om36File.split('_')[0], "%Y-%m-%d-%H-%M-%S")
            next_day_at_8_am = dateCalc.replace(hour=8, minute=0, second=0) + timedelta(days=1)
            today_at_11_pm = dateCalc.replace(hour=23, minute=0, second=0)

            if currentdateTime == next_day_at_8_am:
                time_difference = today_at_11_pm - dateCalc
                hours_difference = time_difference.total_seconds() / 3600
                hoursCalc = picks/hours_difference
                if hoursCalc > 18000:
                    sixamCheck.append([hoursCalc,picks])
                if datetime.datetime.strptime(om36File.split('_')[0], "%Y-%m-%d-%H-%M-%S")>today_at_11_pm:
                    sixamCheck.append(['Remaining: ',picks])

            currentdateTime += hourly_interval

        
        return [pickArray,sixamCheck]
        
        

    def subsystemCheck(self,wp01,om36):
        subsystemMatch = ['Picks Match:']
        columnedwp01 = wp01
        columnedwp01.rename(columns={'cust omer': 'Customer Ident'}, inplace=True)
        columnedwp01.dropna(subset=['picks open'], inplace=True)
        
        columnedom36 = om36
        columnedom36.dropna(subset=['# UM Open'], inplace=True)


        summed_wp01 = columnedwp01.groupby('Customer Ident')['picks open'].sum().reset_index()
        
        summed_om36 = columnedom36.groupby('Customer Ident').agg({'# UM Open': 'sum', 'Route State': 'first'}).reset_index()

        print(summed_om36)


        merged_df = pd.merge(summed_wp01[['Customer Ident', 'picks open']], summed_om36[['Customer Ident', '# UM Open','Route State']], on='Customer Ident', how='outer')
        merged_df.fillna(0, inplace=True)

        merged_df['abs_difference'] = abs(merged_df['picks open'] - merged_df['# UM Open'])

        print(merged_df)


        for i,j in merged_df.iterrows():
            if j['abs_difference'] > 200:
                if j['picks open'] > j['# UM Open']:
                    filtered_df = columnedom36[columnedom36['Customer Ident'] == j['Customer Ident']]
                    subsystemMatch.append([f'Customer: {j["Customer Ident"]}',f'Route type: {j["Route State"]}',f'COM:{filtered_df["COM # UM Open"]}',f'AIO: {filtered_df["AIO # UM Open"]}',f'AIO: {filtered_df["CPS # UM Open"]}'])
                else:
                    subsystemMatch.append([f'Customer: {j["Customer Ident"]}',f'Route type: {j["Route State"]}',f'ABS Diff: {j["abs_difference"]}','LBS Higher'])

        return subsystemMatch
    
    

    def om36Parse(self,om36):
        planCheckom36 = ['Plan Check(2hrs+):'] 
        waitStartinfo = ['Wait Start Info:']
        calcVolume = ['Calc Volume:']

        date_format = "%d/%m/%Y %H:%M:%S" 
        format_str = '%d/%m/%Y'
        for index,row in om36.iterrows():
            #this is to check to see if there are any wait start info
            if isinstance(row['Route start info'], str):
                if 'Created' not in row['Route State']:
                    if "-I- at least one route exists with an earlier _departdate => postpone myself" in row['Route start info']:
                        waitStartinfo.append(f'Route: {row["lrou_ref"]}')


            if isinstance(row['Route Type'],str):
                if 'Calc' in row['Route Type']:
                    try:
                        datetime_object = datetime.datetime.strptime(row['Route Departure Date'], date_format)
                    except ValueError:
                        format_str = '%d/%m/%Y'
                        datetime_object = datetime.datetime.strptime(row['Route Departure Date'], format_str)
                        datetime_object = datetime_object.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                    if datetime.datetime.now().date() == datetime_object.date():
                        calcVolume.append(float(row['COM # UM Open']))


            # this is to check the calc route drop
            if isinstance(row['Route Type'],str):
                if isinstance(row['Route Start Date'],str):
                    if 'Calc' in row['Route Type']:
                        if 'Assigned' in row['Route State']:
                            
                            try:
                                datetime_object = datetime.datetime.strptime(row['Route Start Date'], date_format)
                            except ValueError:
                                datetime_object = datetime.datetime.strptime(row['Route Start Date'], format_str)
                                datetime_object = datetime_object.replace(hour=0, minute=0, second=0, microsecond=0)
                            current_time = datetime.datetime.now()
                            dateDifference = datetime_object - current_time
                            if dateDifference.total_seconds() > 7200:
                                planCheckom36.append(f'Route: {row["lrou_ref"]}')
                
        calcVolumeNum = 0
        for i in calcVolume:
            if isinstance(i,float):
                calcVolumeNum += i

        calcVolume = ['Todays Calc:',calcVolumeNum]
        return [calcVolume,planCheckom36,waitStartinfo]

        


    def checks(self,wp01,om36,om01,travelling):

        #TOTES -----------------
        totes = self.toteCheck(travelling[-1])

        pickedom01 = totes[0]
        prepicks = totes[1]

    
        #----------- com highest number 
        pickCheck = wp01[-1].loc[wp01[-1]['group'].str.contains('picking', na=False)].groupby('work sta tion')['picks'].sum().reset_index()
        com_rows = pickCheck[pickCheck['work sta tion'].str.contains('com', case=False)]
        highestPick = com_rows['picks'].max()
        timeHighestPick = highestPick / 500
        #------------
    
#------------------Data Frame filter --------------------
        
        
        filterwp01 = wp01[-1].fillna('')
        filterwp01late = wp01[0].fillna('')

        filterwp01reloc= wp01[len(wp01)-3].fillna('')
        filterwp01reloc = filterwp01reloc[filterwp01reloc['group'].str.contains('Active reloc')]

        mergedReloc = pd.merge(filterwp01, filterwp01reloc[['work order']], on='work order', suffixes=('_wp01', '_wp01Reloc'), how='inner')
        mergedReloc = mergedReloc.dropna(subset=['work order'])

        filterwp01 = filterwp01[(~filterwp01['group'].str.contains('pick'))& (~filterwp01['group'].str.contains('startable')) & (filterwp01['disp strat'].str.contains('COM')) ]

        filterwp01late = filterwp01late[(~filterwp01late['group'].str.contains('pick'))&(~filterwp01late['group'].str.contains('startable')) &(filterwp01late['disp strat'].str.contains('COM')) ]


        merged_df = pd.merge(filterwp01, filterwp01late, on='work order', suffixes=('_wp01', '_wp01late'))
        filteredblockedwp01 = merged_df.loc[merged_df.index.intersection(merged_df[merged_df['group_wp01'] == merged_df['group_wp01late']].index)]
        filteredblockedwp01 = filteredblockedwp01.drop_duplicates(subset='work order')

        #COM ARRAYS -----------------------------------------------------------
        priodatewp01 = self.latecomWo(filterwp01,timeHighestPick)
        blockedWOwp01 = self.blockedWp01(filteredblockedwp01)
        relocation = self.comReloc(mergedReloc,wp01[-1])
        comsDropped = self.latestComWo(wp01[-1])
# need to make a no stock check -----------------------


#OM01 CHECK-------------------------------
        columnsOm01 = ['Wait Pre pick *','In act ive *','No stock *','Blo cked *','Star ted *','Pi ck ing *','In spec tion *','Pi ck ed *']
        palletWolate = om01[-1][om01[-1][columnsOm01].isna().all(axis=1)]
        palletWoearly = om01[len(om01)-3][om01[-3][columnsOm01].isna().all(axis=1)]
        mergedPalletWo = pd.merge(palletWolate, palletWoearly, on='PalWoRef', suffixes=('_late', '_early'))
        mergedPalletWo.drop_duplicates(subset=['PalWoRef'], keep='first', inplace=True)
        mergedPalletWo.dropna(axis=0, how='any', inplace=True)
        om01PalBlockReason=self.palBlocked(om01)
        palletWo = self.palletizerProgression(mergedPalletWo)
        


        #------------------------------------------------------------------------ om36

        pickCalculator = self.pickCalculator(om36[-1],self.om36[-1])
        sixamCheck=[]

    
        self.pickCalc = pickCalculator[0]
        sixamCheck = pickCalculator[1]
        print('THIS IS THE PICK CALC')
        print(self.pickCalc)

        
      

        subsystemMatch = self.subsystemCheck(wp01[-1],om36[-1])
        om36Parse = self.om36Parse(om36[-1])
        planCheckom36 = om36Parse[1]
        waitStartinfo = om36Parse[2]
        calcVolume = om36Parse[0]


            #------------------------------------------------------------------------------

                                      
            
                                                

        self.warnings = [blockedWOwp01,relocation,priodatewp01,pickedom01,prepicks,planCheckom36,waitStartinfo, subsystemMatch , om01PalBlockReason,sixamCheck,comsDropped,palletWo,self.latestFiles]

#-----------CHECKS END -----------------------------------------



    def process(self):
        files = [file for file in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), file)) and file.endswith('.csv')]
        joblib.Parallel(n_jobs=4)(joblib.delayed(self.directoryCheck)(i) for i in files) 

        self.clearArrays()
        self.readFiles()
        #first element in the array is the earliest report and the last element in the array is the latest
        print(f'om36{len(self.om36)}')
        print(f'wp01{len(self.wp01)}')
        print(f'om01{len(self.om01)}')
        print(f'travelling{len(self.travelling)}')

        self.dataFrameprocess(self.om36,self.om36df)
        self.dataFrameprocess(self.wp01,self.wp01df)
        self.dataFrameprocess(self.om01,self.om01df)
        self.dataFrameprocess(self.travelling,self.travellingdf)
       
        #there should be atleast 5 in an array 
        self.checks(self.wp01df,self.om36df,self.om01df,self.travellingdf)






    def dataFrameprocess(self,arrayfrom, arrayTo):
        print(f'THIS IS WHAT THE FILES ARRAY LOOKS LIKE{arrayfrom}')

        for file in arrayfrom:

            df = pd.read_csv(file, sep=',', skiprows=1, skipinitialspace=True, encoding='ISO-8859-1')
            arrayTo.append(df)


    def get_datetime_from_string(self,date_string):
        return datetime.datetime.strptime(date_string.split('_')[0], "%Y-%m-%d-%H-%M-%S")
    
    def directoryCheck(self,file): 
                smallerName = file.split('_')[0]
                if os.path.exists(file):
                    try:
                        dateObject = datetime.datetime.strptime(smallerName, "%Y-%m-%d-%H-%M-%S")
                        time_difference = datetime.datetime.now() - dateObject
                    
                        if time_difference>timedelta(hours=4):
                            try:
                                os.remove(file)
                           
                            except FileNotFoundError:
                                print(f"File '{file}' not found.")
                            except Exception as e:
                                print(f"An error occurred: {e}")
                    except ValueError:
                        print(f"Cannot convert '{smallerName}' to a datetime object.")
      



    def readFiles(self):

        files = [file for file in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), file)) and file.endswith('.csv')]
        
        for file in files:
            if os.path.exists(file) and '.csv' in file:
                lowercase_file = file.lower() 
                if 'wp01' in lowercase_file:   
                    self.wp01.append(file)
                if 'om36' in lowercase_file:   
                    self.om36.append(file)
                if 'om01' in lowercase_file:   
                    self.om01.append(file)
                if 'travelling' in lowercase_file:  
                    self.travelling.append(file)

        
        self.om36 = sorted(self.om36, key = self.get_datetime_from_string)
        self.wp01 = sorted(self.wp01, key = self.get_datetime_from_string)
        self.om01 = sorted(self.om01, key = self.get_datetime_from_string)
        self.travelling = sorted(self.travelling, key = self.get_datetime_from_string)
        self.latestFiles = [self.om36,self.wp01,self.om01,self.travelling]

    
    def timeCompare(self,dateobject):       
        currentTime = datetime.datetime.now().astimezone(datetime.timezone.utc)
        if dateobject:
            time_difference = currentTime - dateobject
            if time_difference.total_seconds() <= 14400:
           
                return 1
            else:
         
                return 0

        










