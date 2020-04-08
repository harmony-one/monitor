### Mini Explorer
Generates latest block logs

#### Requirements
`python3 -m pip install requests`

#### Commands
Run command:
`python3 mini_explorer.py --endpoints [https://api.s0.b.hmny.io,...] --output_file [filename]`
Output file will be created in the `./data` directory.

To pass in a file with endpoints, use the following instead of `--endpoints`:
`--endpoint_file path/to/file `

To run on Mainnet (networks without staking enabled), use `--no_staking`.

#### Output
```
./data/*
```
