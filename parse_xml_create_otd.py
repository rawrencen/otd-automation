# /sw/pkg/oracle/bea12/oracle_common/common/bin/wlst.sh /sw/home/jxt518/git/toolkit/scripts/otd/otd.py /sw/home/jxt518/git/toolkit/scripts/otd/input.xml
# /sw/pkg/oracle/bea12/oracle_common/common/bin/wlst.sh /sw/home/lxn521/git/toolkit/scripts/otd/otd.py /sw/home/lxn521/git/toolkit/scripts/otd/dcsotdPOC_dev-ipm.sherwin.com_apinv-admin_AB.xml


import os
import sys
import time as systime
from pprint import pprint
import re
import time as pytime
import xml.sax

# Global variables
otd_config = ''
sp_name = ''
sp_servers = ''
virtual_server = ''
route_to = ''
route_from = ''
route_name = ''
redirect_url = ''

### Functions ###

class OTDConfigHandler(xml.sax.ContentHandler):
    element_name = ""
    element_content = ""
    element_attribute = ""

    def __init__(self):
        xml.sax.ContentHandler.__init__(self)

    def startElement(self, name, attr):
        global otd_config
        global virtual_server
        global route_name

        self.element_name = name
        self.element_attribute = attr

        if self.element_name == "otdConfigName":
            otd_config = self.element_attribute.getValue("name")
            print "otd_config: " + otd_config + "\n"
        if self.element_name == "virtualServer":
            virtual_server = self.element_attribute.getValue("name")
            print "virtual_server: " + virtual_server + "\n"
        if self.element_name == "routeName":
            route_name = self.element_attribute.getValue("name")
            print "route_name: " + route_name + "\n"

    def endElement(self, name):
        global sp_name
        global sp_servers
        global route_to
        global route_from

        if self.element_name == "serverPoolName":  # WORKS
            sp_name = self.element_content
            print "sp_name: " + sp_name + "\n"
        elif self.element_name == "serverPoolServers":  # WORKS
            sp_servers = self.element_content
            print "sp_servers: " + sp_servers + "\n"
        elif self.element_name == "routeTo":  # WORKS
            route_to = self.element_content
            print "route_to: " + route_to + "\n"
        elif self.element_name == "routeFrom":  # WORKS
            route_from = self.element_content
            print "route_from: " + route_from + "\n"
        elif self.element_name == "redirectURL":
            redirect_url = self.element_content
            print "redirect_url: " + redirect_url + "\n"
        self.element_name = ""
        self.element_content = ""
        self.element_attribute = ""

    def characters(self, content):
        self.element_content += content.lstrip()


# Gets the hostname of the server/computer that this script is running on
def parse_OTD_Configuration_XML(sourceFileName):
    source = open(sourceFileName)
    xml.sax.parse(source, OTDConfigHandler())


def get_host():
    hostname = os.popen("hostname -s").read()
    return hostname.rstrip()


# Gets the OTD configurations
def get_otd_configs():
    return otd_listConfigurations()


def otd_config_exists(new_otd_config):
    return_value = False

    otd_configs = get_otd_configs()
    for otd_config in otd_configs:
        if otd_config == new_otd_config:
            return_value = True

    return return_value


# Gets the route property
def get_route_properties(otd_config, virtual_server, route):
    props = {}
    props['configuration'] = otd_config
    props['virtual-server'] = virtual_server
    props['route'] = route
    return otd_getRouteProperties(props)

# Gets the Virtual Servers in specified OTD configuration
def get_otd_vs_in_config(otd_config):
    props = {}
    props['configuration'] = otd_config
    return otd_listVirtualServers(props)


# Gets the contents of the obj file
def get_otd_config_file(otd_config, obj_file):
    # print "otd_config: " + otd_config
    # print "obj_file: " + obj_file
    props = {}
    props['configuration'] = otd_config
    props['config-file'] = obj_file
    return otd_getConfigFile(props)


# Get properites for Virtual Server in OTD configuration
def get_otd_vs_props(otd_config, virtual_server):
    props = {}
    props['configuration'] = otd_config
    props['virtual-server'] = virtual_server
    return otd_getVirtualServerProperties(props)


# Get a list of routes for a virtual server in an OTD configuration
def get_list_of_routes(otd_config, virtual_server):
    props = {}
    props['configuration'] = otd_config
    props['virtual-server'] = virtual_server
    return otd_listRoutes(props)


# Get a properties of specific routes for a virtual server in an OTD configuration
def route_properties_exists(otd_config, virtual_server, route):
    try:
        props = {}
        props['configuration'] = otd_config
        props['virtual-server'] = virtual_server
        props['route'] = route
        if otd_getRouteProperties(props) is None:
            return False
        else:
            return True

    except WLSTException, err:
        return False


# Get origin servers from server pool
def get_origin_servers_from_pool(otd_config, serverpool):
    props = {}
    props['configuration'] = otd_config
    props['origin-server-pool'] = serverpool
    return otd_listOriginServers(props)


# Get List of Instances in a configuration
def get_list_of_otd_instances(otd_config):
    props = {}
    props['configuration'] = otd_config
    return otd_listInstances(props)


# Get origin servers pools in config
def get_origin_servers_pool(otd_config):
    props = {}
    props['configuration'] = otd_config
    return otd_listOriginServerPools(props)


def origin_server_pool_exists(otd_config, serverpool):
    return_value = False

    sps = get_origin_servers_pool(otd_config)
    for sp in sps:
        if serverpool == sp:
            return_value = True

    return return_value

# Creates a new route
def create_route(otd_config, virtual_server, route, sp_name, route_to):
    props = {}
    props['configuration'] = otd_config
    props['virtual-server'] = virtual_server
    props['route'] = route
    props['origin-server-pool'] = sp_name
    props['condition'] = route_to

    try:
        editCustom()
        startEdit()
        otd_createRoute(props)
        activate()

    except WLSTException, err:
        print "Error Trace as follows: "
        print WLSTException, err
        # undo('true','y')
        undo(defaultAnswer='y', unactivatedChanges='true')
        stopEdit('y')
        raise

# Creates an origin server pool, servers is a comma seprated string
def create_server_pool(otd_config, serverpool_name, servers):
    props = {}
    props['configuration'] = otd_config
    props['origin-server-pool'] = serverpool_name
    props['type'] = 'http'
    props['origin-server'] = servers
    print "ShowComponentChances"

    try:
        editCustom()
        startEdit()
        otd_createOriginServerPool(props)
        activate()

    except WLSTException, err:
        print "Error Trace as follows: "
        print WLSTException, err
        # undo('true','y')
        undo(defaultAnswer='y', unactivatedChanges='true')
        stopEdit('y')
        raise


def get_otd_http_listeners(otd_config, http_listener_name):
    props = {}
    props['configuration'] = otd_config
    props['http-listener'] = http_listener_name
    return otd_getHttpListenerProperties(props)


def create_vs(otd_config, virtual_server, serverpool_name):
    props = {}
    props['configuration'] = otd_config
    props['virtual-server'] = virtual_server
    props['host'] = virtual_server
    props['origin-server-pool'] = serverpool_name
    props['http-listener'] = 'http-listener-1,http-listener-2'

    try:
        editCustom()
        startEdit()
        otd_createVirtualServer(props)
        activate()
        softRestart(otd_config, block='true')

    except WLSTException, err:
        print "Error Trace as follows: "
        print WLSTException, err
        undo(defaultAnswer='y', unactivatedChanges='true')
        stopEdit('y')
        raise


def vs_exists(otd_config, new_virtual_server):
    return_value = False

    virtual_servers = get_otd_vs_in_config(otd_config)
    for virtual_server in virtual_servers:
        if virtual_server == new_virtual_server:
            return_value = True

    return return_value


def set_to_from_in_vs_route(otd_config, new_virtual_server, route, route_from, route_to):
    props = {}
    props['configuration'] = otd_config
    props['virtual-server'] = virtual_server
    props['route'] = route
    props['from'] = route_from + '*'
    props['to'] = route_to + '*'

    try:
        editCustom()
        startEdit()
        otd_setRouteProperties(props)
        otdInstanceName = 'otd_' + otd_config + '_OTDHOST1'
        showComponentChanges(otdInstanceName)
        pullComponentChanges(otdInstanceName)

        enableOverwriteComponentChanges()

        activate()
        softRestart(otd_config, block='true')

    except WLSTException, err:
        print "Error Trace as follows: "
        print WLSTException, err
        # undo('true','y')
        undo(defaultAnswer='y', unactivatedChanges='true')
        stopEdit('y')
        raise


def route_exists(otd_config, virtual_server, new_route):
    return_value = False

    routes = get_list_of_routes(otd_config, virtual_server)

    for route in routes:
        if route == new_route:
            return_value = True

    return return_value

def uri_exists(otd_config, virtual_server, route):
    return_value = False
    route_to_boolean = False
    route_from_boolean = False

    route_exists_bool = route_exists(otd_config, virtual_server, route)
    if route_exists_bool:
        route_properties_exists_bool = route_properties_exists(otd_config, virtual_server, route)
        if route_properties_exists_bool:
            route_properties = get_route_properties(otd_config, virtual_server, route)

            #print "route_properties: " + route_properties['to']

            for route_property in route_properties:
                if route_properties['to'] is not None:
                    route_to_boolean = True
                if route_properties['from'] is not None:
                    route_from_boolean = True

            if route_to_boolean and route_from_boolean:
                return_value = True

    return return_value

def redirect_exists():
    return_value = False

    command_line = 'cat ' + os.environ["OTD_INST_CONFIG"] + "/" + virtual_server + "-obj.conf"
    #command_line = 'cd ~otdadm/env_files/' + env + ' && . ./' + tier.lower() + '.env && env'
    # print "command_line: " + command_line
    # print 'command_line: cd ~otdadm/env_files/dcs && . ./poc.env && env'
    obj_conf_out_pipe = os.popen(command_line)
    for obj_conf_line in obj_conf_out_pipe.readlines():
        #print obj_conf_line.rstrip('\n')
        if obj_conf_line.rstrip('\n') == '<If not $internal>':
            return_value = True

    return return_value

def verify_editobj_was_run():
    return_value = False

    command_line = 'cat ' + os.environ["OTD_INST_CONFIG"] + "/" + virtual_server + "-obj.conf"
    obj_conf_out_pipe = os.popen(command_line)
    for obj_conf_line in obj_conf_out_pipe.readlines():
        if obj_conf_line.rstrip('\n') == 'AuthTrans fn="OBWebGate_Authent" dump="true"':
            return_value = True

    return return_value

def config_wg_for_vs(otd_config, virtual_server):
    wg_obj_conf_cmd = 'cd ' + os.environ["OTD_INST_CONFIG"] + ' && ' + os.environ["INST_TOOLS"] + '/EditObjConf -f ' + \
                      os.environ["OTD_INST_CONFIG"] + '/' + virtual_server + '-obj.conf -w ' + os.environ[
                          "OTD_INST_CONFIG"] + ' -oh /sw/pkg/oracle/bea12 -ws otd'
    try:
        editCustom()
        startEdit()
        return_value = os.system(wg_obj_conf_cmd)

        if return_value != 0:
            raise WLSTException("Command " + wg_obj_conf_cmd + " failed. Reverting Changes.")

        otdInstanceName = 'otd_' + otd_config + '_OTDHOST1'
        showComponentChanges(otdInstanceName)
        pullComponentChanges(otdInstanceName)
        enableOverwriteComponentChanges()
        activate()
        softRestart(otd_config, block='true')

    except WLSTException, err:
        print "Error Trace as follows: "
        print WLSTException, err
        undo(defaultAnswer='y', unactivatedChanges='true')
        stopEdit('y')
        print "skipping..."


def pullComponents(otd_config, virtual_server):  # Testing

    try:
        editCustom()
        startEdit()
        showComponentChanges(virtual_server)
        pullComponentChanges(virtual_server)
        activate()
        softRestart(otd_config, block='true')
    # activate(200000, block='true')

    except WLSTException, err:
        print "Error Trace as follows: "
        print WLSTException, err
        undo(defaultAnswer='y', unactivatedChanges='true')
        stopEdit('y')
        print "skipping..."


def list_config_files_for_configuration(otd_config):
    props = {}
    props['configuration'] = otd_config
    return otd_listConfigFiles(props)


def fix_redirect_in_obj(otd_config, virtual_server, route_to):
    obj_config_file = ""
    obj_configs = list_config_files_for_configuration(otd_config)
    uts = int(pytime.time())

    script_name = os.path.basename(sys.argv[0])

    complete_tmp_file_path = '/tmp/' + str(script_name) + '_' + str(uts)

    for obj_config in obj_configs:
        if obj_config == virtual_server + '-obj.conf':
            obj_config_file = obj_config

    if obj_config_file != "":
        print "found config: " + obj_config_file
    else:
        print "Error: Could not find obj.conf file to update for redirection: " + virtual_server + '-obj.conf, skipping...'
        return

    contents = get_otd_config_file(otd_config, obj_config_file)

    tmp_out_fh = open(complete_tmp_file_path, "w")
    for line in contents.splitlines():
        tmp_out_fh.write(line + '\n')

        if line == '<Object name="default">':
            tmp_out_fh.write('<If not $internal>' + '\n')
            tmp_out_fh.write('<If not $restarted and $uri =~ "^/$">' + '\n')
            tmp_out_fh.write('NameTrans fn="restart" uri="' + route_to + '"' + '\n')
            tmp_out_fh.write('</If>' + '\n')
            tmp_out_fh.write('</If>' + '\n')

    tmp_out_fh.close()

    props = {}
    props['configuration'] = otd_config
    props['file-path'] = complete_tmp_file_path
    props['config-file'] = obj_config_file

    try:
        editCustom()
        startEdit()
        otd_saveConfigFile(props)

        otdInstanceName = 'otd_' + otd_config + '_OTDHOST1'
        showComponentChanges(otdInstanceName)
        pullComponentChanges(otdInstanceName)

        enableOverwriteComponentChanges()

        activate()
        softRestart(otd_config, block='true')
    except WLSTException, err:
        dumpStack()
        print "Error Trace as follows: "
        print WLSTException, err
        dumpStack()
        undo(defaultAnswer='y', unactivatedChanges='true')
        stopEdit('y')
        raise

### MAIN ###
input_file = sys.argv[1]
print "input_file: " + input_file + "\n"

if os.path.isfile(input_file):
    print "Loading " + input_file + "...\n"
else:
    print "Error: file does not exist\n"
    exit()

parse_OTD_Configuration_XML(input_file)

# Not supplied by inputs
route = route_name
print "route: " + route + "\n"

# find env and source in tier
env_file = ""
env, tier = otd_config.split("otd")
print "env: " + env + "\n"
print "tier: " + tier + "\n"

# Source in the environment
command_line = 'cd ~otdadm/env_files/ && . ./' + tier.lower() + '.env && env'
#print "command_line: " + command_line
#print 'command_line: cd ~otdadm/env_files/dcs && . ./poc.env && env'
env_out_pipe = os.popen(command_line)

for env_value in env_out_pipe.readlines():
    env_value = str(env_value)
    key, value = env_value.split("=", 1)
    os.environ[key] = value.rstrip()
    #print key + ":" + value
print 'starting the script .... '
hostname = get_host()

try:

    # connect(username,password,'t3://' + hostname  + ':8130')
    connect(userConfigFile='/sw/pkg/user_projects/dcsotd/nodemanager/dcsotdNMConfigfile.secure',
            userKeyFile='/sw/pkg/user_projects/dcsotd/nodemanager/dcsotdNMUserkeyfile.secure',
            url='t3://' + hostname + ':8130')
    otd_config_exists_bool = otd_config_exists(otd_config)

    if not otd_config_exists_bool:
        print 'OTD configuration (' + str(otd_config) + ') does not exist!'
        exit()

    server_exists_bool = origin_server_pool_exists(otd_config, sp_name)

    if server_exists_bool:
        print 'Origin Server Pool ( ' + sp_name + ' )  in OTD Configuration ( ' + otd_config + ' )  exists, skipping  ...'

    else:
        print "Info: Creating ServerPool(" + str(sp_name) + ")..."
        create_server_pool(otd_config, sp_name, sp_servers)

    vs_exists_bool = vs_exists(otd_config, virtual_server)

    if vs_exists_bool:
        print 'Virtual Server ( ' + virtual_server + ' )  in OTD Configuration ( ' + otd_config + ' )  exists, skipping  ...'

    else:
        print "Info: Creating Virtual Server(" + str(virtual_server) + ")..."
        create_vs(otd_config, virtual_server, sp_name)

    route_exists_bool = route_exists(otd_config, virtual_server, route)
    if not route_exists_bool:   #if route-name does not exist, create new route
        print route + " does not exist... "
        print "Creating " + route + "\n"
        create_route(otd_config, virtual_server, route, sp_name, route_to)
    else:                       #else if route_name does exist, check if URI map exists, and redirect_edit_obj exists.
        print route + " exists. Checking if URI Mapping and editObj redirect is configured..."
        uri_map_exists_bool = uri_exists(otd_config, virtual_server, route)
        #print "URI_MAP_EXISTS_BOOL: " + str(uri_map_exists_bool)
        redirect_editobj_exists_bool = redirect_exists()
        #print "REDIRECT_EDITOBJ_EXISTS_BOOL: " + str(redirect_editobj_exists_bool)

    if route == 'default-route' and uri_map_exists_bool and redirect_editobj_exists_bool:
        print "The default-route URI Mapping and editObj redirect for " + virtual_server + " already exists! Please remove the URI Mapping and editObj manually and rerun the script." + "\n"
    elif route_exists_bool and route == 'default-route' and not uri_map_exists_bool and not redirect_editobj_exists_bool and not route_to == '/':
        print "The default-route exists, but URI Mapping and editObj are NULL."
        print "Updating URI Mapping..." + "\n"
        set_to_from_in_vs_route(otd_config, virtual_server, route, route_from, route_to)
        print "Updating editObj redirect..." + "\n"
        fix_redirect_in_obj(otd_config, virtual_server, route_to)
    elif route_exists_bool and route == 'default-route' and uri_map_exists_bool and not redirect_editobj_exists_bool and not route_to == '/':
        print "The default-route and URI Mapping exist, but editObj redirect is missing"
        print "Updating editObj redirect..." + "\n"
        fix_redirect_in_obj(otd_config, virtual_server, route_to)
    elif route_exists_bool and route == 'default_route' and not uri_map_exists_bool and redirect_editobj_exists_bool and not route_to == '/':
        print "The default-route and editObj redirect exist, but URI Mapping is missing"
        print "Updating URI Mapping..." + "\n"
        set_to_from_in_vs_route(otd_config, virtual_server, route, route_from, route_to)
    elif route_exists_bool and route_to == '/':
        print route + " has been setup." + "\n"
    elif route_exists_bool:
        print route + " already exists! Please remove manually and rerun the script." + "\n"

    if verify_editobj_was_run():
        print "editObj was already run for this virtual server... skipping..."
    else:
        config_wg_for_vs(otd_config, virtual_server)

except Exception, err:
    print "MAIN: Error Trace as follows: "
    print Exception, err
    dumpStack()
    exit()

softRestart(otd_config, block='true')
print "Finished Successfully\n";
exit()
