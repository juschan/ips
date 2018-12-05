#import libraries
import random
import numpy as np
import datetime
from datetime import date
import math
from dateutil.relativedelta import relativedelta

#declare global variables
num_ph = 10000
avg_pol = 0.33 #average policies bought per year.
ph_filename, clm_filename, pol_filename, chn_filename, pd_filename = "policyholders.csv", "claims.csv", "policies.csv", "channels.csv", "products.csv"
all_files, file_handles, all_prod, all_ch=[], [], [], []
ph_id_count, pol_id_count, clm_id_count = 0, 0, 0
mortality_table, ci_table, hosp_table={}, {}, {}
lapse_rate=0.05
#assume mortality,ci and hosp rates for male non-smoker, standard, non-fab
mort_female = -0.1
mort_smoker= 0.15
mort_substandard = 5
mort_fab = -7
ci_female = 0.2
ci_smoker = 0.25
ci_substandard = 7
ci_fab = -3
hosp_female = 0.1
hosp_smoker = 0.1
hosp_substandard = 7
hosp_fab = -5

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
    global avg_pol
    num = np.random.poisson(((avg_pol/365) * (last_survival_date - first_policy_date ).days), 1)[0]
    return max(1, num)

def test_if_repeat_Hosp(ph, pd, ph_pols):
    #get last bought product
    last_pd = ph_pols[len(ph_pols)-1]
    if pd.id=="PD004" and last_pd.id == pd.id:
        #can only buy if there's one year from last product
        if last_pd.policy_end_date < ph.last_survival_date:
            return True
    return False

def gen_actuarial_tables():
    #mortality, ci and hosp tables, assume age last birthday
    global mortality_table
    global ci_table
    global hosp_table
    for x in range(17,100):
        qx = 0.0002 + math.exp(x/100) * 0.0005
        mortality_table[x] = qx
        
        kx = 0.003 + math.exp(x/100) * 0.005
        ci_table[x] = kx

        hosp_table[x] = kx * 0.1

def get_ci_rate(ph, dt):
    global ci_table
    #adjust for gender, smoker, uw_status, fab
    age_adj = 0
    if(ph.fab=="Y"): age_adj = ci_fab
    if(ph.uw_status=="substandard"): age_adj += ci_substandard
    
    age = age_last_birthday(ph.dob, dt) + age_adj
    ci_rate = ci_table[age]
    
    if(ph.gender=="F"): ci_rate *= (1+ci_female)
    if(ph.smoker=="Y"): ci_rate *= (1+ci_smoker)
      
    return ci_rate

def get_mort_rate(ph, dt):
    global mortality_table
    #adjust for gender, smoker, uw_status, fab
    age_adj = 0
    if(ph.fab=="Y"): age_adj = mort_fab
    if(ph.uw_status=="substandard"): age_adj += mort_substandard
    
    age = age_last_birthday(ph.dob, dt) + age_adj
    mort_rate = mortality_table[age]
    
    if(ph.gender=="F"): mort_rate *= (1+mort_female)
    if(ph.smoker=="Y"): mort_rate *= (1+mort_smoker)

    return mort_rate

def get_hosp_rate(ph, dt):
    global hosp_table
    #adjust for gender, smoker, uw_status, fab
    age_adj = 0
    if(ph.fab=="Y"): age_adj = hosp_fab
    if(ph.uw_status=="substandard"): age_adj += hosp_substandard
    
    age = age_last_birthday(ph.dob, dt) + age_adj
    hosp_rate = hosp_table[age]
    
    if(ph.gender=="F"): hosp_rate *= (1+hosp_female)
    if(ph.smoker=="Y"): hosp_rate *= (1+hosp_smoker)

    return hosp_rate

def age_last_birthday(dob, dt):
    #return complete years between dob and dt
    return relativedelta(dt, dob).years


def get_last_survival_date(ph):
    global sim_end_date
    global mortality_table
    #write function to determine this, based on p/h characteristics
    #loop through from first_policy_date each year to see if life dies. If life dies within that year, return as last_survival_date
    period_start=ph.first_policy_date
    period_end = period_start
    while (period_end < sim_end_date):
        period_end = add_years(period_start,1) - datetime.timedelta(days=1)
        if period_end > sim_end_date: 
            period_end = sim_end_date
        age = age_last_birthday(ph.dob, period_start)
        
        #died between period start and end?
        qx = get_mort_rate(ph, period_start)
        result=np.random.binomial(size=1, n=1, p=qx )
        if result==1:
            #If died, update last_survival_date and return
            ph.last_survival_date = period_start + datetime.timedelta( days=random.randint(0,(period_end- period_start).days))                
            return
        #didn't die, so repeat       
        period_start = period_end
    
    #outlive simulation period. Update last_survival_date as sim_end_date
    ph.last_survival_date = sim_end_date
    return

def is_between(start, end, at):
    #test if 'at' is between start and end dates.
    if (at >= start and at <= end):
        return True
    return False

def gen_hosp_claim_amt():
    return np.random.randint(low=2, high=50, size=1)*5000

def gen_hosp_claim_reason():
    conditions = ["Cancer", "Heart Attack", "Stroke", "Kidney Disease", "COPD", "Paralysis"]
    return random.choice(conditions)

def gen_ci_claim_reason():
    conditions = ["Cancer", "Heart Attack", "Stroke", "Kidney Disease", "COPD", "Paralysis", "Major Burns", "Major Organ Transplant", "Bacterial Meningitis"]
    return random.choice(conditions)

#Policy class
class Policy:
    def __init__(self, policy_start, policy_end, policyholder_id, product_id, channel_id, sum_assured, claims, status_date, status):
        #create policy with id, start date, end date, status
        self.id=gen_policy_id() #unique id of policy sold. Eg PL001
        self.policy_start=policy_start
        self.policy_end=policy_end
        self.policyholder_id = policyholder_id
        self.product_id=product_id #product ID
        self.channel_id=channel_id #channel ID
        self.sum_assured=sum_assured
        self.claims=claims #list of claims
        self.status_date=date.min
        self.status=status #Active, Mature, Lapse, Death Maturity, Claim Maturity

    @classmethod   
    def print_header(cls, file_handle):
        file_handle.write("Policy_ID, Policy_Start, Policy_End, Policyholder_ID, Product_ID, Channel_ID, Status\n")

    def output_details(self, pol_file_handle, clm_file_handle):
        #output to policy.csv
        details = (self.id, self.policy_start.isoformat(), self.policy_end.isoformat(), self.policyholder_id, self.product_id, self.channel_id, self.status_date.isoformat(), self.status)
        pol_line=(", ").join(details)
        pol_file_handle.writelines(pol_line)
        pol_file_handle.write("\n")
        #output claims!
        for cl in self.claims:
            cl.output_details(clm_file_handle)

    def display(self):
        return ("Policy: " + self.id + " has " + str(len(self.claims)) + " claims.")

    @classmethod
    def gen_policies(cls, ph, num_policies):

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
                policy_end_date = add_years(policy_start_date, term)

            #create policy object and add to ph_pols
            pol=Policy(policy_start_date, policy_end_date - datetime.timedelta(days=1), ph.id, pd.id, ch.id, gen_sa(), [], date.min, "Active")
            ph_pols.append(pol)
        
        return ph_pols
    
    @classmethod
    def gen_decrements(cls, ph):
        global ci_table
        global hosp_table
        ph_pols = []
        #adjust for death by removing policies starting after death
        for x in range(0, len(ph.policies)):
            p=ph.policies[x]
            if ph.last_survival_date > p.policy_start:
                ph_pols.append(p)
        
        ph.policies=ph_pols

        #for policies ending after death but starting before
        #check if term or wol -> test for lapse. Else trigger death claim
        for p in ph_pols:
            if p.product_id in ["PD001", "PD002","PD003"]:
                if (p.policy_end < ph.last_survival_date):
                    #test if lapse during this period
                    result=np.random.binomial(size=1, n=1, p=lapse_rate*((ph.last_survival_date - p.policy_end).days)/365.0)
                    if result==1:
                        #lapse!
                        p.status="Lapsed"
                        p.status_date=p.policy_start + datetime.timedelta( days=random.randint(0,(ph.last_survival_date-p.policy_end).days))
                    else: #did not lapse. So mature
                        p.status="Mature"
                        p.status_date = p.policy_end
                else:
                    #death claim
                    p.status="Death Claim"
                    p.status_date = ph.last_survival_date
                    p.claims.append(Claim(p.id, p.status_date, p.sum_assured, "Death Claim"))

        #ci or hospitalization policies
        #iterate through remaining policies for ci, lapse and hosp on period by period basis
        #Death claim for CI `covered in code above. No lapse for Hosp as premium paid in advance.
        period_start = ph.first_policy_date
        period_end = period_start
        while period_end < ph.last_survival_date:
            period_end = add_years(period_start,1) - datetime.timedelta(days=1)
            age=age_last_birthday(ph.dob, period_start)

            #Test if Hospitalization condition is triggered. 
            result=np.random.binomial(size=1, n=1, p=get_hosp_rate(ph, period_start) )
            if result==1:
                #iterate through all policies to see if there is an active hospitalization policy.
                for p in ph_pols:
                    hosp_claim_date = random_date(period_start, period_end)
                    if (p.product_id=="PD004" and is_between(p.policy_start, p.policy_end, hosp_claim_date)):
                        #create claim
                        p.claims.append(Claim(p.id, hosp_claim_date, gen_hosp_claim_amt() , gen_hosp_claim_reason()))
                        p.status="Hosp Claim"
                                
                        #80% this will trigger a CI claim:
                        if (random.choice("YYYYN")=="Y"):
                            for k in ph_pols:
                                if(p.product_id=="PD003" and p.status=="Active" and is_between(p.policy_start, p.policy_end, hosp_claim_date)):
                                    #trigger a ci claim
                                    p.claims.append(Claim(p.id, hosp_claim_date, p.sum_assured, gen_ci_claim_reason()))
                                    p.status="CI Claim Maturity"
                    

            #Test for CI condition - 20% of ci_table, given overlap with hospitalization
            ci_rate = get_ci_rate(ph, period_start)
            result=np.random.binomial(size=1, n=1, p=0.2*ci_rate)
            if result==1: 
                #iterate through all policies to see if there is an active ci policy.
                for p in ph_pols:
                    ci_claim_date = random_date(period_start, period_end)
                    if (p.product_id=="PD003" and p.status=="Active" and is_between(p.policy_start, p.policy_end, ci_claim_date)):
                        #create claim
                        p.claims.append(Claim(p.id, ci_claim_date, p.sum_assured, gen_ci_claim_reason()))
                        p.status("Claim Maturity")

            period_start = period_end + datetime.timedelta(days=1)
        return ph_pols 

#Claim class
class Claim:
    def __init__(self, policy_id, claim_date, claim_amount, claim_reason):
        self.id=gen_claim_id()
        self.policy_id=policy_id
        self.claim_date = claim_date
        self.claim_amount = claim_amount #should be based on sum assured
        self.claim_reason = claim_reason #should be based product risk/conditions covered
    
    @classmethod
    def print_header(cls, file_handle):
        file_handle.write("Claim_ID, Policy_ID, Claim_date, Claim_Amount, Claim_Reason\n")

    def output_details(self, file_handle):
        details = (self.id, self.policy_id, self.claim_date.isoformat(), str(self.claim_amount), self.claim_reason)
        cl_line=(", ").join(details)
        file_handle.writelines(cl_line)
        file_handle.write("\n")


#Product class
class Product:

    def __init__(self, id, name, min_term, max_term):
        self.id=id #id of product. Eg. PD001
        self.name=name #name of product. Eg. Term Life
        self.min_term = min_term
        self.max_term = max_term

    @classmethod
    def print_header(cls, file_handle): #no need 'self' argument. This is a class function
        file_handle.write("Product_ID, Product_Name, Min_Term, Max_Term\n")

    #setup products - class function
    @classmethod
    def setup_products(cls, file_handle):
        #create multiple products default templates
        p1=Product("PD001", "Term Life", 3, 25)
        p2=Product("PD002", "Whole of Life", 9999, 9999)
        p3=Product("PD003", "Accelerated Critical Illness", 5, 25)
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

    @classmethod
    def print_header(cls, file_handle): #no need 'self' argument. This is a class function
        file_handle.write("Channel_ID, Channel_Type, Channel_Name\n")

    #setup channels - class function
    @classmethod
    def setup_channels(cls, file_handle):
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

    @classmethod  
    def gen_ch(cls):
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

    @classmethod
    def print_header(cls, file_handle):
        file_handle.write(",".join(["Policyholder_ID", "Gender", "DOB", "Smoker", "UW_Status", "Fab", "Last_Survival_Date", "First_Policy_Date"]))
        file_handle.write("\n")
    
    def output_details(self, file_handle):
        details = (self.id, self.gender, self.dob.isoformat(), self.smoker, self.uw_status, self.fab, self.last_survival_date.isoformat(), self.first_policy_date.isoformat())
        ph_line=(", ").join(details)
        file_handle.writelines(ph_line)
        file_handle.write("\n")

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
        get_last_survival_date(self)

        #Generate num_policies number of policies.
        num_policies = gen_num_policies(self.first_policy_date, self.last_survival_date)

        #Generate policies.
        self.policies=Policy.gen_policies(self, num_policies)
        self.policies=Policy.gen_decrements(self)

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

    #generate actuarial tablaes
    gen_actuarial_tables()

#housekeeping stuff
def housekeep():
    #close files
    for f in file_handles:
        f.close()

#run simulator
init()
run_sim(num_ph)
housekeep()