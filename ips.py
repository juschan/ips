#import libraries - csv


#declare variables
num_ph = 10
ph_filename = "policyholders.csv"
clm_filename="claims.csv"
pol_filename="policies.csv"
chn_filename="channels_csv"
pd_filename="products.csv"
all_files=[]
file_handles=[]
all_prod=[]

#Policy class
class Policy:
    def __init__(self, id):
        #create policy with id, start date, end date, status
        self.id=id #unique id of policy sold. Eg PL001
        self.policy_start="20101010"
        self.policy_end="20151009"
        self.status="Lapse"
        self.product="PD001" #product ID

    def print_header(file_handle):
        file_handle.write("ID, Policy_Start, Policy_End, Product_ID,Status\n")


#Product class
class Product:

    def __init__(self, id, name):
        self.id=id #id of product. Eg. PD001
        self.name=name #name of product. Eg. Term Life

    def print_header(file_handle):
        file_handle.write("Product_ID, Name\n")

#Policyholder class
class Policyholder:
    
    def __init__(self):
        #create policyholder data
        self.id="PH0001" #Pxxxx
        self.gender="M" #M, F
        self.dob="19990101" #YYYYMMDD
        self.smoker="Y" #Y, N
        self.uw_status="standard" # standard, substandard
        self.fab="Y" #Y, N - Fab is a healthy lifestyle programme
        self.first_policy_date="" #start date of first policy purchased

    def print_header(file_handle):
        file_handle.write(",".join(["Policyholder_ID", "Gender", "DOB", "Smoker", "UW_Status", "Fab"]))
        file_handle.write("\n")
    
    def output_details(self):
        details = (self.id, self.gender, self.dob, self.smoker, self.uw_status, self.fab)
        ph_line=(", ").join(details)
        print(ph_line)
        file_handles[0].writelines(ph_line)
        file_handles[0].write("\n")

    def transact_sim(self):
        #purchase k number of policies. Currently only have 4 products.
        num_policies = 3 
        #for policy created, identify channel, product, then claims
        for x in range(3):
            print("create policy with product, agent, policy start date, term")
            print("determine if claimed")
    
    def run_transactions(self):
        print("Create policy and claim transactions")
        self.transact_sim()

    

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


#init files
def init():
    print("Run init")
    #configure and create files
    all_files=[ph_filename, clm_filename, pol_filename, chn_filename, pd_filename]
    for f in all_files:
        output=open(f, 'w')
        file_handles.append(output)
    print("init files: " + str(file_handles))

    #print headers
    Policyholder.print_header(file_handles[0])
    Policy.print_header(file_handles[2])
    Product.print_header(file_handles[4])
    #setup agents, products etc.
    setup_products()


#setup products:
def setup_products():
    #create multiple products default templates
    p1=Product("PD001", "Term Life")
    p2=Product("PD002", "Whole of Life")
    p3=Product("PD003", "Standalone Critical Illness")
    p4=Product("PD004", "Hospitalization")
    all_prod=[p1, p2, p3, p4]
       
    for p in all_prod:
        file_handles[4].write(",".join([str(p.id), str(p.name)]))
        file_handles[4].write("\n")

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