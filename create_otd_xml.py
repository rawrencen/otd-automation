#TUI: python createXML.py C:/Users/lxn521/PycharmProjects/otdAutomation/
#ARGS: python createXML.py C:/Users/lxn521/PycharmProjects/otdAutomation/ {a,b,A,B,AB} -otd dcsotdPOC -vs dev-ipm.sherwin.com -osn apinv-admin -osp e-corp-soa1-devint:8130 -rn apinv-admin -rf / -rt /console/
#testing
import xml.etree.ElementTree as ET
import argparse
import os
import datetime


### Dictionaries ###
env = {'1': 'DCS', '2': 'GEA', '3': 'mySW', '4': 'IDM', '5': 'IAM'}
tier = {'1': 'POC', '2': 'Tier0', '3': 'Tier1', '4': 'Tier2', '5': 'Tier3'}
rat = {'1': 'internal', '2': 'external'}  # rat = Resource Access Type: 1:internal, 2:external
extra_config = {}  # program will use the empty dictionary. extra_config = '1':'serverPoolName|serverPoolServers|routeName|routeTo|routeFrom', '2':'...', '3':'...'
routes = {}  # program will use the empty dictionary. routes = '1':'/yum*', '2':'/gtt*', etc...


### Methods ###
# Print error messages
def print_error(num):
    if num == 0:
        print("ERROR: Please select the correct number." + "\n")


# Returns OTD environment and tier number: otd_env_num|otd_tier_num
def get_env_tier_number():
    concat_env_tier = ''
    for x in range(0, 2):
        while True:
            print("Select the number that corresponds:")
            display_config_to_user(x)  # loop will run twice.
            num = int(input())
            if x == 0 and 0 < num <= len(env):  # ENV
                if str(num) in env:
                    concat_env_tier = str(num)
                    break
            elif x == 1 and 0 < num <= len(tier):  # TIER
                if str(num) in tier:
                    concat_env_tier = concat_env_tier + "|" + str(num)
                    break
            else:
                print_error(0)
    return concat_env_tier


# Returns OTD rat number: 1=int, 2=ext
def get_rat_num():
    while True:
        print("Select the number that corresponds to your OTD ACCESS TYPE:")
        display_config_to_user(2)  # 2 - print tier dictionary
        rat_num = input()
        if rat_num in rat:  # if userInput exists in tier
            return rat_num
        else:
            print_error(0)


# Display to user
def display_config_to_user(num):
    if num == 0:  # env dictionary
        for x in range(0, len(env)):
            print(str(x + 1) + ". " + str(env.get(str(x + 1))))
    elif num == 1:  # tier dictionary
        for x in range(0, len(tier)):
            print(str(x + 1) + ". " + str(tier.get(str(x + 1))))
    elif num == 2:  # net dictionary
        for x in range(0, len(rat)):
            print(str(x + 1) + ". " + str(rat.get(str(x + 1))))


# Returns otdConfigName
def get_otd_config_name(otd_env_num, otd_tier_num, otd_rat_num):
    env_name = env.get(otd_env_num)
    tier_name = tier.get(otd_tier_num)
    rat_name = rat.get(otd_rat_num)
    if rat_name == "external":
        otd_config_name = env_name.lower() + "otd" + tier_name + "-ext"
    else:
        otd_config_name = env_name.lower() + "otd" + tier_name
    print("You have selected: " + otd_config_name)
    return otd_config_name


# verify user input
def verify_user_input(str):
    print("Is this correct? " + str)
    print("1. Correct")
    print("2. Reenter")
    verify = input()
    return verify


# Returns virtual server name
def get_virtual_server_name():
    while True:
        print("Please enter the virtual server name:")
        virtual_server_name = input("")
        if virtual_server_name.find('.sherwin.com') != -1:
            verify = verify_user_input(virtual_server_name)
            if verify == "1":
                return virtual_server_name
        else:
            virtual_server_name = virtual_server_name + ".sherwin.com"
            verify = verify_user_input(virtual_server_name)
            if verify == "1":
                return virtual_server_name

# Gets the total number of origin servers from user and stores into extra_config dictionary
def get_num_of_origin_servers():
    while True:
        try:
            print("Enter the total number of origin server pool(s) (1-10):")
            num_origin_pools = int(input())
            if 0 < int(num_origin_pools) <= 10:
                # print(num_origin_pools)
                for x in range(0, num_origin_pools):
                    concat_origin_pools = create_origin_pools(x)
                    concat_routes = create_routes(x)
                    concat_str = concat_origin_pools + "|" + concat_routes
                    extra_config.update({x: concat_str})
                return num_origin_pools
        except ValueError:
            print("Please enter a number between 1-10:")


# returns str with parsed route
def parse_route(route):
    num_of_delimiters = route.count(',')
    if num_of_delimiters == 0 and route != 'default-route':

        route_append = "$uri = '" + route + "'"
        return route_append
    parts = route.split(',')
    route_append = ''
    for x in range(0, num_of_delimiters + 1):
        if x == num_of_delimiters:
            route_append += "$uri = '" + parts[x] + "'"
        else:
            route_append += "$uri = '" + parts[x] + "' or "
    return route_append


# Returns routeName|routeTo|routeFrom
def create_routes(num_origin_servers):
    if num_origin_servers == 0:
        route_name = 'default-route'
        while True:
            print("Current configuring the DEFAULT ROUTE")
            print("Please enter the TO URI.")
            print("EXAMPLE: /yum/")
            routeTo = input("")
            count_routes = routeTo.count(',')
            if count_routes > 0:
                print('ERROR: default-route should not multiple route destinations.')
                print('')
            else:
                print('Please enter the FROM URI.')
                print('EXAMPLE: /')
                routeFrom = input("")
                concat_route = route_name + "|" + routeTo + "|" + routeFrom
                return concat_route
    else:
        print('Additional route configuration')
        print('Please enter the route name.')
        route_name = input("")
        while True:
            print('Please enter the TO URI. NOTE: For multiple entries use \',\' as a DELIMITER')
            print('EXAMPLE: /yum*,/gtt*')
            routeTo = input("")
            parsedRoute = parse_route(routeTo)
            verify = verify_user_input(parsedRoute)
            if verify == '1':
                print('Please enter the FROM URI. Hit enter for empty value')
                print('EXAMPLE: /')
                routeFrom = input("")
                concat_route = route_name + "|" + parsedRoute + "|" + routeFrom
                return concat_route


# Returns serverPoolName|serverPoolServers
def create_origin_pools(iteration_of_origin):
    # print("iteration: " + str(iteration_of_origin+1))
    if iteration_of_origin == 0:
        print("Current configuring the DEFAULT ORIGIN SERVER POOL")
        print("Please enter the origin server name")
        serverPoolName = input("")
        print("Please enter the origin servers using a COMMA as a delimiter.")
        print("EXAMPLE: e-corp-soa1-devint:8131,e-corp-soa2-devint:8131")
        serverPoolServers = input("")
        concat_spn_sps = serverPoolName + "|" + serverPoolServers
    else:
        print("Additional origin server pools")
        print("Please enter the origin server name")
        serverPoolName = input("")
        print("Please enter the origin servers using a COMMA as a delimiter.")
        print("EXAMPLE: e-corp-soa1-devint:8131,e-corp-soa2-devint:8131")
        serverPoolServers = input("")
        concat_spn_sps = serverPoolName + "|" + serverPoolServers
    return concat_spn_sps


# New Create XML documents - embedded XML with attributes
def createXML(dir_location, data_center, num_of_origin_servers, otd_config_name, virtual_server_name, redirect_url):
    for x in range(0, num_of_origin_servers):
        xml_otd_config = ET.Element('otdConfig')
        xml_otd_config_name = ET.SubElement(xml_otd_config, 'otdConfigName', name=otd_config_name)
        xml_virtual_server_name = ET.SubElement(xml_otd_config_name, 'virtualServer', name=virtual_server_name)
        dict_str = extra_config.get(x)
        origin_server_name, origin_server_pools, route_name, route_to, route_from = dict_str.split("|")
        xml_route_name = ET.SubElement(xml_virtual_server_name, 'routeName', name=route_name)
        xml_route_from = ET.SubElement(xml_route_name, 'routeFrom')
        xml_route_from.text = route_from
        xml_route_to = ET.SubElement(xml_route_name, 'routeTo')
        xml_route_to.text = route_to
        xml_server_pool_name = ET.SubElement(xml_route_name, 'serverPoolName')
        xml_server_pool_name.text = origin_server_name
        xml_server_pool_servers = ET.SubElement(xml_route_name, 'serverPoolServers')
        xml_server_pool_servers.text = origin_server_pools
        xml_redirect_url = ET.SubElement(xml_route_name, 'redirectURL')
        xml_redirect_url.text = redirect_url

        file_name = otd_config_name + "_" + virtual_server_name + "_" + route_name + "_" + data_center.upper()

        xmlDoc = ET.tostring(xml_otd_config)
        if dir_location[len(dir_location)-1] != '/':                                    #check if directory_path is missing / at the end. if it is append it.
            dir_location = dir_location + '/'
        complete_path = dir_location + file_name + ".xml"
        print("Checking if " + file_name + " already exists...")
        if os.path.isfile(complete_path):                                               #check if file exists
            timedate = datetime.datetime.now().strftime("%Y-%m-%d.%H.%M.%S")
            print(file_name + " already exists!")
            print("Rotating " + file_name + " -> " + file_name + "." + timedate)
            append_date_time = complete_path + "." + str(timedate)
            os.rename(complete_path, append_date_time)
        print(file_name + " does not exist!")
        print("Creating configuration file: " + file_name)
        xmlFile = open(complete_path, "wb")
        xml_dec_as_bytes = str.encode('<?xml version="1.0"?>')
        xmlFile.write(xml_dec_as_bytes)
        xmlFile.write(xmlDoc)
        print("Configuration file has been created: " + complete_path)
        xmlFile.close()

#ARGS required including optional: python createXML.py C:/Users/lxn521/PycharmProjects/otdAutomation/ -dc {a,b,A,B|default} -otd dcsotdPOC -vs dev-ipm.sherwin.com -osn apinv-admin -osp e-corp-soa1-devint:8130 -rn apinv-admin -rf / -rt /console/
### MAIN ###
parser = argparse.ArgumentParser(
prog='createXML.py'
, usage='{REQUIRED}'
        '\nTUI: %(prog)s {absolute_file_path} {a,b,A,B,ab,AB} '
        '\nARGS: %(prog)s {absolute_file_path} {a,b,A,B,ab,AB} {-otd otd_config_name} {-vs virtual_server_name} {-osn origin_server_name} {-osp origin_server_pools} {-rn route_name} {-rf route_from} {-rt route_to} {-rurl redirect_url}'
, description='DESCRIPTION: createXML.py will create an OTD configuration XML file based on user input from the text interface or on the arguments passed to the program.')
#positional arguments
parser.add_argument('dir_location', type=str, help='output directory for XML file')
parser.add_argument('dc', type=str, choices=['a', 'b', 'A', 'B', 'ab', 'AB'], help='example: -dc AB', metavar='{a,b,A,B,ab,AB}')

#optional arguments
parser.add_argument('-otd', type=str, help='example: -otd dcsotdTier1', metavar='config_name')
parser.add_argument('-vs', type=str, help='example: -vs dev-apinvoicing.sherwin.com', metavar='v_server_name')
parser.add_argument('-osn', type=str, help='example: -osn apinvoicing-soa', metavar='o_server_name')
parser.add_argument('-osp', type=str, help='example: -osp e-corp-soa1-devint:8131,e-corp-soa2-devint:8131', metavar='o_server_pool')
parser.add_argument('-rn', type=str, help='example: -rn default-route', metavar='route_name')
parser.add_argument('-rf', type=str, help='example: -rf /', metavar='route_from')
parser.add_argument('-rt', type=str, help='example: -rt /yum*,/console*/,/gtt*', metavar='route_to')
parser.add_argument('-rurl', type=str, help='example: -rurl geabpm.sherwin.com', metavar='redirect_url')

args = parser.parse_args()
dir_location = args.dir_location
if os.path.isdir(dir_location): #check if output directory exists
    data_center = args.dc
    if args.otd is None:
        #TUI
        otd_env_tier_num = get_env_tier_number()
        otd_env_num, otd_tier_num = otd_env_tier_num.split("|")
        otd_rat_num = get_rat_num()  # get rat number
        otd_config_name = get_otd_config_name(otd_env_num, otd_tier_num, otd_rat_num)
        virtual_server_name = get_virtual_server_name()
        num_of_origin_servers = get_num_of_origin_servers()
        createXML(dir_location, data_center, num_of_origin_servers, otd_config_name, virtual_server_name)
    else:
        #ARGS
        otd_config_name = args.otd
        if args.vs.find(".sherwin.com") != -1:
            virtual_server_name = args.vs
        else:
            virtual_server_name = args.vs + ".sherwin.com"
        concat_osn_os = args.osn + "|" + args.osp
        if args.rn == 'default-route':
            concat_rn_rt_rf = args.rn + "|" + args.rt + "|" + args.rf
        else:
            route_to_str = args.rt
            parsed_route = parse_route(route_to_str)
            concat_rn_rt_rf = args.rn + "|" + parsed_route + "|" + args.rf
        concat_str = concat_osn_os + "|" + concat_rn_rt_rf
        extra_config.update({0: concat_str})
        if args.rurl is None:                                                       #if args -rurl doesn't exist, use virtual_server_name to fill.
            redirect_url = virtual_server_name
        else:
            redirect_url = args.rurl
        createXML(dir_location, data_center, 1, otd_config_name, virtual_server_name, redirect_url)
else:
    print()
    print("ERROR: output directory " + dir_location + " does not exist.")
