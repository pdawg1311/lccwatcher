
        #---------------- ACCURATE CALCUATOR -------------------------------------------------------

        coms = op14f[-1]['wo dest'].unique()

        print(f"THIS SHOULD BE COMS 1-40 {coms}")

        picksPerCom = []

        for i in coms:
            for index,row in op14f[-1].iterrows():
                if row['wo dest']==i:
                    picksPerCom.append([row['wo dest'],row['wo group seq'],row['wo ref'],row['cases next hour']])

        
        print(f'THIS IS MY NEW {picksPerCom}')
        filtered_df = wp01[-1][(wp01[-1]['disp strat'] == 'COM')]
        filtered_df = filtered_df.dropna(subset=['prio date actual'])

        date_format = "%d/%m/%Y %I:%M:%S %p"


        print(f'prio dates {filtered_df['prio date actual']}')

        earliest_date = datetime.datetime.strptime(filtered_df['prio date actual'].min(), date_format)
        latest_date = datetime.datetime.strptime(filtered_df['prio date actual'].max(), date_format)

        





        print(f'earliest WP01 {earliest_date}')
        print(f'latest WP01 {latest_date}')


        #------ find accurate calculator in the wp01 section now