#import libraries - csv


#portfolio creation
def run_sim(n):
    print("run sim")
    #create n number of policyholders, each with policies and claims
    for x in range(n):
        print("Running Policyholder: " + str(x))
        #Create policyholder and transaction
        output()


#init and setup files
def init():
    print("Run init")
    #configure and create files
    #setup agents, products etc.


#output stuff
def output():
    print("Output policyholder info.")


#housekeeping stuff
def housekeep():
    print("Run housekeeping")
    #close files


#declare variables
num_ph = 10
ph_filename = "policyholders.csv"
claims_filename="claims.csv"
policies_filename="policies.csv"
print("Completed initiating variables")

#run simulator
init()
run_sim(num_ph)
housekeep()