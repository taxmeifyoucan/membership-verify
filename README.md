# Split verification

WIP Calculates current shares of PG members to verify Split allocations and Safe transaction.

## Usage

The script calculates member shares based on csv input with addresses, start dates, time off and multiplier. 

The default output shows percentage allocations for members at the current moment. It can also output it in format for updating the split. 

Another feature is validating proposed multisig transactions for split update/creation. Multisig signers or DAO members can input tx hash from Safe UI, the script validates it's interacting with correct contracts and calculates weights at the time of tx submission for comparison. 

Run using python: 

```
python3 weights.py --help

usage: weights.py [-h] [--percent] [--splits] [--safetx SAFETX] [--input_file INPUT_FILE] [--v2] [--v1]

Calculate PG members weights

options:
  -h, --help            show this help message and exit
  --percent             Only print the member's address and current percentage. (default)
  --splits              Print and write output for Split update
  --safetx SAFETX       Split update tx hash from Safe (multisig frontend) to verify
  --input_file INPUT_FILE  Input file with member data (default: ./members.csv)
  --v2                  Point to PGv2 contracts (default)
  --v1                  Point to PGv1 contracts
```

For example, verify a proposed Safe transaction to update/create the Split:
```
python3 weights.py --safetx 720d4add65156a612019f8aff2a2269d70776bf557dcd8aa393d7e1ace5b6dbe  

Percentual differences between local calculation and Safe tx:
                                         address  % diff
0    0x83ec0B504650C35320a04F4dc714b36cbd889081  0.0048
1    0x9Bee5b17Eb847744b6a81Ee935409739F91c722c  0.0059
2    0x974B9cb3c122561e3bf6234651E0b82B88Fb9015  0.0019
3    0x19d2e56df1133D262D3381d50418Bfc60a86c327  0.0018
4    0x69f4b27882eD6dc39E820acFc08C3d14f8e98a99 -0.0011
5    0x28672015d230e554453024e469fbd3bfd26dd2de  0.0039
...
```

### TODO

- Validate executed updateSplit transactions based on onchain data
- Add more checks, handle edge cases
- Rounding errors 
- Website hosting? api? 