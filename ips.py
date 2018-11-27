#import libraries - csv


#declare variables
num_ph = 10
ph_filename = "policyholders.csv"
clm_filename="claims.csv"
pol_filename="policies.csv"
chn_filename="channels.csv"
pd_filename="products.csv"
all_files=[]
file_handles=[]
all_prod=[]
all_ch=[]
 
#Policy class
class Policy:
    def __init__(self, id, policy_start, policy_end, product_id, channel_id, sum_assured, claims, status):
        #create policy with id, start date, end date, status
        self.id=id #unique id of policy sold. Eg PL001
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
        details = (self.id, self.policy_start, self.policy_end, self.product_id, self.channel_id, self.status)
        pol_line=(", ").join(details)
        print(pol_line)
        pol_file_handle.writelines(pol_line)
        pol_file_handle.write("\n")
        #output claims!
        for cl in self.claims:
            cl.output_details(clm_file_handle)


#Claim class
class Claim:
    def __init__(self, id, policy_id, claim_amount, claim_reason):
        self.id=id
        self.policy_id=policy_id
        self.claim_amount = claim_amount #should be based on sum assured
        self.claim_reason = claim_reason #should be based product risk/conditions covered
    
    def print_header(file_handle):
        file_handle.write("Claim_ID, Policy_ID, Claim_Amount, Claim_Reason\n")

    def output_details(self, file_handle):
        details = (self.id, self.policy_id, str(self.claim_amount), self.claim_reason)
        cl_line=(", ").join(details)
        print(cl_line)
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
        all_prod=[p1, p2, p3, p4]
        
        for p in all_prod:
            file_handle.write(",".join([str(p.id), str(p.name)]))
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
        all_ch=[c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]

        #create agency channel
        #1000 agents for agency
        for i in range(11,1111):
            i_length = len(str(i))
            all_ch.append(Channel( "CH" + "0"*(4-i_length) + str(i) , "Agency" , "Agent " + str(i)))
        
        for c in all_ch:
            file_handle.write(", ".join([str(c.id), c.type, c.name]))
            file_handle.write("\n")

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
    
    def output_details(self, file_handle):
        details = (self.id, self.gender, self.dob, self.smoker, self.uw_status, self.fab)
        ph_line=(", ").join(details)
        print(ph_line)
        file_handle.writelines(ph_line)
        file_handle.write("\n")

    def transact_sim(self):
        #purchase k number of policies. Currently only have 4 products.
        num_policies = 3
        ph_pols=[]
        #for policy created, identify channel, product, then claims
        for x in range(num_policies):
            print("create policy with product, agent, policy start date, term")
            pol = Policy("PL001", "20101010", "20151009", "PD001", "CH0011", 100000, [], "")
            print("Housekeep - add to list of policies")
            ph_pols.append(pol)


        #decide what happens to policyholder (ie. dies, claims, lapses)
        #then update policy files to reflect status
        ph_pols[0].status="Lapse"
        ph_pols[1].status="Claim"
        ph_pols[1].claims.append(Claim("CL0001", ph_pols[1].id, ph_pols[1].sum_assured, "Death"))
        ph_pols[2].status="Mature"

        #output to policy.csv file
        for p in ph_pols:
                p.output_details(file_handles[2], file_handles[1])
    
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
        ph.run_transactions()
        #ouput details
        ph.output_details(file_handles[0])


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
    Claim.print_header(file_handles[1])
    Product.print_header(file_handles[4])
    
    #setup products, channels etc.
    Product.setup_products(file_handles[4])
    Channel.setup_channels(file_handles[3])
    

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