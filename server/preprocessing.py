import pandas as pd
#We will use OneHotEncoding:
def oneHot_encoder(df, column):
    df = df.copy()
    dummies = pd.get_dummies(df[column], prefix=column)
    df = pd.concat([df, dummies], axis=1)
    df = df.drop(column, axis=1)
    return df

def preprocessing(df):
    # Load the data
    df['date_zre'] = pd.to_datetime(df['date_zre'], format='%d/%m/%y %H:%M:%S,%f')
    df['day_of_week'] = df['date_zre'].dt.day
    df['hour'] = df['date_zre'].dt.hour

    #use onehoteencoding 
    for column in ['terminal', 'nature_marchandise','couloir']:
        df = oneHot_encoder(df, column=column)
    df['is_ensemble_routier'] = df.ss_type_unite.eq('Ensemble Routier')

    # handle the 'type de marchandise' column
    df['is_semi_remorque'] = df.ss_type_unite.eq('Semi Remorque')
    df['is_Camion_12m_ou_moins'] = df.ss_type_unite.eq('Camion 12m ou moins')
    df['is_20'] = df.ss_type_unite.eq("20'")
    df['is_40'] = df.ss_type_unite.eq("40'")
    df['is_45'] = df.ss_type_unite.eq("45'")
    df['is_tracteur'] = df.ss_type_unite.eq("Tracteur")
    df = df.drop(columns='ss_type_unite')

    df['winddir_lt_150'] = df.winddir.lt(150)
    df = df.drop(columns='winddir')

    df['visibility_lt_15'] = df.visibility.lt(15)
    df = df.drop(columns='visibility')
    return df
        

