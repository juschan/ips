#import libraries - csv
import random
import numpy as np
from datetime import date

#declare variables
num_ph = 10
avg_pol = 3 #average number of policies per policyholder
ph_filename="policyholders.csv"
clm_filename="claims.csv"
pol_filename="policies.csv"
chn_filename="channels.csv"
pd_filename="products.csv"
all_files=[]
file_handles=[]
all_prod=[]
all_ch=[]
ph_id_count=0
pol_id_count=0
clm_id_count=0

# Date-related simulation variables
# Use ISO-8601 date-time standard. YYYY-MM-DD
# Have 10 years of simulated time - simulate for the period 2007/1/1 till 2017/12/31
total_days = 366*3 + 365*7 # 3 leap years (2008, 2012, 2016) and 7 non-leap
sim_end_date = date(2017,12,31) #simulation end date


#utility functions
def get_uw_status():
    result=np.random.binomial(size=1, n=1, p=0.7)
    if result==1:
        return "standard"
    return "substandard"

def gen_ph_id():
    max_len=len(str(num_ph))
    global ph_id_count
    ph_id_count= ph_id_count+1
    return "PH" + "0"*(max_len-len(str(ph_id_count))) + str(ph_id_count) 

def gen_policy_id():
    max_len=len(str(num_ph * avg_pol))
    global pol_id_count
    pol_id_count=pol_id_count+1
    return "PL" + "0"*(max_len-len(str(pol_id_count))) + str(pol_id_count)   

def gen_claim_id():
    max_len=len(str(num_ph * avg_pol))
    global clm_id_count
    clm_id_count=clm_id_count+1
    return "CL" + "0"*(max_len-len(str(clm_id_count))) + str(clm_id_count)

def gen_sa(): #generate random sum assured
    return np.random.randint()*50000

#Policy class
class Policy:
    def __init__(self, policy_start, policy_end, product_id, channel_id, sum_assured, claims, status):
        #create policy with id, start date, end date, status
        self.id=gen_policy_id() #unique id of policy sold. Eg PL001
        self.policy_start=policy_start
        self.policy_end=policy_end
        self.product_id=product_id #product ID
        self.channel_id=channel_id #channel ID
        self.sum_assured=sum_assured
        self.claims=claims #list of claims
        self.status=status
        
        
    def print_header(file_handle):
        file_handle.write("Policy_ID, Policy_Start, Policy_End, Product_ID, Channel_ID, Status\n")

    def output_details(self, pol_file_handle, clm_file_handle):
        #output to policy.csv
        details = (self.id, self.policy_start.isoformat(), self.policy_end.isoformat(), self.product_id, self.channel_id, self.status)
        pol_line=(", ").join(details)
        pol_file_handle.writelines(pol_line)
        pol_file_handle.write("\n")
        #output claims!
        for cl in self.claims:
            cl.output_details(clm_file_handle)


#Claim class
class Claim:
    def __init__(self, policy_id, claim_amount, claim_reason):
        self.id=gen_claim_id()
        self.policy_id=policy_id
        self.claim_amount = claim_amount #should be based on sum assured
        self.claim_reason = claim_reason #should be based product risk/conditions covered
    
    def print_header(file_handle):
        file_handle.write("Claim_ID, Policy_ID, Claim_Amount, Claim_Reason\n")

    def output_details(self, file_handle):
        details = (self.id, self.policy_id, str(self.claim_amount), self.claim_reason)
        cl_line=(", ").join(details)
        file_handle.writelines(cl_line)
        file_handle.write("\n")

#Product class
class Product:

    def __init__(self, id, name):
        self.id=id #id of product. Eg. PD001
        self.name=name #name of product. Eg. Term Life

    def print_header(file_handle): #no need 'self' argument. This is a class function
        file_handle.write("Product_ID, Product_Name\n")

    #setup products - class function
    def setup_products(file_handle):
        #create multiple products default templates
        p1=Product("PD001", "Term Life")
        p2=Product("PD002", "Whole of Life")
        p3=Product("PD003", "Standalone Critical Illness")
        p4=Product("PD004", "Hospitalization")
        
        global all_prod
        all_prod=[p1, p2, p3, p4]
        
        for p in all_prod:
            file_handle.write(",".join([str(p.id), str(p.name)]))
            file_handle.write("\n")

    def gen_pd_id():
        global all_prod
        prod=random.choice(all_prod)
        return prod.id

#Channel class
class Channel:

    def __init__(self, id, type, name):
        self.id=id #id of channel. Eg CH1 for bank, CH2 for IFA, CH3 for Agent
        self.type = type # channel type. Bank, IFA, Agency
        self.name=name #channel name. Bank, IFA, Agent

    def print_header(file_handle): #no need 'self' argument. This is a class function
        file_handle.write("Channel_ID, Channel_Type, Channel_Name\n")

    #setup channels - class function
    def setup_channels(file_handle):
        #create multiple products default templates
        c1=Channel("CH0001", "Bank", "ABC Bank, Branch 1")
        c2=Channel("CH0002", "Bank", "ABC Bank, Branch 2")
        c3=Channel("CH0003", "Bank", "ABC Bank, Branch 3")
        c4=Channel("CH0004", "Bank", "XYZ Bank, Branch 1")
        c5=Channel("CH0005", "Bank", "XYZ Bank, Branch 2")
        c6=Channel("CH0006", "Bank", "XYZ Bank, Branch 3")
        c7=Channel("CH0007", "IFA", "IFA 1")
        c8=Channel("CH0008", "IFA", "IFA 2")
        c9=Channel("CH0009", "IFA", "IFA 3")
        c10=Channel("CH0010", "IFA", "IFA 4")

        #Add Bank and IFA
        global all_ch
        all_ch=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]

        #create agency channel
        #1000 agents for agency
        for i in range(11,1111):
            i_length = len(str(i))
            all_ch.append(Channel( "CH" + "0"*(4-i_length) + str(i) , "Agency" , "Agent " + str(i)))

        for c in all_ch:
            file_handle.write(", ".join([str(c.id), c.type, c.name]))
            file_handle.write("\n")
        
    def gen_ch_id():
        global all_ch
        ch=random.choice(all_ch)
        return ch.id

#Policyholder class
class Policyholder:
    
    def __init__(self):
        #create policyholder data
        self.id=gen_ph_id() #PHxxxxxxx
        self.gender=random.choice("MMMFF") #M, F
        self.dob=date(1999,1,1) #YYYY-MM/-D
        self.smoker=random.choice("YNNNN") #Y, N
        self.uw_status= get_uw_status() # standard, substandard
        self.fab=random.choice("YN") #Y, N - Fab is a healthy lifestyle programme
        self.first_policy_date="" #start date of first policy purchased
        self.policies=[]

    def print_header(file_handle):
        file_handle.write(",".join(["Policyholder_ID", "Gender", "DOB", "Smoker", "UW_Status", "Fab", "First_Policy_Date"]))
        file_handle.write("\n")
    
    def output_details(self, file_handle):
        details = (self.id, self.gender, self.dob.isoformat(), self.smoker, self.uw_status, self.fab, self.first_policy_date.isoformat())
        ph_line=(", ").join(details)
        file_handle.writelines(ph_line)
        file_handle.write("\n")
    
    def update_policies(self, ph_pols):
        self.policies=ph_pols
        #update first_policy_date
        all_dates = []
        for k in ph_pols:
            all_dates.append(k.policy_start)
        all_dates.sort()
        self.first_policy_date=all_dates[0]

    def transact_sim(self):
        #purchase k number of policies. Currently only have 4 products.
        num_policies = 3
        ph_pols=[]
        #for policy created, identify channel, product, then claims
        for x in range(num_policies):
            pol = Policy(date(2010,10,10), date(2015,10,9), Product.gen_pd_id(), Channel.gen_ch_id(), gen_sa, [], "")
            ph_pols.append(pol)

        self.update_policies(ph_pols)

        #decide what happens to policyholder (ie. dies, claims, lapses)
        #then update policy files to reflect status
        ph_pols[0].status="Lapse"
        ph_pols[1].status="Claim"
        ph_pols[1].claims.append(Claim( ph_pols[1].id, ph_pols[1].sum_assured, "Death"))
        ph_pols[2].status="Mature"

        #update policyholder variable first_policy_date
        self.update_policies(ph_pols)

        #output to policy.csv file
        for p in ph_pols:
                p.output_details(file_handles[2], file_handles[1])
    

#portfolio creation
def run_sim(n):
    global file_handles
    #create n number of policyholders, each with policies and claims
    for x in range(n):
        #Create policyholder
        ph=Policyholder()
        #Simulate transactions (ie. policy purchase, claims etc.)
        ph.transact_sim()
        #ouput details
        ph.output_details(file_handles[0])


#init files
def init():
    #configure and create files
    global all_files
    global file_handles
    all_files=[ph_filename, clm_filename, pol_filename, chn_filename, pd_filename]
    for f in all_files:
        output=open(f, 'w')
        file_handles.append(output)

    #print headers
    Policyholder.print_header(file_handles[0])
    Policy.print_header(file_handles[2])
    Claim.print_header(file_handles[1])
    Product.print_header(file_handles[4])
    
    #setup products, channels etc.
    Product.setup_products(file_handles[4])
    Channel.setup_channels(file_handles[3])
    
    #setup random seed
    np.random.seed(1227)


#housekeeping stuff
def housekeep():
    #close files
    for f in file_handles:
        f.close()

#run simulator
init()
run_sim(num_ph)
housekeep()