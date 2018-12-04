# ips
Insurance Portfolio Simulator

### Description
This Python seeks to create a simulate an insurance portfolio by creating policyholders, policies, claims, channels and products.
The results are output in csv format.

The program is programmed with an object-oriented approach. Channels and products are first set up, before generating policyholders which purchase policies, that may eventually lead to claims (or some other decrement).
It also has a relational data aspect, with the creation of primary and foreign keys, to allow for the consistent data model using the csv files.


### Technology
Requires Python 3.6


### Running the program
Specify the number of policyholders by changing the variable, num_ph.
Type the following in the command line to run the programme:

    python ips.py

This would create several csv files - policyholders.csv, policies.csv, claims.csv, channels.csv and products.csv.
