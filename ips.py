#import libraries - csv


#Policyholder class
class Policyholder:
    
    def __init__(self):
        #create policyholder data
        self.id="P0001" #Pxxxx
        self.gender="M" #M, F
        self.dob="19990101" #YYYYMMDD
        self.smoker="Y" #Y, N
        self.uw_status="standard" # standard, substandard
        self.fab="Y" #Y, N - Fab is a healthy lifestyle programme

    
    def print_details(self):
        details = (self.id, self.gender, self.dob, self.smoker, self.uw_status, self.fab)
        print(("; ").join(details))

    def run_transactions(self):
        print("Create policy and claim transactions")


#portfolio creation
def run_sim(n):
    print("run sim")
    #create n number of policyholders, each with policies and claims
    for x in range(n):
        print("Running Policyholder: " + str(x))
        #Create policyholder and transaction
        ph=Policyholder()
        ph.print_details()
        ph.run_transactions()
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
clm_filename="claims.csv"
pol_filename="policies.csv"
chn_filename="channels_csv"
print("Completed initiating variables")

#run simulator
init()
run_sim(num_ph)
housekeep()