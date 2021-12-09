"""
This module prepares epm datasets in 'data' folder for plotting.
"""
import pandas as pd


def session_agg():
    """
    This function automatically reads csv file contains 
    all the detailed students' log activities across six sessions.
    Then it generates the sum of each students' log activities 
    for each activity type of one session for six sessions

    Return
    -------
    A dataframe with 4169 rows and 10 columns 
    showing aggregated log activities for each activity type 
    for each student in six sessions

    """
    log_raw = pd.read_csv('data/all_log.csv')
    # drop irrelevant cols
    drop_cols = ['start_time','exercise','end_time']
    log_raw = log_raw.drop(columns = drop_cols)

    log_session = log_raw.groupby(['session','student_id','activity']).sum()
    log_session = log_session.reset_index()

    return log_session

def session_avg(log_session):
    """
    This function read calculates the mean of 
    log activities across six sessions.

    Parameter
    ---------
    log_session: DataFrame
        Dataframe generated by session_agg function
    
    Return 
    ------
    A dataframe with 54 rows and 9 columns

    """
    class_average = log_session.groupby(['session','activity']).mean()
    class_average = class_average.reset_index().drop(columns='student_id')

    return class_average

def mid_avg():
    """
    This function automatically reads in the intermediate grades data in
    the "data" folder, then calculates out the quantile and average grades 
    of the class for each session.

    Return
    ---------
    The function returns a dataframe of three columns, which are 'Student Id', 
    'Session', 'Avg_grades'.
    """
    mid_grades= pd.read_excel('data/intermediate_grades.xlsx',engine='openpyxl')
    #calculate the mean
    mid_avg = pd.DataFrame(mid_grades.mean(axis=0))
    mid_avg = mid_avg.drop(['Student Id'])
    mid_avg.reset_index(inplace = True)
    mid_avg.columns = ['Session', 'Avg_grades']
    mid_avg.insert(0, "Student Id", 'Average')

    #calculate the Q1
    mid_avg_Q1 = pd.DataFrame(mid_grades.quantile(q=0.25, axis=0))
    mid_avg_Q1 = mid_avg_Q1.drop(['Student Id'])
    mid_avg_Q1.reset_index(inplace = True)
    mid_avg_Q1.columns = ['Session', 'Avg_grades']
    mid_avg_Q1.insert(0, "Student Id", 'Q1')

    #calculate the median
    mid_avg_Q2 = pd.DataFrame(mid_grades.quantile(q=0.5, axis=0))
    mid_avg_Q2 = mid_avg_Q2.drop(['Student Id'])
    mid_avg_Q2.reset_index(inplace = True)
    mid_avg_Q2.columns = ['Session', 'Avg_grades']
    mid_avg_Q2.insert(0, "Student Id", 'Q2')

    #calculate the Q3
    mid_avg_Q3 = pd.DataFrame(mid_grades.quantile(q=0.75, axis=0))
    mid_avg_Q3 = mid_avg_Q3.drop(['Student Id'])
    mid_avg_Q3.reset_index(inplace = True)
    mid_avg_Q3.columns = ['Session', 'Avg_grades']
    mid_avg_Q3.insert(0, "Student Id", 'Q3')

    #transform the data into another dataframe
    mid_std = pd.melt(mid_grades, id_vars='Student Id', 
                  value_vars=['Session 2', 'Session 3',
                              'Session 4', 'Session 5',
                              'Session 6'])
    mid_std.columns = ['Student Id', 'Session', 'Avg_grades']

    mid_all = pd.concat([mid_avg, mid_avg_Q1, mid_avg_Q2, mid_avg_Q3, mid_std])
    mid_all['Student Id'] = mid_all['Student Id'].astype(str)
    #cut the long tail after the dot
    mid_all['Avg_grades'] = mid_all.apply(lambda x: round(x["Avg_grades"],2), axis=1)
    return mid_all

def final_step_1():
    '''
    This function automatically reads in the final grades data in the "data" folder, 
    then calculate out the score for each Session and standardize the data into a scale
    of full score for each session and TOTAL are 10.

    Returns
    ---------
    The function returns a dataframe with columns of Session1 to Session6 and TOTAL
    '''
    data= pd.read_excel('data/final_grades.xlsx',engine='openpyxl')

    #grab the columns' title
    namelist = list(data).copy()

    #calculate the grade sum for each session
    data['Session1'] = data.apply(lambda x: x[namelist[1]] +  x[namelist[2]], axis=1)
    data['Session2'] = data.apply(lambda x: x[namelist[3]] +  x[namelist[4]], axis=1)
    data['Session3'] = data.apply(lambda x: x[namelist[5]] + x[namelist[6]] + x[namelist[7]] + x[namelist[8]] + x[namelist[9]], axis=1)
    data['Session4'] = data.apply(lambda x: x[namelist[10]] + x[namelist[11]], axis=1)
    data['Session5'] = data.apply(lambda x: x[namelist[12]] + x[namelist[13]]  + x[namelist[14]], axis=1)
    data['Session6'] = data.apply(lambda x: x[namelist[15]] +  x[namelist[16]], axis=1)

    #only keep the grades for each session and total
    data_final_use=pd.DataFrame(data, columns=["Student ID", "Session1", "Session2"
                                               , "Session3", "Session4", "Session5", "Session6", "TOTAL\n(100 points)"])

    data_final_use.columns=["Student ID", "Session1", "Session2"
                            , "Session3", "Session4", "Session5", "Session6", "TOTAL"]

    #standardize
    data_final_use['Session1'] = data_final_use.apply(lambda x: x["Session1"]*10/data_final_use.max()[1], axis=1)
    data_final_use['Session2'] = data_final_use.apply(lambda x: x["Session2"]*10/data_final_use.max()[2], axis=1)
    data_final_use['Session3'] = data_final_use.apply(lambda x: x["Session3"]*10/data_final_use.max()[3], axis=1)
    data_final_use['Session4'] = data_final_use.apply(lambda x: x["Session4"]*10/data_final_use.max()[4], axis=1)
    data_final_use['Session5'] = data_final_use.apply(lambda x: x["Session5"]*10/data_final_use.max()[5], axis=1)
    data_final_use['Session6'] = data_final_use.apply(lambda x: x["Session6"]*10/data_final_use.max()[6], axis=1)
    data_final_use['TOTAL'] = data_final_use.apply(lambda x: x["TOTAL"]/10, axis=1)

    #get it looked better with drop the tail
    data_final_use['Session1'] = data_final_use.apply(lambda x: x["Session1"].round(2), axis=1)
    data_final_use['Session2'] = data_final_use.apply(lambda x: x["Session2"].round(2), axis=1)
    data_final_use['Session3'] = data_final_use.apply(lambda x: x["Session3"].round(2), axis=1)
    data_final_use['Session4'] = data_final_use.apply(lambda x: x["Session4"].round(2), axis=1)
    data_final_use['Session5'] = data_final_use.apply(lambda x: x["Session5"].round(2), axis=1)
    data_final_use['Session6'] = data_final_use.apply(lambda x: x["Session5"].round(2), axis=1)
    data_final_use['TOTAL'] = data_final_use.apply(lambda x: x["TOTAL"].round(2), axis=1)

    return(data_final_use)

def final_avg(data_final_use):
    '''
    This function automatically reads in the intermediate grades data in
    the "data" folder, then calculates out the quantile and average grades 
    of the class for each session.

    Parameter
    ---------
    a dataframe with columns are different Sessions and TOTAL, rows are ID and scores 
    of students who have taken the final.

    Return
    ---------
    The function returns a dataframe of three columns, which are 'Student ID', 
    'Session', 'Avg_grades'. The quantiles and average of grades are also listed
    inside this dataframe with their 'Student ID's are 'Q1','Q2','Q3','Average'
    '''
    #calculate the mean
    final_avg = pd.DataFrame(data_final_use.mean(axis=0))
    final_avg = final_avg.drop(['Student ID'])
    final_avg.reset_index(inplace = True)
    final_avg.columns = ['Session', 'Avg_grades']
    final_avg.insert(0, "Student ID", 'Average')

    #calculate the Q1
    final_avg_Q1 = pd.DataFrame(data_final_use.quantile(q=0.25, axis=0))
    final_avg_Q1 = final_avg_Q1.drop(['Student ID'])
    final_avg_Q1.reset_index(inplace = True)
    final_avg_Q1.columns = ['Session', 'Avg_grades']
    final_avg_Q1.insert(0, "Student ID", 'Q1')

    #calculate the median
    final_avg_Q2 = pd.DataFrame(data_final_use.quantile(q=0.5, axis=0))
    final_avg_Q2 = final_avg_Q2.drop(['Student ID'])
    final_avg_Q2.reset_index(inplace = True)
    final_avg_Q2.columns = ['Session', 'Avg_grades']
    final_avg_Q2.insert(0, "Student ID", 'Q2')

    #calculate the Q3
    final_avg_Q3 = pd.DataFrame(data_final_use.quantile(q=0.75, axis=0))
    final_avg_Q3 = final_avg_Q3.drop(['Student ID'])
    final_avg_Q3.reset_index(inplace = True)
    final_avg_Q3.columns = ['Session', 'Avg_grades']
    final_avg_Q3.insert(0, "Student ID", 'Q3')
    final_avg_Q3

    #transform the data into another dataframe
    final_std = pd.melt(data_final_use, id_vars='Student ID', 
                  value_vars=['Session1', 'Session2', 'Session3',
                              'Session4', 'Session5',
                              'Session6','TOTAL'])
    final_std.columns = ['Student ID', 'Session', 'Avg_grades']

    #merge into one
    final_all = pd.concat([final_avg, final_avg_Q1, final_avg_Q2, final_avg_Q3, final_std])
    final_all['Student ID'] = final_all['Student ID'].astype(str)
    #cut the long tail after the dot
    final_all['Avg_grades'] = final_all.apply(lambda x: round(x["Avg_grades"],2), axis=1)
    
    return(final_all)