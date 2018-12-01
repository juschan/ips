#import libraries
import random
import numpy as np
import datetime
from datetime import date

#declare global variables
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
# Have 10 years of simulated time - simulate for the period 2007-1-1 till 2017-12-31
total_days = 366*3 + 365*7 # 3 leap years (2008, 2012, 2016) and 7 non-leap
sim_end_date = date(2017,12,31) #simulation end date
dob_start = 25*365
dob_end = 45*365

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
    return np.random.randint(low=1, high=10, size=1)*50000

def gen_dob_at_date(at_date):
    days_lived_at_date = np.random.randint(dob_start, dob_end)
    return at_date - datetime.timedelta(days=days_lived_at_date)

def random_date(start, end):
    return start + datetime.timedelta( days=random.randint(0,(end-start).days))

def add_years(d, years):
    try:
        return d.replace(year=d.year+years)
    except ValueError:
        return d+(date(d.year + years, 1, 1) - date(d.year, 1,1))

def gen_num_policies(first_policy_date, last_survival_date):
    #generate Poisson sample, 1 policy every three years (0.5 per 365 days)
    return np.random.poisson(((0.33/365) * (last_survival_date - first_policy_date ).days), 1)[0]

def test_if_repeat_Hosp(ph, pd, ph_pols):
    #get last bought product
    last_pd = ph_pols[len(ph_pols)-1]
    if pd.id=="PD004" and last_pd.id == pd.id:
        #can only buy if there's one year from last product
        if last_pd.policy_end_date < ph.last_survival_date:
            return True
    return False



#Policy class
class Policy:
    def __init__(self, policy_start, policy_end, policyholder_id, product_id, channel_id, sum_assured, claims, status):
        #create policy with id, start date, end date, status
        self.id=gen_policy_id() #unique id of policy sold. Eg PL001
        self.policy_start=policy_start
        self.policy_end=policy_end
        self.policyholder_id = policyholder_id
        self.product_id=product_id #product ID
        self.channel_id=channel_id #channel ID
        self.sum_assured=sum_assured
        self.claims=claims #list of claims
        self.status=status #Active, Mature, Lapse, Death Maturity, Claim Maturity
         
    def print_header(file_handle):
        file_handle.write("Policy_ID, Policy_Start, Policy_End, Policyholder_ID, Product_ID, Channel_ID, Status\n")

    def output_details(self, pol_file_handle, clm_file_handle):
        #output to policy.csv
        details = (self.id, self.policy_start.isoformat(), self.policy_end.isoformat(), self.policyholder_id, self.product_id, self.channel_id, self.status)
        pol_line=(", ").join(details)
        pol_file_handle.writelines(pol_line)
        pol_file_handle.write("\n")
        #output claims!
        for cl in self.claims:
            cl.output_details(clm_file_handle)

    def gen_policies(ph, num_policies):

        ph_pols=[]
        last_channel = None
        last_product = None
 
        #generate num_policies
        for x in range(num_policies):
            pd=None
            #generate product. Tend to re-purchase Hosp
            if last_product != None and last_product.id == "PD004":
                    global all_prod
                    prod_choice = all_prod.copy()
                    prod_choice.append(all_prod[3])
                    prod_choice.append(all_prod[3])
                    pd = random.choice(prod_choice)
            else:
                pd=random.choice(all_prod)
            
            if x==0: #first policy bought
                policy_start_date=ph.first_policy_date
                ch=Channel.gen_ch()
            else: #subsequent policies
                #if last policy bought was Hosp, then can only buy one year later
                #if not enough remaining time, choose another product
                if test_if_repeat_Hosp(ph, pd, ph_pols):
                    policy_start_date = last_product.policy_end + datetime.timedelta(days=1)
                else:
                    prod_choice = all_prod.copy()
                    del prod_choice[3]
                    pd= random.choice(prod_choice)
                    policy_start_date = random_date(ph.first_policy_date, ph.last_survival_date)
                ch=random.choice([last_channel, last_channel, Channel.gen_ch()] ) #higher chance of buying from last channel

            last_channel=ch
            last_product = pd
            
            #generate term
            term = random.randint(pd.min_term, pd.max_term)

            if (pd.id=="PD002"): #whole of life
                policy_end_date = date(9999,12,31)
            else:
                policy_end_date = add_years(policy_start_date, random.randint(pd.min_term, pd.max_term))

            #create policy object and add to ph_pols
            pol=Policy(policy_start_date, policy_end_date - datetime.timedelta(days=1), ph.id, pd.id, ch.id, gen_sa(), [], "Active")
            ph_pols.append(pol)

        #generate claims

        return ph_pols

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

    def gen_claims(self):
        return  []


#Product class
class Product:

    def __init__(self, id, name, min_term, max_term):
        self.id=id #id of product. Eg. PD001
        self.name=name #name of product. Eg. Term Life
        self.min_term = min_term
        self.max_term = max_term

    def print_header(file_handle): #no need 'self' argument. This is a class function
        file_handle.write("Product_ID, Product_Name, Min_Term, Max_Term\n")

    #setup products - class function
    def setup_products(file_handle):
        #create multiple products default templates
        p1=Product("PD001", "Term Life", 3, 25)
        p2=Product("PD002", "Whole of Life", 9999, 9999)
        p3=Product("PD003", "Standalone Critical Illness", 5, 25)
        p4=Product("PD004", "Hospitalization", 1, 1)
        
        global all_prod
        all_prod=[p1, p2, p3, p4]
        
        for p in all_prod:
            file_handle.write(",".join([str(p.id), str(p.name), str(p.min_term), str(p.max_term)]))
            file_handle.write("\n")

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
        
    def gen_ch():
        global all_ch
        ch=random.choice(all_ch)
        return ch

#Policyholder class
class Policyholder:
    
    def __init__(self):
        #create policyholder data
        global sim_end_date
        self.id=gen_ph_id() #PHxxxxxxx
        self.gender=random.choice("MMMFF") #M, F
        self.dob=None #date(1999,1,1) #YYYY-MM-DD
        self.smoker=random.choice("YNNNN") #Y, N
        self.uw_status= get_uw_status() # standard, substandard
        self.fab=random.choice("YN") #Y, N - Fab is a healthy lifestyle programme
        self.first_policy_date="" #start date of first policy purchased
        self.last_survival_date=sim_end_date
        self.policies=[]

    def print_header(file_handle):
        file_handle.write(",".join(["Policyholder_ID", "Gender", "DOB", "Smoker", "UW_Status", "Fab", "Last_Survival_Date", "First_Policy_Date"]))
        file_handle.write("\n")
    
    def output_details(self, file_handle):
        details = (self.id, self.gender, self.dob.isoformat(), self.smoker, self.uw_status, self.fab, self.last_survival_date.isoformat(), self.first_policy_date.isoformat())
        ph_line=(", ").join(details)
        file_handle.writelines(ph_line)
        file_handle.write("\n")

    def get_last_survival_date(self):
        global sim_end_date
        #write function to determine this, based on p/h characteristics
        #return random.choice(sim_end_date, date(2016,4,3))  

        return sim_end_date

    #if died during simulation, adjust the policies
    def death_adjustment(self):
        if self.last_survival_date != sim_end_date:
            for pol in self.policies:
                if pol.status == "Active": pol.status="Death Maturity"
                
        

    def transact_sim(self):
        #create first policy start date
        self.first_policy_date = sim_end_date - datetime.timedelta(days=np.random.randint(1, total_days))

        #generate birthday at first policy start date
        self.dob = gen_dob_at_date(self.first_policy_date)

        #determine if p/h dies between first policy start and sim end date. If so, determine when.
        self.get_last_survival_date()

        #Generate num_policies number of policies.
        num_policies = gen_num_policies(self.first_policy_date, self.last_survival_date)

        #Generate policies.
        self.policies=Policy.gen_policies(self, num_policies)

        self.death_adjustment()

        #output to policy.csv file
        for p in self.policies:
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


#init files, random seed etc.
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