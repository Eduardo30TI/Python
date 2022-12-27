import phonenumbers
from glob import glob
import os
import pandas as pd

temp_path=os.path.join(os.getcwd(),'*.xlsx')

arq=glob(temp_path)

df=pd.read_excel(arq[-1])

if __name__=='__main__':

    phones=[str(l).strip() for l in df['Telefone'].tolist()]

    for i,phone in enumerate(phones):

        ddd=df.loc[i,'DDD']

        tel_format=f'{ddd}{phone}'

        tel_ajust=phonenumbers.parse(tel_format,'BR')

        tel_format=phonenumbers.format_number(tel_ajust,phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        tel_format=''.join([l.strip() for l in tel_format])

        tel_format=''.join([l.strip() for l in tel_format.split('-')])

        print(tel_format)

        pass

    pass