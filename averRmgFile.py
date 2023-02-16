import os
import numpy as np
import pandas as pd

def makeAvgdf(df, start, last):
    # this function takes a dataframe and start and last index and returns a new averaged dataframe

    # group the data by level
    df_sub = df[start:last]
    level_group = df_sub.groupby('Level')

    # make a new dataframe
    """ 
    header index = 
        [' ', 'Level', 'Bias Field (G)', 'Spin Speed (rps)', 'Hold Time (s)',
        'Mz (emu)', 'Std. Dev. Z', 'Mz/Vol', 'Moment Susceptibility (emu/Oe)',
        'Mx (emu)', 'Std. Dev. X', 'My (emu)', 'Std. Dev. Y', 'Remarks',
        'Core Dec', 'Core Inc', 'M (emu)', 'CSD', 'Sample Height (cm)',
        'Date/Time ']
    """

    new_df = pd.DataFrame()
    new_df[' '] = level_group[' '].first()

    if (new_df[' '] == 'UAFX1').any() :
        new_df[' '] = 'AF'
    elif (new_df[' '] == 'UAX1').any():
        new_df[' '] = 'AF'

    print("I found levels of and each corresponding level has counts of")
    print(pd.DataFrame([level_group['Level'].count(), new_df[' '], level_group['Bias Field (G)'].first()], index = ['counts (# of meas)', 'Type (NRM/AF/ARM)', 'biased field (G)']))

    print("I will average them!")
    new_df['Level'] = level_group['Level'].mean()
    new_df['Bias Field (G)'] = level_group['Bias Field (G)'].first()
    new_df['Spin Speed (rps)'] = level_group['Spin Speed (rps)'].mean()
    new_df['Hold Time (s)'] = level_group['Hold Time (s)'].mean()
    new_df['Mz (emu)'] = level_group['Mz (emu)'].mean()
    new_df['Std. Dev. Z'] = level_group['Std. Dev. Z'].mean()
    new_df['Mz/Vol'] = level_group['Mz/Vol'].mean()
    new_df['Moment Susceptibility (emu/Oe)'] = level_group['Moment Susceptibility (emu/Oe)'].mean()
    new_df['Mx (emu)'] = level_group['Mx (emu)'].mean()
    new_df['Std. Dev. X'] = level_group['Std. Dev. X'].mean()
    new_df['My (emu)'] = level_group['My (emu)'].mean()
    new_df['Std. Dev. Y'] = level_group['Std. Dev. Y'].mean()
    new_df['Remarks'] = level_group['Remarks'].first()

    # calculate declination and inclination
    r = np.sqrt(new_df['Mx (emu)']**2 + new_df['My (emu)']**2 + new_df['Mz (emu)']**2)
    new_df['Core Dec'] = (np.arctan2(new_df['My (emu)'], new_df['Mx (emu)']) * (180 / np.pi)  + 360) % 360
    new_df['Core Inc'] = np.arcsin(new_df['Mz (emu)'] / r) * (180 / np.pi)
    new_df['M (emu)'] = r

    new_df['CSD'] = level_group['CSD'].mean()
    new_df['Sample Height (cm)'] = level_group['Sample Height (cm)'].first()
    new_df['Date/Time '] = level_group['Date/Time '].first()


    return new_df

def writeAvgrmg(file):
    # this function takes a rmg file from inputs folder and write avg rmg file in outputs folder

    # read the file
    df = pd.read_csv('inputs/' + file, header = 1, sep=',')

    # find the index where biased field is not zero so that we can make a section
    bf = df['Bias Field (G)']
    bf_idx =  bf[bf != 0].index

    # make a section 
    level = df['Level']
    allAvgdf = []

    for current_bf_idx in bf_idx:
        start = current_bf_idx
        print("I am calculating the biased field of index: ", bf[current_bf_idx] , "G")
        
        i = start
        while True:
            i += 1
            if i == len(level) - 1:
                last = i + 1
                break
            if level[i + 1] < level[i]:
                    last = i + 1
                    break
            else:
                continue

        # make a new dataframe
        allAvgdf.append(makeAvgdf(df, start, last))

        print("finished calculating the biased field of index: ", bf[current_bf_idx] , "G \n \n")

    # concatenate all the dataframes
    new_df = pd.concat(allAvgdf)

    # write the content of the file in a new file
    with open('outputs/' + file, 'w') as f:
        new_df.to_csv(f, index = False, header = df.head().columns , sep = ',')

    print("I wrote down this on: " + 'outputs/' + str(file) + "\n \n")



#writeAvgrmg('your file name')
