# IPS
Insurance Portfolio Simulator

### Description
A Python program that simulates an insurance portfolio by creating policyholders, policies, claims, channels and products.
The results are output in csv format.

IPS is programmed using an object-oriented approach. Channels and products are first set up, before generating policyholders which purchase policies, that may eventually lead to claims (or some other decrement).
IPS has a relational data aspect, with the creation of primary and foreign keys, to allow for the consistent data model using the csv files.


### Technology
Requires Python 3.6


### Running the program
Specify the number of policyholders by changing the variable, num_ph.
Type the following in the command line to run the programme:

    python ips.py

This would create several csv files - policyholders.csv, policies.csv, claims.csv, channels.csv and products.csv.

### Next steps
* Refactor the code for a cleaner separation between simulation and the various objects
* Consider removing 'status' for Policyholder as it appears redundant
* DRY refactoring for similar functions
* Ship a released version inline with the set of RIP data
* Produce documentation for the simulator