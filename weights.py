import pandas as pd
import time
from math import sqrt
import os
import argparse

# DAO 0x412a32DD71357bD12337F4408168DF903F90CBD3
# Multisig 0x3250c2CEE20FA34D1c4F68eAA87E53512e95A62a
# Split 0xd4ad8daba9ee5ef16bb931d1cbe63fb9e102ec10
# Splits main 0x2ed6c4B5dA6378c7897AC67Ba9e43102Feb694EE

# Load file with all members
def membership(path):
    if os.path.exists(path):
        csv = pd.read_csv(path)
        data = csv[['address', 'start_timestamp', 'weight', 'break_months']]
        return data

def weight(data):
    current_time = int(time.time())
    n = len(data)
    
    shares = []  
    for i in range(n):
        active_seconds = (current_time - data['start_timestamp'].iloc[i]) -  data['break_months'].iloc[i] * 2629800
        activity_multiplier =  int(data['weight'].iloc[i] * active_seconds / (current_time - data['start_timestamp'].iloc[i]))

        share = sqrt((current_time - data['start_timestamp'].iloc[i]) * activity_multiplier / 100)
        shares.append(share)
    
    data['share'] = shares

def percentage(data):
    total_shares = sum(data['share'])
    data['percentage'] = (data['share'] / total_shares) * 100

if __name__ == "__main__":
    file_path = "./members.csv"
    data = membership(file_path)
    n = len(data)
    print("Members:", n)
    
    weight(data)
    percentage(data)
    
    parser = argparse.ArgumentParser(description='Calculate PG members weights')
    parser.add_argument('--splits', action='store_true', help='Print output for Split update')
    parser.add_argument('--percent', action='store_true', help='Print just the member\'s name and percentage. (default)')
    args = parser.parse_args()


    if args.splits:
        for index, member in data.iterrows():
            print(f"{member['address']},{int(member['percentage']*10000)}")
    else:
        for index, member in data.iterrows():
            print(f"{member['address']}: {member['percentage']:.4f}%")
