#!/usr/bin/env python3

from ciscoisesdk import IdentityServicesEngineAPI
from ciscoisesdk.exceptions import  ApiError
from datetime import date
import argparse
import re
import texttable
import multiprocessing
from colorama import Fore
import sys

# used for date conversion for certificate expiration
MONTHS = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,
            "Sep":9,"Sept":9,"Oct":10,"Nov":11,"Dec":12}


# list of arguments and their function
parser=argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,allow_abbrev=False,description="ISE Certificate Import Tool")
parser.add_argument("-l",help="List all certificates. Required: -n, -u, and -p. Other options are ignored.",action="store_true")
parser.add_argument("-i",help="import certificate. Required: -n, -u, -p, -c, -f, and -k. Other options are ignored.",action="store_true")
parser.add_argument("-n",metavar="<isenode>",help="ISE admin node IP address",required=True)
parser.add_argument("-u",metavar="<username>",help="GUI Admin username",required=True)
parser.add_argument("-p",metavar="<password>",help="GUI Admin password",required=True)
parser.add_argument("-c",metavar="<certfile>",help="Path to certificate file",type=argparse.FileType("r"))
parser.add_argument("-f",metavar="<keyfile>",help="Path to key file",type=argparse.FileType("r"))
parser.add_argument("-k",metavar="<keypassword>",help="Key encryption password")
parser.add_argument("-N",metavar="<node>",help="Node list (ipv4, FQDN, or hostname) to install certificate. Space separated.",nargs="+")
parser.add_argument("-A",help="Certificate will be installed on all nodes",action="store_true")
parser.add_argument("-D",help="Admin uses certificate",action="store_true")
parser.add_argument("-P",metavar="<portal>",help="Portal uses certificate. A non-default tag is specified with P : <tag>",nargs="+")
parser.add_argument("-E",help="Eap uses certificate",action="store_true")
parser.add_argument("-X",help="Pxgrid uses certificate",action="store_true")
parser.add_argument("-R",help="Radius uses certificate",action="store_true")
parser.add_argument("-S",help="SAML uses certificate",action="store_true")


args=parser.parse_args()


username=args.u
password=args.p
ise_pan=args.n
ise_base_url=f"https://{ise_pan}/admin"
import_nodes=args.N
eap=args.E
admin=args.D
pxgrid = args.X
pem_file=args.c
pvk_file=args.f
key_password=args.k
radius=args.R
saml=args.S
portal_arg = args.P
VALID_FLAG = True
# creates first API instance. All other information and crosschecks are obtained from this source
api = IdentityServicesEngineAPI(username= username,
                                password=password,
                                base_url=ise_base_url,
                                verify=False,
                                )

# This function obtains certs from the specified api and lists them in a table format
def cert_list(api_param,hostname_param):
    print("\nLoading certificates...\n")
    devices_response = None
    try:
        devices_response = api_param.certificates.get_system_certificates(hostname_param)
    except ApiError as e:
        print(e)
    response = devices_response.response.response
    table = texttable.Texttable(max_width=120)
    table.set_cols_align(["c","c", "c", "c","c","c","c","c",])
    table.set_cols_valign(["t", "t","t","t","t","t","i","t",])
    rowlist = [["Certificate ID", "Protocol", "Issued To","Issued By", "Valid From", "Valid To", "Days Until Expiration", "Expired?"]]
    today = date.today()

    for i in range(len(response)):
        entry = response[i].expirationDate
        split_dates = entry.split(" ")
        expire = date(int(split_dates[5]),int(MONTHS[split_dates[1]]),int(split_dates[2]))
        days_to_expire_unformatted = str((expire-today)).split(",") 
        days_to_expire = days_to_expire_unformatted[0]
        if today > expire:
            isValid = "EXPIRED"
        else:
            isValid = "VALID"
        rowlist.append([response[i].id, response[i].usedBy, response[i].issuedTo,response[i].issuedBy, response[i].validFrom, 
                        response[i].expirationDate, days_to_expire,isValid])
    table.add_rows(rowlist)
    print(hostname_param+":")
    print(table.draw())

# This function is used to import a certificate
def cert_install(api_param,hostname_param):
    print("\nImporting certificate...\n")
    post_num = None
    initial_num = None
    # gets the pre-install number of certs
    try:
        devices_response =api_param.certificates.get_system_certificates(hostname_param)
        initial_num = len(devices_response.response.response)
    except ApiError as e:
        print(e)
        
    #opens certificate files stored on system and reads them into variables
    try:
        f = open(pem_file.name,'r')
        cert = f.read()
        f.close()
        f = open(pvk_file.name,'r')
        key = f.read()
        f.close()
        # this tool offers basic installation, look up sdk to see how to manipulate the below call for more advanced functionality
        api_param.certificates.import_system_certificate(admin,False,False,False,False,False,False,False,False,cert,eap,False,None,key_password,portal,portal_tag,key,pxgrid,radius,saml)
    except ApiError as e:
        print(e)


    #certificate import validation checks the the number of certificates after import is greater than before 
    try:
        devices_response2 =api_param.certificates.get_system_certificates(hostname_param)
        post_num = len(devices_response2.response.response)
    except ApiError as e:
        print(e)
    print(hostname_param+":")
    if post_num > initial_num:
        print(Fore.GREEN+"Certificate Successfully Imported.\n"+Fore.WHITE)
    else:
        print(Fore.RED+"Certificate Import Failed.\n"+Fore.WHITE)


# This function is used to cross reference and return apis and hostnames for nodes listed with -N
def N_Function():
    api_return_list = []
    hostname_return_list = []
    node_list = args.N
    deployment_nodes_fqdn = []
    deployment_nodes_ips = []
    deployed_hostnames = []
    try:
        response = api.node_deployment.get_nodes().response.response
        # creates a list of FQDNS, Hostnames, and IPv4 addresses for cross reference
        for i in range(len(response)):
            deployment_nodes_fqdn.append(response[i].fqdn)
            deployment_nodes_ips.append(response[i].ipAddress)
            deployed_hostnames.append(response[i].hostname)
        for n in node_list:
            # cross reference and notes placement of match with the counter variable
            if n in deployment_nodes_fqdn or  n in deployment_nodes_ips or n in deployed_hostnames:
                try:
                    counter = deployment_nodes_fqdn.index(n)
                except:
                    try:
                        counter = deployment_nodes_ips.index(n)
                    except:
                        counter = deployed_hostnames.index(n)
                # IP is the most reliable way to access a node so we use the cached index to find the ip of the match
                ise_pan2=deployment_nodes_ips[counter]
                ise_base_url2=f"https://{ise_pan2}/admin"
                # creates a new api object 
                api2 = IdentityServicesEngineAPI(username= username,
                                    password=password,
                                    base_url=ise_base_url2,
                                    verify=False,
                                    )
                hostname2 = deployed_hostnames[counter]
                # passes new api and hostname for api into lists for later use
                api_return_list.append(api2)
                hostname_return_list.append(hostname2)
            
            else:
                # if no match in main nodes deployment for other nodes listed it will print this error
                print(Fore.RED+n+" is not found in the deployment"+Fore.WHITE)
        

        return api_return_list , hostname_return_list
    except ApiError:
        print("you must have multiple Nodes deployed and connected to eachother to use -N")
        sys.exit()
            
def A_Function():
    api_return_list = []
    hostname_return_list = []
    try:
        # gets all nodes in a deployment
        nodes = api.node_deployment.get_nodes().response.response
    except ApiError as e: 
        print(str(e)+"\ncheck to see if other nodes are connected...\n")
        sys.exit()
            
    try:
        # gets IP address for every node and makes a new api object
        for i in range(len(nodes)):
            ip = nodes[i].ipAddress
            ise_base_url2=f"https://{ip}/admin"
            api2 = IdentityServicesEngineAPI(username= username,
                                password=password,
                                base_url=ise_base_url2,
                                verify=False,
                                )
            # returns api and hostname of every node
            hostname2 = api2.node_details.get_node_details().response.SearchResult.resources[i].name
            api_return_list.append(api2)
            hostname_return_list.append(hostname2)
        return api_return_list , hostname_return_list
    except ApiError:
        print("you must have multiple nodes deployed and connected to eachother to use -A")
        sys.exit()


# checks for valid credentials and connection on node specified by -n
def test_connection_1():
    print("Testing connection to "+ise_pan+"...")
    try:
        api.aci_settings.get_version()
        print("Connection to "+ise_pan+" Successful!!!")
    except ApiError as e:
        print(str(e)+"\nCheck node information entered and make sure API is enabled in the Node...\n")
        sys.exit()



    
if __name__=="__main__":
    # runs the test and checks for timeout when connecting to node
    p = multiprocessing.Process(target=test_connection_1)
    p.start()
    p.join(20)
    if p.is_alive():
        print("\nConnection test timed out on "+ise_pan+"...check Node status and try again")
        p.kill()
        sys.exit()

    p.join()

    # portal tag is parsed
    portal = None
    portal_tag = ""
    try:
        if args.P != None:
            if len(args.P)==0:
                portal = False
                portal_tag =None
            else:
                # parses based on : so if no colon the defualt tag will be used no matter what is entered after
                if re.search(":",args.P[0])!=None:
                    for i in range(len(portal_arg)):
                        if i != 0:
                            # allows for tags to have spaces
                            portal_tag += portal_arg[i]+" "
                    portal = True
                else:
                    portal_tag="Default Portal Certificate Group"
                    portal = True
    except:
        parser.error(f"Invalid certificate use: {args.P}")

    #used to install and list certs 
    if args.i and args.l:
        # install and list certs on all nodes
        if args.A:
            api_list, hostname_list = A_Function()
            if len(api_list) != 0:
                for a in api_list:
                    index = api_list.index(a)
                    cert_install(a,hostname_list[index])                    
                    cert_list(a,hostname_list[index])

        # install and list certs on specified nodes
        elif args.N != None:
            api_list, hostname_list = N_Function()
            if len(api_list) != 0:
                for a in api_list:
                    index = api_list.index(a)
                    cert_install(a,hostname_list[index])                    
                    cert_list(a,hostname_list[index])
        
            
        # install and list certs on only the node specified by -n 
        else:
            hostname2 = api.node_details.get_node_details().response.SearchResult.resources[0].name
            cert_install(api,hostname2)
            cert_list(api,hostname2)
            


    elif args.l:
        # list certs on all nodes
        if args.A:
            api_list, hostname_list = A_Function()
            if len(api_list) != 0:
                for a in api_list:
                    index = api_list.index(a)                 
                    cert_list(a,hostname_list[index])

        # list certs on specified nodes
        elif args.N != None:
            api_list, hostname_list = N_Function()
            if len(api_list) != 0:
                for a in api_list:
                    index = api_list.index(a)                   
                    cert_list(a,hostname_list[index])

                
        # list certs on only the node specified by -n         
        else:
            hostname2 = api.node_details.get_node_details().response.SearchResult.resources[0].name
            cert_list(api,hostname2)

    elif args.i:
        # install certs on all nodes
        if args.A:
            api_list, hostname_list = A_Function()
            if len(api_list) != 0:
                for a in api_list:
                    index = api_list.index(a)
                    cert_install(a,hostname_list[index])                    
        

        # install certs on specified nodes
        elif args.N != None:
            api_list, hostname_list = N_Function()
            if len(api_list) != 0:
                for a in api_list:
                    index = api_list.index(a)
                    cert_install(a,hostname_list[index])                    

        #install certs on only the node specified by -n  
        else:
            hostname2 = api.node_details.get_node_details().response.SearchResult.resources[0].name
            cert_install(api,hostname2)

    else:
        print("That is not a valid option. Must include -l, or -i")

