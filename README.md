# pg-members

Calculate current shares of PG members and verify the Split. 

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

### TODO

- Validate executed updateSplit transactions based on logged events 
- Add more checks, address validation 
- Website hosting? api? 