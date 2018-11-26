#import libraries - csv


#declare variables
num_ph = 10
ph_filename = "policyholders.csv"
clm_filename="claims.csv"
pol_filename="policies.csv"
chn_filename="channels_csv"
all_files=[]
file_handles=[]

#Policyholder classf
class Policyholder:
    
    def __init__(self):
        #create policyholder data
        self.id="P0001" #Pxxxx
        self.gender="M" #M, F
        self.dob="19990101" #YYYYMMDD
        self.smoker="Y" #Y, N
        self.uw_status="standard" # standard, substandard
        self.fab="Y" #Y, N - Fab is a healthy lifestyle programme

    def print_header():
        print(",".join("ID", "Gender", "DOB", "Smoker", "UW_Status", "Fab"))
    
    def output_details(self):
        details = (self.id, self.gender, self.dob, self.smoker, self.uw_status, self.fab)
        ph_line=(", ").join(details)
        print(ph_line)
        file_handles[0].writelines(ph_line)

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
        ph.output_details()
        ph.run_transactions()

#init and setup files
def init():
    print("Run init")
    #configure and create files
    all_files=[ph_filename, clm_filename, pol_filename, chn_filename]
    for f in all_files:
        output=open(f, 'w')
        file_handles.append(output)
    print("init files: " + str(file_handles))
    #setup agents, products etc.


#housekeeping stuff
def housekeep():
    print("Run housekeeping")
    #close files
    for f in file_handles:
        f.close()
    print("Completed housekeeping - closed all opened files")


#run simulator
init()
run_sim(num_ph)
housekeep()