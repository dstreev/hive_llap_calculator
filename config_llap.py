#!/usr/bin/env python

import readline

TF = ("true", "false")
KB = 1024

TYPE_INPUT = "input"
TYPE_CALC = "calc"
TYPE_REFERENCE = "reference(default)"
TYPE_THRESHOLD = "threshold"

# Yarn Sizing
YARN_MEMORY_PERCENT = 80
LLAP_PERCENT_OF_CLUSTER = 10
LLAP_PERCENT_OF_YARN_NODE_MEMORY = 90
LLAP_CACHE_PERCENTAGE = 50

# Configuration

# [ Short Desc, Type, Section, Config, Value, Options, Long Desc ]
HEADER = ["Short Desc", "Type", "Section", "Config", "Value", "Options", "Long Desc"]

# Positions
POS_SHORT_DESC = 0
POS_TYPE = 1
POS_SECTION = 2
POS_CONFIG = 3
POS_VALUE = 4
POS_OPTIONS = 5
POS_LONG_DESC = 6

# Sections
YARN_SITE = ("YARN Configuration", "yarn-site")
HIVE_INTERACTIVE_SITE = ("LLAP Configuration", "hive-interactive-site")
HIVE_INTERACTIVE_ENV = ("LLAP Environment", "hive-interactive-env")
TEZ_INTERACTIVE_SITE = ("LLAP Tez Configuration", "tez-interactive-site")
HOST_ENV = ("Cluster Host Configuration", "host-env")
THRESHOLD_ENV = ("Calculation Thresholds", "threshold-env")
CLUSTER_ENV = ("Cluster Environment", "cluster-env")

SECTIONS = (HOST_ENV, THRESHOLD_ENV, YARN_SITE, HIVE_INTERACTIVE_SITE, HIVE_INTERACTIVE_ENV, TEZ_INTERACTIVE_SITE)

# Environment
WORKER_MEMORY_GB = ["Node Memory Footprint(GB)", TYPE_INPUT, HOST_ENV,
                    "", 16, (), ""]
WORKER_COUNT = ["Number of Cluster Worker Nodes", TYPE_INPUT, HOST_ENV,
                "", 30, (), ""]
WORKER_CORES = ["Number of Cores per Host", TYPE_INPUT, HOST_ENV, "", 8, (), ""]

# Thresholds
PERCENT_OF_HOST_MEM_FOR_YARN = ["Percent of Host Memory for YARN NodeManager", TYPE_REFERENCE, THRESHOLD_ENV, "", 80]
PERCENT_OF_CLUSTER_FOR_LLAP = ["Percent of Cluster for LLAP", TYPE_INPUT, THRESHOLD_ENV, "", 50]
PERCENT_OF_NODE_FOR_LLAP_MEM = ["Percent of NodeManager Memory for LLAP", TYPE_REFERENCE, THRESHOLD_ENV, "", 90]
PERCENT_OF_LLAP_FOR_CACHE = ["Percent of LLAP Memory for Cache", TYPE_REFERENCE, THRESHOLD_ENV, "", 50]
PERCENT_OF_CORES_FOR_EXECUTORS = ["Percent of Cores for LLAP Executors", TYPE_REFERENCE, THRESHOLD_ENV, "", 80]
THRESHOLD_MAX_HEADROOM_GB = ["MAX LLAP Headroom Value", TYPE_REFERENCE, THRESHOLD_ENV, "", 12]
PERCENT_OF_DAEMON_CONTAINER_MEM_MB_FOR_HEADROOM = ["Percent of Daemon Container Memory(MB) for Headroom",
                                                   TYPE_REFERENCE, THRESHOLD_ENV, "", 20]
PERCENT_OF_EXECUTORS_FOR_IO_THREADPOOL = ["Percent of Executors for IO Threadpool", TYPE_REFERENCE,
                                          THRESHOLD_ENV, "", 100]

# YARN
YARN_NM_RSRC_MEM_MB = ["Node Manager Memory(MB)", TYPE_CALC, YARN_SITE,
                       "yarn.nodemanager.resource.memory-mb", 13107, (), ""]
YARN_SCH_MAX_ALLOC_MEM_MB = ["Yarn Max Mem Allocation(MB)", TYPE_CALC, YARN_SITE,
                             "yarn.scheduler.maximum-allocation-mb", 11927, (), ""]

# Hive Interactive Site
HIVE_LLAP_QUEUE = ["YARN Queue", TYPE_INPUT, HIVE_INTERACTIVE_SITE,
                   "hive.llap.daemon.queue.name", "llap", (), ""]
TEZ_CONTAINER_SIZE_MB = ["TEZ Container Size", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                         "hive.tez.container.size", KB * 4, (), ""]
LLAP_DAEMON_CONTAINER_MEM_MB = ["Daemon Memory(MB)", TYPE_CALC, HIVE_INTERACTIVE_SITE,
                                "hive.llap.daemon.yarn.container.mb", 11796, (), ""]
LLAP_CACHE_MEM_MB = ["Cache(MB)", TYPE_CALC, HIVE_INTERACTIVE_SITE,
                     "hive.llap.io.memory.size", KB * 4, (), ""]
LLAP_OBJECT_CACHE_ENABLED = ["Object Cache Enabled?", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                             "hive.llap.object.cache.enabled", "true",
                             TF, "Cache objects (plans, hashtables, etc) in LLAP"]
LLAP_MEMORY_MODE = ["Memory Mode", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                    "hive.llap.io.memory.mode", "cache", ("cache", "allocator", "none"), ""]
LLAP_IO_ENABLED = ["Cache Enabled?", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                   "hive.llap.io.enabled", "true", TF, ""]
LLAP_IO_ALLOCATOR_NMAP_ENABLED = ["Direct I/O cache enabled?", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                                  "hive.llap.io.allocator.nmap", "false", TF,
                                  "Whether ORC low-level cache should use memory mapped allocation (direct I/O)"]
LLAP_IO_ALLOCATOR_NMAP_PATH = ["Direct I/O cache path", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                               "hive.llap.io.allocator.nmap.path", "", (), ""]

LLAP_NUM_EXECUTORS_PER_DAEMON = ["Num of Executors", TYPE_CALC, HIVE_INTERACTIVE_SITE,
                                 "hive.llap.daemon.num.executors", 12, (), ""]

LLAP_IO_THREADPOOL = ["I/O Threadpool", TYPE_CALC, HIVE_INTERACTIVE_SITE,
                      "hive.llap.io.threadpool", 12, (), ""]

# Hive Interactive Size (Custom)
LLAP_PREWARMED_ENABLED = ["Prewarmed Containers", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                          "hive.prewarm.enabled", "false", TF, ""]
LLAP_PREWARM_NUM_CONTAINERS = ["Number of prewarmed Containers", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                               "hive.prewarm.numcontainers", 1, (), ""]

# Hive Interactive Env
LLAP_NUM_NODES = ["Daemon Count", TYPE_CALC, HIVE_INTERACTIVE_ENV,
                  "num_llap_nodes_for_llap_daemons", 1, (), ""]
LLAP_CONCURRENCY = ["Query Concurrency", TYPE_INPUT, HIVE_INTERACTIVE_ENV,
                    "hive.server2.tez.sessions.per.default.queue", 2, (), ""]
LLAP_AM_DAEMON_HEAP_MB = ["AM Heap for Daemons", TYPE_INPUT, HIVE_INTERACTIVE_ENV,
                          "hive_heapsize", 4096, (), ""]
LLAP_HEADROOM_MEM_MB = ["Heap Headroom", TYPE_CALC, HIVE_INTERACTIVE_ENV,
                        "llap_headroom_space", 2048, (), ""]
LLAP_DAEMON_HEAP_MEM_MB = ["Daemon Heap size(MB)", TYPE_CALC, HIVE_INTERACTIVE_ENV,
                           "llap_heap_size", 8192, (), ""]

# TEZ Interactive site
TEZ_AM_MEM_MB = ["TEZ AM Container size(MB)", TYPE_REFERENCE, TEZ_INTERACTIVE_SITE,
                 "tez.am.resource.memory.mb", KB * 2, (), ""]

# Total Section
TOTAL_MEM_FOOTPRINT = ["Total Memory Footprint", TYPE_CALC, CLUSTER_ENV,
                       "", 0, (), ""]
TOTAL_LLAP_DAEMON_FOOTPRINT = ["Total LLAP Daemon Memory Footprint", TYPE_CALC, CLUSTER_ENV,
                               "", 0, (), ""]
TOTAL_LLAP_OTHER_FOOTPRINT = ["Total LLAP Other Memory Footprint", TYPE_CALC, CLUSTER_ENV,
                              "", 0, (), ""]
TOTAL_LLAP_MEM_FOOTPRINT = ["Total LLAP Memory Footprint", TYPE_CALC, CLUSTER_ENV,
                            "", 0, (), ""]
LLAP_QUEUE_MIN_REQUIREMENT = ["LLAP Minimum YARN Queue Capacity % Requirement", TYPE_CALC, CLUSTER_ENV,
                              "", 0, (), ""]


CONFIGS = [WORKER_MEMORY_GB,
           WORKER_COUNT,
           WORKER_CORES,

           PERCENT_OF_HOST_MEM_FOR_YARN,
           PERCENT_OF_CLUSTER_FOR_LLAP,
           PERCENT_OF_NODE_FOR_LLAP_MEM,
           PERCENT_OF_LLAP_FOR_CACHE,
           PERCENT_OF_CORES_FOR_EXECUTORS,
           PERCENT_OF_DAEMON_CONTAINER_MEM_MB_FOR_HEADROOM,
           PERCENT_OF_EXECUTORS_FOR_IO_THREADPOOL,
           THRESHOLD_MAX_HEADROOM_GB,

           YARN_NM_RSRC_MEM_MB,
           TOTAL_MEM_FOOTPRINT,
           YARN_SCH_MAX_ALLOC_MEM_MB,
           HIVE_LLAP_QUEUE,

           LLAP_NUM_NODES,

           LLAP_CONCURRENCY,
           TEZ_AM_MEM_MB,

           LLAP_NUM_EXECUTORS_PER_DAEMON,

           LLAP_AM_DAEMON_HEAP_MB,
           LLAP_DAEMON_CONTAINER_MEM_MB,
           LLAP_DAEMON_HEAP_MEM_MB,
           LLAP_HEADROOM_MEM_MB,
           LLAP_CACHE_MEM_MB,

           TOTAL_LLAP_DAEMON_FOOTPRINT,


           TOTAL_LLAP_OTHER_FOOTPRINT,

           LLAP_MEMORY_MODE,
           LLAP_IO_ENABLED,
           LLAP_OBJECT_CACHE_ENABLED,

           LLAP_IO_THREADPOOL,

           LLAP_IO_ALLOCATOR_NMAP_ENABLED,
           LLAP_IO_ALLOCATOR_NMAP_PATH,

           TEZ_CONTAINER_SIZE_MB,

           LLAP_PREWARMED_ENABLED,
           LLAP_PREWARM_NUM_CONTAINERS,

           TOTAL_LLAP_MEM_FOOTPRINT,
           LLAP_QUEUE_MIN_REQUIREMENT]

SELECT_TASK = "\t-- Select Task -- : "
SELECT_SECTION = "\t-- Select Section -- : "
SELECT_CONFIG = "\t-- Select Config(enter for previous menu) -- : "
NEW_VALUE_INPUT = "\t-- New Value? -- : "
GO_BACK = "\n.. previous menu ..\n"

MODE = [TYPE_INPUT]


def run_calc():
    # print ("running calc")

    ## YARN
    #########
    # YARN_NM_RSRC_MEM_MB
    YARN_NM_RSRC_MEM_MB[POS_VALUE] = WORKER_MEMORY_GB[POS_VALUE] * KB * PERCENT_OF_HOST_MEM_FOR_YARN[POS_VALUE] / 100
    # YARN_SCH_MAX_ALLOC_MEM_MB
    # Adding a percent for a little clearance on mem settings.
    YARN_SCH_MAX_ALLOC_MEM_MB[POS_VALUE] = YARN_NM_RSRC_MEM_MB[POS_VALUE] * \
                                           (PERCENT_OF_NODE_FOR_LLAP_MEM[POS_VALUE] + 1) / 100

    ## LLAP
    #########
    # LLAP_NUM_NODES
    LLAP_NUM_NODES[POS_VALUE] = WORKER_COUNT[POS_VALUE] * PERCENT_OF_CLUSTER_FOR_LLAP[POS_VALUE] / 100

    # LLAP_NUM_EXECUTORS_PER_DAEMON
    LLAP_NUM_EXECUTORS_PER_DAEMON[POS_VALUE] = WORKER_CORES[POS_VALUE] * \
                                               PERCENT_OF_CORES_FOR_EXECUTORS[POS_VALUE] / 100

    # LLAP_DAEMON_CONTAINER_MEM_MB
    LLAP_DAEMON_CONTAINER_MEM_MB[POS_VALUE] = YARN_NM_RSRC_MEM_MB[POS_VALUE] * \
                                              (PERCENT_OF_NODE_FOR_LLAP_MEM[POS_VALUE]) / 100

    # LLAP_HEADROOM_MEM_MB
    # =IF((E37*0.2) > (12*1024),12*1024,E37*0.2)
    if LLAP_DAEMON_CONTAINER_MEM_MB[POS_VALUE] * PERCENT_OF_DAEMON_CONTAINER_MEM_MB_FOR_HEADROOM[POS_VALUE] / 100 \
            > THRESHOLD_MAX_HEADROOM_GB[POS_VALUE] * KB:
        LLAP_HEADROOM_MEM_MB[POS_VALUE] = THRESHOLD_MAX_HEADROOM_GB[POS_VALUE] * KB
    else:
        LLAP_HEADROOM_MEM_MB[POS_VALUE] = LLAP_DAEMON_CONTAINER_MEM_MB[POS_VALUE] * \
                                          PERCENT_OF_DAEMON_CONTAINER_MEM_MB_FOR_HEADROOM[POS_VALUE] / 100

    # LLAP_DAEMON_HEAP_MEM_MB
    # =(E37-E38)*(1-E16)
    LLAP_DAEMON_HEAP_MEM_MB[POS_VALUE] = (LLAP_DAEMON_CONTAINER_MEM_MB[POS_VALUE] - LLAP_HEADROOM_MEM_MB[POS_VALUE]) * \
                                         (100 - PERCENT_OF_LLAP_FOR_CACHE[POS_VALUE]) / 100

    # LLAP_CACHE_MEM_MB
    # =E37-E39
    LLAP_CACHE_MEM_MB[POS_VALUE] = LLAP_DAEMON_CONTAINER_MEM_MB[POS_VALUE] - LLAP_DAEMON_HEAP_MEM_MB[POS_VALUE]

    # LLAP_IO_THREADPOOL
    LLAP_IO_THREADPOOL[POS_VALUE] = LLAP_NUM_EXECUTORS_PER_DAEMON[POS_VALUE] * \
                                    PERCENT_OF_EXECUTORS_FOR_IO_THREADPOOL[POS_VALUE] / 100
    
    # Total LLAP Daemon Footprint
    TOTAL_LLAP_DAEMON_FOOTPRINT[POS_VALUE] = LLAP_NUM_NODES[POS_VALUE] * LLAP_DAEMON_CONTAINER_MEM_MB[POS_VALUE] \
                                             + LLAP_AM_DAEMON_HEAP_MB[POS_VALUE]
    
    # Total LLAP Other Footprint
    # =IF(E30, IF(E32>0, (E29*E32*E34)+(E29*E33),(E29*E31*E34)+(E29*E33)),E29*E33)
    # TODO: Add support for PREWARMED CONTAINERS.
    TOTAL_LLAP_OTHER_FOOTPRINT[POS_VALUE] = LLAP_CONCURRENCY[POS_VALUE] * LLAP_AM_DAEMON_HEAP_MB[POS_VALUE]

    # Total LLAP Memory Footprint
    TOTAL_LLAP_MEM_FOOTPRINT[POS_VALUE] = TOTAL_LLAP_DAEMON_FOOTPRINT[POS_VALUE] + TOTAL_LLAP_OTHER_FOOTPRINT[POS_VALUE]
    
    # Total Cluster Memory Footprint
    TOTAL_MEM_FOOTPRINT[POS_VALUE] = YARN_NM_RSRC_MEM_MB[POS_VALUE] * WORKER_COUNT[POS_VALUE]

    # Total LLAP Yarn Queue Requirement (Percent of Root Queue)
    LLAP_QUEUE_MIN_REQUIREMENT[POS_VALUE] = round(float(TOTAL_LLAP_MEM_FOOTPRINT[POS_VALUE]) / \
                                            TOTAL_MEM_FOOTPRINT[POS_VALUE] * 100, 2)
    
def get_current(selection, lst):
    for item in lst:
        if item[0] == selection:
            return item[2]


def set_value(selection, lst):
    current = []
    for item in lst:
        if item[0] == selection:
            current = item

    new_value = raw_input("{0}\t[{1}]:".format(current[1], current[2]))

    current[2] = new_value


# def input_loop():
#     for element in ENV_SET:
#         # print (element[0])
#         print ("{0}: {1} \t{2}".format(element[0], element[1], element[2]))
#
#     selection = raw_input("Select property: ")
#
#     # current = get_current(selection, ENV_SET)
#
#     set_value(selection, ENV_SET)
#
#     print ENV_SET
#     # line = ''
#     # while line != 'stop':
#     #     line = raw_input('...')
#     #     print 'Dispatch \t\t%s' % line


def convert(value, original):
    if isinstance(original, int):
        return int(value)
    if isinstance(original, long):
        return long(value)
    if isinstance(original, str):
        return str(value)


def sections_loop():
    while True:
        # List Sections
        inc = 1
        for section in SECTIONS:
            print ("({0})\t{1}".format(inc, section[0]))
            inc += 1

        # Select Section
        try:
            raw_selection = raw_input(SELECT_SECTION)
            if raw_selection == "":
                break
            selection = int(raw_selection)
        except ValueError:
            # print (GO_BACK)
            return

        # Check selection boundaries
        if selection > len(SECTIONS) or selection < 1:
            # print (GO_BACK)
            return

        if not section_loop(selection):
            break


def section_loop(selection):
    while True:
        # Identify Section
        section_choice = ""
        inc = 1
        for section in SECTIONS:
            if selection == inc:
                section_choice = section
            inc += 1

        # Find configs in Section that are "TYPE_INPUT"
        section_configs = []
        for config in CONFIGS:
            if config[POS_SECTION][1] == section_choice[1] and config[POS_TYPE] in MODE:
                section_configs.append(config)

        if not change_config(select_config(section_choice, section_configs)):
            break
        else:
            run_calc()


def select_config(section, section_configs):
    # List Filtered Sections
    print (section[0])
    inc = 1
    for config in section_configs:
        print (" ({0})\t[{1}] {2}".format(inc, config[POS_VALUE], config[POS_SHORT_DESC]))
        inc += 1

    # Pick Config to Edit
    try:
        choice = int(raw_input(SELECT_CONFIG))
    except ValueError:
        print (GO_BACK)
        return True

        # Check selection boundaries
    if choice > (inc - 1) or choice < 1:
        print (GO_BACK)
        return True

    # Enter New Value
    inc = 1
    # target_config = []
    for config in section_configs:
        if choice == inc:
            return config
        inc += 1


def change_config(config):
    try:
        raw_value = raw_input("{0}({1}) [{2}]: ".format(config[POS_SHORT_DESC], config[POS_CONFIG], config[POS_VALUE]))
        if raw_value == "":
            return True
        new_value = convert(raw_value, config[POS_VALUE])
    except:
        print ("Error Setting Value, try again. Most likely a bad conversion.")
        return False

    config[POS_VALUE] = new_value

    return True


def guided_loop():
    # Find configs in Section that are "TYPE_INPUT"
    guided_configs = []
    for config in CONFIGS:
        if config[POS_TYPE] in MODE:
            guided_configs.append(config)

    for config in guided_configs:
        change_config(config)

    run_calc()


def edit_loop():
    while True:
        if not sections_loop():
            break


def display():
    run_calc()
    pprinttable(CONFIGS, [0, 1, 2, 3, 4])

    print ("Display")


def report():
    print("Report")


def save():
    print("Save")


def change_mode():
    print ("\t(1)\tSimple Mode")
    print ("\t(2)\tReference Mode")

    selection = raw_input("\t-- Select Mode -- : ")

    if selection in ("1", "2"):
        if selection == "1":
            MODE.remove(TYPE_REFERENCE)
        else:
            MODE.append(TYPE_REFERENCE)
    else:
        print ("Invalid Mode. Current Mode: " + MODE)


def action_loop():
    actions = (("Guided Config", "g"), ("Display", "d"), ("Edit", "e"), ("Save", "s"), ("Mode", "m"), ("Report", "r"),
               ("Quit", "q"))

    def validate(choice):
        for action in actions:
            if choice == action[1]:
                return True

    for action in actions:
        print ("({1})\t{0}".format(action[0], action[1]))

    selection = raw_input(SELECT_SECTION)

    if validate(selection):
        print("Good choice %s" % selection)
        if selection == "q":
            return False
        elif selection == "g":
            guided_loop()
            return True
        elif selection == "e":
            edit_loop()
            return True
        elif selection == "d":
            display()
            return True
        elif selection == "s":
            save()
            return True
        elif selection == "m":
            change_mode()
            return True
        elif selection == "r":
            report()
            return True
        else:
            return True
    else:
        print("No Good, try again.")
        return True


def left(field, length):
    diff = length - len(str(field))
    return str(field) + " " * diff


def center(field, length):
    diff = length - len(str(field))
    return " " * (diff / 2) + str(field) + " " * (length - len(str(field)) - (diff / 2))


def right(field, length):
    diff = length - len(str(field))
    return " " * diff + str(field)


def pprinttable(rows, fields):
    if len(rows) > 0:
        # headers = HEADER._fields
        headers = HEADER
        lens = []
        for field in fields:
            lens.append(len(headers[field]))

        for row in rows:
            inc = 0
            for field in fields:
                if isinstance(row[field], int) or isinstance(row[field], float) or isinstance(row[field], long):
                    if lens[inc] < 16:
                        lens[inc] = 16
                elif isinstance(row[field], list) or isinstance(row[field], tuple):
                    size = 2
                    for i in range(len(row[field])):
                        size += len(row[field][i]) + 3
                    if size > lens[inc]:
                        lens[inc] = size
                else:
                    if len(row[field]) > lens[inc]:
                        lens[inc] = len(row[field])
                inc += 1

        headerRowSeparator = ""
        headerRow = ""
        for loc in range(len(fields)):
            headerRowSeparator = headerRowSeparator + "|" + "=" * lens[loc]
            headerRow = headerRow + "|" + center(headers[fields[loc]], lens[loc])

        headerRowSeparator = headerRowSeparator + "|"
        headerRow = headerRow + "|"

        print headerRowSeparator
        print headerRow
        print headerRowSeparator

        for row in rows:
            inc = 0
            recordRow = ""
            for field in fields:
                if isinstance(row[field], int) or isinstance(row[field], float) or isinstance(row[field], long):
                    recordRow = recordRow + "|" + right(row[field], lens[inc])
                else:
                    recordRow = recordRow + "|" + left(row[field], lens[inc])
                inc += 1
            recordRow = recordRow + "|"

            print recordRow

        print headerRowSeparator


def main():
    # parser = optparse.OptionParser(usage="usage: %prog [options]")

    # login_options_group = OptionGroup(parser, "To specify credentials please use \"-e\" OR \"-u\" and \"-p'\"")
    # login_options_group.add_option("-u", "--user", dest="user", default="admin", help="Optional user ID to use for authentication. Default is 'admin'")
    # login_options_group.add_option("-p", "--password", dest="password", default="admin", help="Optional password to use for authentication. Default is 'admin'")
    # login_options_group.add_option("-e", "--credentials-file", dest="credentials_file", help="Optional file with user credentials separated by new line.")
    # parser.add_option_group(login_options_group)

    # parser.add_option("-t", "--port", dest="port", default="8080", help="Optional port number for Ambari server. Default is '8080'. Provide empty string to not use port.")
    # parser.add_option("-s", "--protocol", dest="protocol", default="http", help="Optional support of SSL. Default protocol is 'http'")
    # parser.add_option("--unsafe", action="store_true", dest="unsafe", help="Skip SSL certificate verification.")
    # parser.add_option("-a", "--action", dest="action", help="Script action: <get>, <set>, <delete>")
    # parser.add_option("-l", "--host", dest="host", help="Server external host name")
    # parser.add_option("-n", "--cluster", dest="cluster", help="Name given to cluster. Ex: 'c1'")
    # parser.add_option("-c", "--config-type", dest="config_type", help="One of the various configuration types in Ambari. Ex: core-site, hdfs-site, mapred-queue-acls, etc.")
    # parser.add_option("-b", "--version-note", dest="version_note", default="", help="Version change notes which will help to know what has been changed in this config. This value is optional and is used for actions <set> and <delete>.")
    #
    # config_options_group = OptionGroup(parser, "To specify property(s) please use \"-f\" OR \"-k\" and \"-v'\"")
    # config_options_group.add_option("-f", "--file", dest="file", help="File where entire configurations are saved to, or read from. Supported extensions (.xml, .json>)")
    # config_options_group.add_option("-k", "--key", dest="key", help="Key that has to be set or deleted. Not necessary for 'get' action.")
    # config_options_group.add_option("-v", "--value", dest="value", help="Optional value to be set. Not necessary for 'get' or 'delete' actions.")
    # parser.add_option_group(config_options_group)
    #
    # (options, args) = parser.parse_args()

    # Setup Base defaults
    run_calc()
    
    while True:
        if not action_loop():
            break


main()
