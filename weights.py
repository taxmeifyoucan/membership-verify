import pandas as pd
import time
from math import sqrt
import os
import argparse
import requests
import json 

# DAO 0x412a32DD71357bD12337F4408168DF903F90CBD3
# Multisigs
multisigv2='0x3250c2CEE20FA34D1c4F68eAA87E53512e95A62a'
multisigv1='0xF6CBDd6Ea6EC3C4359e33de0Ac823701Cc56C6c4'
# PG Splits
splitv2='0xd4ad8daba9ee5ef16bb931d1cbe63fb9e102ec10'
splitv1='0x84af3D5824F0390b9510440B6ABB5CC02BB68ea1'
# Splits main contract
split_main='0x2ed6c4B5dA6378c7897AC67Ba9e43102Feb694EE'

foundation='0x69f4b27882eD6dc39E820acFc08C3d14f8e98a99'

#TODO tx events from updateSplit

# Load file with all members
def membership(path):
    if os.path.exists(path):
        csv = pd.read_csv(path)
        data = csv[['address', 'start_timestamp', 'multiplier', 'break_months']]
        return data

def weight(data, timestamp):
    n = len(data)
    
    shares = []  
    for i in range(n):
        active_seconds = (timestamp - data['start_timestamp'].iloc[i]) -  data['break_months'].iloc[i] * 2629800
        activity_multiplier =  int(data['multiplier'].iloc[i] * active_seconds / (timestamp - data['start_timestamp'].iloc[i]))

        share = sqrt((timestamp - data['start_timestamp'].iloc[i]) * activity_multiplier / 100) * 0.99
        shares.append(int(share)) 

    data['share'] = shares

    foundation_share = {'address': foundation, 'share': sum(data['share']) / 99} 
    data = data.append(foundation_share, ignore_index = True) 

    return data.sort_values(by=['share'], ascending=False, ignore_index=True)
    # todo check addresses format

def percentage(data):
    total_shares = sum(data['share'])
    data['percentage'] = (data['share'] / total_shares) * 100 

def split(data):
    total_shares = sum(data['share'])
    data['split'] =((data['share'] / total_shares) * 1000000).astype(int)
    
    data.to_csv('output.csv')

def validate_safe_tx(response):

    to=response['txData']['to']['value']
    if to != split_main:
        print("Splits Main contract address mismatch")
    
    if args.v1:
        split_addr=splitv1
    else:
        split_addr=splitv2
    
    if (response['txData']['dataDecoded']['method'] == 'updateSplit') & (split_addr != response['txData']['dataDecoded']['parameters'][0]['value']):
            print("PG Split contract address mismatch")

def safe_tx(tx, data):
    url_base = 'https://safe-client.safe.global/v1/chains/1/transactions/multisig_'

    if args.v1:
        multisig=multisigv1
    else:
        multisig=multisigv2

    url = url_base + multisig + '_' + tx

    headers = {
        'Origin': 'https://app.safe.global'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        jres= json.loads(response.text)
        validate_safe_tx(jres)
    else:
        print("Safe tx not found")
        return 1

    if jres['txData']['dataDecoded']['method'] == 'createSplit':
        addresses_list=(jres['txData']['dataDecoded']['parameters'][0]['value'])
        percentage_list=(jres['txData']['dataDecoded']['parameters'][1]['value'])
    else:
        addresses_list=(jres['txData']['dataDecoded']['parameters'][1]['value'])
        percentage_list=(jres['txData']['dataDecoded']['parameters'][2]['value'])

    timestamp=int(jres['detailedExecutionInfo']['submittedAt']/1000)
    data=weight(data, timestamp)
    split(data)
    safe_data=pd.DataFrame({'address': pd.Series(addresses_list), 'share': pd.to_numeric(pd.Series(percentage_list), errors='coerce', downcast='integer')}).sort_values('share', ascending=False, ignore_index=True)


    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        comp=(safe_data['share'].compare(data['split']).rename(columns={'self': 'Safe tx', 'other': 'Local'}, level=-1))
        print(comp)

## TODO show more detailed comparison, validate individual addresses

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Calculate PG members weights')
    parser.add_argument('--percent', action='store_true', help='Only print the member\'s address and current percentage. (default)')
    parser.add_argument('--splits', action='store_true', help='Print and write output for Split update')
    parser.add_argument('--safetx', type=str, help='Split update tx hash from Safe (multisig frontend) to verify')
    parser.add_argument('--input_file', type=str, help='Input file with member data (default: ./members.csv)')
    parser.add_argument('--v2', action='store_true', help='Point to PGv2 contracts (default)')
    parser.add_argument('--v1', action='store_true', help='Point to PGv1 contracts')

    args = parser.parse_args()

    if args.input_file:
       input_file=args.input_file
    else:
        input_file='members.csv'

    if os.path.exists(input_file):
        data = membership(input_file)
        n = len(data) 
        if os.path.exists('output.csv'):
            data_old = membership('output.csv')
            if n > len(data_old):
                print(n-len(data_old), "members added")
    else: 
        print("Missing input file")
        quit()

    if args.splits:
        current_time = int(time.time())
        data=weight(data, current_time)
        split(data)
        for index, member in data.iterrows():
            print(f"{member['address']},{int(member['split'])}")
    elif args.safetx:
        safe_tx(args.safetx, data)
    else:
        current_time = int(time.time())
        data = weight(data, current_time)
        percentage(data)
        print("Members:", n)
        for index, member in data.iterrows():
            print(f"{member['address']}: {member['percentage']:.4f}%")
