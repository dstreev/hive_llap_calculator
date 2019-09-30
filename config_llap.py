#!/usr/bin/env python

import optparse
from optparse import OptionGroup
import logging
import sys
import os
import json
import readline
from ambari_configs import api_accessor, get_properties, set_properties
from cStringIO import StringIO
import math

logger = logging.getLogger('LLAPConfig')

TF = ("true", "false")
KB = 1024

# SSL_ON = False
SSL_CMD = ""

TYPE_INPUT = "simple"
TYPE_CALC = "calc"
TYPE_REFERENCE = "extended"
# TYPE_THRESHOLD = "threshold"

# Yarn Sizing
YARN_MEMORY_PERCENT = 80
LLAP_CACHE_PERCENTAGE = 50

# Configuration

# [ Short Desc, Type, Section, Config, Value, Current Value, Options, Long Desc ]
HEADER = ["Short Desc", "Type", "Section", "Config", "Value", "Current Value", "Options", "Long Desc"]

# Positions
# LOCATION,DISPLAY_ORDER
POS_SHORT_DESC = [0,"Short Desc"]
POS_TYPE = [1,"Type"]
POS_SECTION = [2,"Section"]
POS_CONFIG = [3,"Config"]
POS_VALUE = [4,"Value"]
POS_CUR_VALUE = [5,"Current Value"]
POS_OPTIONS = [6,"Options"]
POS_LONG_DESC = [7,"Long Desc"]
POS_DELTA = [8, "Delta"]

ALL_DISPLAY_COLUMNS = [POS_SHORT_DESC,POS_TYPE,POS_SECTION,POS_CONFIG, \
                       POS_VALUE,POS_CUR_VALUE,POS_OPTIONS,POS_LONG_DESC,POS_DELTA]

DISPLAY_COLUMNS = [POS_SHORT_DESC, POS_TYPE, POS_SECTION, POS_CONFIG, \
                   POS_VALUE, POS_CUR_VALUE]

# Sections
YARN_SITE = ("YARN Configuration", "yarn-site")
HIVE_INTERACTIVE_SITE = ("LLAP Configuration", "hive-interactive-site")
HIVE_INTERACTIVE_ENV = ("LLAP Environment", "hive-interactive-env")
TEZ_INTERACTIVE_SITE = ("LLAP Tez Configuration", "tez-interactive-site")
HOST_ENV = ("Cluster Host Configuration", "host-env")
THRESHOLD_ENV = ("Calculation Thresholds", "threshold-env")
CLUSTER_ENV = ("Cluster Environment", "")

VALID_AMBARI_SECTIONS = (YARN_SITE, HIVE_INTERACTIVE_SITE, HIVE_INTERACTIVE_ENV, TEZ_INTERACTIVE_SITE)

SECTIONS = (HOST_ENV, THRESHOLD_ENV, YARN_SITE, HIVE_INTERACTIVE_SITE, HIVE_INTERACTIVE_ENV, TEZ_INTERACTIVE_SITE)

# Environment
WORKER_MEMORY_GB = ["Node Memory Footprint(GB)", TYPE_INPUT, HOST_ENV,
                    "", 32, 32, (), "", 0]
WORKER_COUNT = ["Number of Cluster Worker Nodes", TYPE_INPUT, HOST_ENV,
                "", 30, 30, (), "", 0]
WORKER_CORES = ["YARN Resource CPU-vCores", TYPE_INPUT, YARN_SITE, "yarn.nodemanager.resource.cpu-vcores", 4, 4, (), "", 0]

# Thresholds
PERCENT_OF_HOST_MEM_FOR_YARN = ["Percent of Host Memory for YARN NodeManager", TYPE_REFERENCE, THRESHOLD_ENV, "", 80, None, (), "","na"]
# PERCENT_OF_CLUSTER_FOR_LLAP = ["Percent of Cluster for LLAP", TYPE_CALC, THRESHOLD_ENV, "", 50, None]
# PERCENT_OF_NODE_FOR_LLAP_MEM = ["Percent of NodeManager Memory for LLAP", TYPE_REFERENCE, THRESHOLD_ENV, "", 90, None]
PERCENT_OF_LLAP_FOR_CACHE = ["Percent of LLAP Memory for Cache", TYPE_REFERENCE, THRESHOLD_ENV, "", 50, None, (), "","na"]
PERCENT_OF_CORES_FOR_EXECUTORS = ["Percent of Cores for LLAP Executors", TYPE_REFERENCE, THRESHOLD_ENV, "", 80, None, (), "","na"]
MAX_HEADROOM_GB = ["MAX LLAP Headroom Value(GB)", TYPE_REFERENCE, THRESHOLD_ENV, "", 12, None, (), "","na"]
LLAP_MIN_MB_TASK_ALLOCATION = ["LLAP Task Min MB Allocation", TYPE_REFERENCE, THRESHOLD_ENV, "", 4096, None, (), "","na"]
PERCENT_OF_DAEMON_CONTAINER_MEM_MB_FOR_HEADROOM = ["Percent of Daemon Container Memory(MB) for Headroom",
                                                   TYPE_REFERENCE, THRESHOLD_ENV, "", 20, None, (), "","na"]
PERCENT_OF_EXECUTORS_FOR_IO_THREADPOOL = ["Percent of Executors for IO Threadpool", TYPE_REFERENCE,
                                          THRESHOLD_ENV, "", 100, None, (), "","na"]

# YARN
YARN_NM_RSRC_MEM_MB = ["Node Manager Memory(MB)", TYPE_CALC, YARN_SITE,
                       "yarn.nodemanager.resource.memory-mb", 13107, 13107, (), "", 0]
YARN_SCH_MAX_ALLOC_MEM_MB = ["Yarn Max Mem Allocation(MB)", TYPE_CALC, YARN_SITE,
                             "yarn.scheduler.maximum-allocation-mb", 11927, 11927, (), "", 0]
YARN_SCH_MIN_ALLOC_MEM_MB = ["Yarn Min Mem Allocation(MB)", TYPE_REFERENCE, YARN_SITE,
                             "yarn.scheduler.minimum-allocation-mb", 2048, 2048, (), "", 0]

DIVIDER = ["", "", "", "", "", "", "", "", ""]
THRESHOLDS =    [" --  Threshold DETAILS -- ", "", "", "", "", "", "", "", ""]
CLUSTER_DETAILS =   ["  --  CLUSTER DETAILS -- ", "", "", "", "", "", "", "", ""]
YARN_ENV =      ["    --  YARN DETAILS --", "", "", "", "", "", "", "", ""]
HIVE_ENV =      ["    --  HIVE DETAILS --", "", "", "", "", "", "", "", ""]
TOTALS = ["> Totals", "", "", "", "", "", "", "", ""]


# Hive Interactive Site
HIVE_LLAP_QUEUE = ["YARN Queue", TYPE_INPUT, HIVE_INTERACTIVE_SITE,
                   "hive.llap.daemon.queue.name", "llap", "llap", (), "","na"]
TEZ_CONTAINER_SIZE_MB = ["TEZ Container Size", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                         "hive.tez.container.size", KB * 4, KB * 4, (), "Tez container size when LLAP is run with hive.execution.mode=container, which launches container instances for the job.",0]
LLAP_DAEMON_CONTAINER_MEM_MB = ["Daemon Memory(MB)", TYPE_CALC, HIVE_INTERACTIVE_SITE,
                                "hive.llap.daemon.yarn.container.mb", 11796, 11796, (), "", 0]
LLAP_CACHE_MEM_MB = ["Cache(MB)", TYPE_CALC, HIVE_INTERACTIVE_SITE,
                     "hive.llap.io.memory.size", KB * 4, KB * 4, (), "", 0]
LLAP_OBJECT_CACHE_ENABLED = ["Object Cache Enabled?", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                             "hive.llap.object.cache.enabled", "true", "true",
                             TF, "Cache objects (plans, hashtables, etc) in LLAP","na"]
LLAP_MEMORY_MODE = ["Memory Mode", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                    "hive.llap.io.memory.mode", "cache", "cache", ("cache", "allocator", "none"), "","na"]
LLAP_IO_ENABLED = ["Cache Enabled?", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                   "hive.llap.io.enabled", "true", "true", TF, "","na"]
LLAP_IO_ALLOCATOR_NMAP_ENABLED = ["Direct I/O cache enabled?", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                                  "hive.llap.io.allocator.mmap", "false", "false", TF,
                                  "Whether ORC low-level cache should use memory mapped allocation (direct I/O)","na"]
LLAP_IO_ALLOCATOR_NMAP_PATH = ["Direct I/O cache path", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                               "hive.llap.io.allocator.mmap.path", "", "", (), "","na"]

LLAP_NUM_EXECUTORS_PER_DAEMON = ["Num of Executors", TYPE_CALC, HIVE_INTERACTIVE_SITE,
                                 "hive.llap.daemon.num.executors", 12, 12, (), "",0]

LLAP_IO_THREADPOOL = ["I/O Threadpool", TYPE_CALC, HIVE_INTERACTIVE_SITE,
                      "hive.llap.io.threadpool.size", 12, 12, (), "", 0]

# Hive Interactive Size (Custom)
LLAP_PREWARMED_ENABLED = ["Prewarmed Containers", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                          "hive.prewarm.enabled", "false", "false", TF, "", "na"]
LLAP_PREWARM_NUM_CONTAINERS = ["Number of prewarmed Containers", TYPE_REFERENCE, HIVE_INTERACTIVE_SITE,
                               "hive.prewarm.numcontainers", 1, 0, (), "", 1]

# Hive Interactive Env
LLAP_NUM_NODES = ["Daemon Count", TYPE_INPUT, HIVE_INTERACTIVE_ENV,
                  "num_llap_nodes", 1, 1, (), "", 0]
LLAP_NUM_NODES_ALT = ["Daemon Count(legacy)", TYPE_CALC, HIVE_INTERACTIVE_ENV,
                  "num_llap_nodes_for_llap_daemons", 1, 1, (), "", 0]
LLAP_CONCURRENCY = ["Query Concurrency", TYPE_INPUT, HIVE_INTERACTIVE_SITE,
                    "hive.server2.tez.sessions.per.default.queue", 2, 2, (), "", 0]
LLAP_AM_DAEMON_HEAP_MB = ["AM Heap for Daemons", TYPE_REFERENCE, HIVE_INTERACTIVE_ENV,
                          "hive_heapsize", 4096, 4096, (), "Could be 2048, but defaults to 4096 in Ambari", 0]
LLAP_HEADROOM_MEM_MB = ["Heap Headroom", TYPE_CALC, HIVE_INTERACTIVE_ENV,
                        "llap_headroom_space", 2048, 2048, (), "", 0]
LLAP_DAEMON_HEAP_MEM_MB = ["Daemon Heap size(MB)", TYPE_CALC, HIVE_INTERACTIVE_ENV,
                           "llap_heap_size", 8192, 8192, (), "", 0]

# TEZ Interactive site
TEZ_AM_MEM_MB = ["TEZ AM Container size(MB) DAG Submission", TYPE_REFERENCE, TEZ_INTERACTIVE_SITE,
                 "tez.am.resource.memory.mb", 4 * KB, 4 * KB, (), "", 0]

# Total Section
TOTAL_MEM_FOOTPRINT = ["Total Memory Footprint", TYPE_CALC, CLUSTER_ENV,
                       "", 0, 0, (), "", 0]
TOTAL_LLAP_DAEMON_FOOTPRINT = ["Total LLAP Daemon Memory Footprint", TYPE_CALC, CLUSTER_ENV,
                               "", 0, 0, (), "", 0]
TOTAL_LLAP_OTHER_FOOTPRINT = ["Total LLAP Other Memory Footprint", TYPE_CALC, CLUSTER_ENV,
                              "", 0, 0, (), "", 0]
TOTAL_LLAP_MEM_FOOTPRINT = ["Total LLAP Memory Footprint", TYPE_CALC, CLUSTER_ENV,
                            "", 0, 0, (), "", 0]
LLAP_QUEUE_MIN_REQUIREMENT = ["LLAP Minimum YARN Queue Capacity % Requirement", TYPE_CALC, CLUSTER_ENV,
                              "", 0, 0, (), "", 0]

LOGICAL_CONFIGS = [
    CLUSTER_DETAILS,
    WORKER_MEMORY_GB,
    WORKER_COUNT,
    WORKER_CORES,
    DIVIDER,
    THRESHOLDS,
    PERCENT_OF_HOST_MEM_FOR_YARN,
    # PERCENT_OF_CLUSTER_FOR_LLAP,
    # PERCENT_OF_NODE_FOR_LLAP_MEM,
    LLAP_MIN_MB_TASK_ALLOCATION,
    PERCENT_OF_LLAP_FOR_CACHE,
    PERCENT_OF_CORES_FOR_EXECUTORS,
    PERCENT_OF_DAEMON_CONTAINER_MEM_MB_FOR_HEADROOM,
    PERCENT_OF_EXECUTORS_FOR_IO_THREADPOOL,
    MAX_HEADROOM_GB,
    DIVIDER,
    YARN_ENV,
    YARN_NM_RSRC_MEM_MB,
    YARN_SCH_MAX_ALLOC_MEM_MB,
    YARN_SCH_MIN_ALLOC_MEM_MB,
    HIVE_LLAP_QUEUE,
    TOTALS,
    TOTAL_MEM_FOOTPRINT,
    DIVIDER,
    HIVE_ENV,
    LLAP_NUM_NODES,
    LLAP_NUM_NODES_ALT,
    LLAP_CONCURRENCY,
    TEZ_AM_MEM_MB,
    LLAP_NUM_EXECUTORS_PER_DAEMON,
    DIVIDER,
    LLAP_AM_DAEMON_HEAP_MB,
    LLAP_DAEMON_CONTAINER_MEM_MB,
    LLAP_DAEMON_HEAP_MEM_MB,
    LLAP_HEADROOM_MEM_MB,
    LLAP_CACHE_MEM_MB,
    DIVIDER,
    LLAP_MEMORY_MODE,
    LLAP_IO_ENABLED,
    LLAP_OBJECT_CACHE_ENABLED,
    DIVIDER,

    LLAP_IO_THREADPOOL,
    DIVIDER,

    LLAP_IO_ALLOCATOR_NMAP_ENABLED,
    LLAP_IO_ALLOCATOR_NMAP_PATH,
    TEZ_CONTAINER_SIZE_MB,
    DIVIDER,

    LLAP_PREWARMED_ENABLED,
    LLAP_PREWARM_NUM_CONTAINERS,
    DIVIDER,

    TOTALS,
    TOTAL_LLAP_DAEMON_FOOTPRINT,
    TOTAL_LLAP_OTHER_FOOTPRINT,
    TOTAL_LLAP_MEM_FOOTPRINT,


    DIVIDER,
    LLAP_QUEUE_MIN_REQUIREMENT]

AMBARI_CONFIGS = [
    YARN_NM_RSRC_MEM_MB,

    YARN_SCH_MAX_ALLOC_MEM_MB,
    YARN_SCH_MIN_ALLOC_MEM_MB,
    WORKER_CORES,
    HIVE_LLAP_QUEUE,
    LLAP_QUEUE_MIN_REQUIREMENT,

    LLAP_NUM_NODES,
    LLAP_NUM_NODES_ALT,

    LLAP_CONCURRENCY,
    TEZ_AM_MEM_MB,

    LLAP_NUM_EXECUTORS_PER_DAEMON,

    LLAP_AM_DAEMON_HEAP_MB,
    LLAP_DAEMON_CONTAINER_MEM_MB,
    LLAP_DAEMON_HEAP_MEM_MB,
    LLAP_HEADROOM_MEM_MB,
    LLAP_CACHE_MEM_MB,

    LLAP_MEMORY_MODE,
    LLAP_IO_ENABLED,
    LLAP_OBJECT_CACHE_ENABLED,

    LLAP_IO_THREADPOOL,

    LLAP_IO_ALLOCATOR_NMAP_ENABLED,
    LLAP_IO_ALLOCATOR_NMAP_PATH,

    TEZ_CONTAINER_SIZE_MB,

    LLAP_PREWARMED_ENABLED,
    LLAP_PREWARM_NUM_CONTAINERS
]

SELECT_TASK = "Select Task -- : "
SELECT_SECTION = "Select Section -- : "
SELECT_MODE = "Select Mode -- : "
SELECT_ACTION = "Select Action --: "
SELECT_CONFIG = "Select Config -- : "
ENTER_RETURN = " <enter> - to go back"
ENTER_CONTINUE = " <enter> - to continue"
AMBARI_CFG_CMD = "./ambari_configs.py --host=${{AMBARI_HOST}} --port=${{AMBARI_PORT}} {0} --cluster=${{CLUSTER_NAME}}" + \
                    " --credentials-file=${{HOME}}/.ambari-credentials --action=set --config-type={1}" + \
                    " --key={2} --value={3}"

ERROR_MESSAGES = []

cluster = ""
ambari_accessor_api = None
version_note = ""
ambari_integration = True

MODE = [TYPE_INPUT]


class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


def run_calc(position):
    # print ("running calc")

    ## YARN
    #########
    # YARN_NM_RSRC_MEM_MB
    YARN_NM_RSRC_MEM_MB[position] = WORKER_MEMORY_GB[position] * KB * PERCENT_OF_HOST_MEM_FOR_YARN[position] / 100

    ## LLAP
    #########
    # LLAP_NUM_NODES
    # LLAP_NUM_NODES[position] = WORKER_COUNT[position] * PERCENT_OF_CLUSTER_FOR_LLAP[position] / 100
    # Sync Values.
    LLAP_NUM_NODES_ALT[position] = LLAP_NUM_NODES[position]

    # LLAP_NUM_EXECUTORS_PER_DAEMON
    LLAP_NUM_EXECUTORS_PER_DAEMON[position] = WORKER_CORES[position] * \
                                               PERCENT_OF_CORES_FOR_EXECUTORS[position] / 100

    # Total LLAP Other Footprint
    # TODO: Add support for PREWARMED CONTAINERS.
    TOTAL_LLAP_OTHER_FOOTPRINT[position] = LLAP_CONCURRENCY[position] * TEZ_AM_MEM_MB[position]

    OTHER_MEM_PER_NODE =  TOTAL_LLAP_OTHER_FOOTPRINT[position] / LLAP_NUM_NODES[position]

    # LLAP_DAEMON_CONTAINER_MEM_MB
    LLAP_DAEMON_CONTAINER_MEM_MB[position] = YARN_NM_RSRC_MEM_MB[position] - OTHER_MEM_PER_NODE

    # YARN_SCH_MAX_ALLOC_MEM_MB
    # Adding a percent for a little clearance on mem settings.
    YARN_SCH_MAX_ALLOC_MEM_MB[position] = LLAP_DAEMON_CONTAINER_MEM_MB[position] + 1

    # LLAP_HEADROOM_MEM_MB
    # =IF((E37*0.2) > (12*1024),12*1024,E37*0.2)
    if LLAP_DAEMON_CONTAINER_MEM_MB[position] * PERCENT_OF_DAEMON_CONTAINER_MEM_MB_FOR_HEADROOM[position] / 100 \
            > MAX_HEADROOM_GB[position] * KB:
        LLAP_HEADROOM_MEM_MB[position] = MAX_HEADROOM_GB[position] * KB
    else:
        LLAP_HEADROOM_MEM_MB[position] = LLAP_DAEMON_CONTAINER_MEM_MB[position] * \
                                          PERCENT_OF_DAEMON_CONTAINER_MEM_MB_FOR_HEADROOM[position] / 100

    # LLAP_DAEMON_HEAP_MEM_MB
    LLAP_DAEMON_HEAP_MEM_MB[position] = (LLAP_DAEMON_CONTAINER_MEM_MB[position] - LLAP_HEADROOM_MEM_MB[position]) * \
                                         (100 - PERCENT_OF_LLAP_FOR_CACHE[position]) / 100

    # This ensures that a minimum of 4Gb per Executor is available in the Daemon Heap.
    if LLAP_DAEMON_HEAP_MEM_MB[position] < LLAP_NUM_EXECUTORS_PER_DAEMON[position] * LLAP_MIN_MB_TASK_ALLOCATION[position]:
        LLAP_DAEMON_HEAP_MEM_MB[position] = LLAP_NUM_EXECUTORS_PER_DAEMON[position] * LLAP_MIN_MB_TASK_ALLOCATION[position]


    # LLAP_CACHE_MEM_MB
    LLAP_CACHE_MEM_MB[position] = LLAP_DAEMON_CONTAINER_MEM_MB[position] - LLAP_DAEMON_HEAP_MEM_MB[position]

    # LLAP_IO_THREADPOOL
    LLAP_IO_THREADPOOL[position] = LLAP_NUM_EXECUTORS_PER_DAEMON[position] * \
                                    PERCENT_OF_EXECUTORS_FOR_IO_THREADPOOL[position] / 100
    run_totals_calc(position)


def run_totals_calc(position):
    # Total LLAP Daemon Footprint
    # True Daemon NM Memory use needs to round to the yarn.min.container.size.
    # LLAP_DAEMON_CONTAINER_MEM_MB[position]
    # YARN_SCH_MIN_ALLOC_MEM_MB[position]
    # Round Up!
    factor = math.ceil(float(LLAP_DAEMON_CONTAINER_MEM_MB[position]) / YARN_SCH_MIN_ALLOC_MEM_MB[position])

    TOTAL_LLAP_DAEMON_FOOTPRINT[position] = LLAP_NUM_NODES[position] * factor * YARN_SCH_MIN_ALLOC_MEM_MB[position] \
                                             + LLAP_AM_DAEMON_HEAP_MB[position]

    # # Total LLAP Other Footprint
    # # TODO: Add support for PREWARMED CONTAINERS.
    # TOTAL_LLAP_OTHER_FOOTPRINT[position] = LLAP_CONCURRENCY[position] * TEZ_AM_MEM_MB[position]

    # Total LLAP Memory Footprint
    TOTAL_LLAP_MEM_FOOTPRINT[position] = TOTAL_LLAP_DAEMON_FOOTPRINT[position] + TOTAL_LLAP_OTHER_FOOTPRINT[position]

    # Total Cluster Memory Footprint
    TOTAL_MEM_FOOTPRINT[position] = YARN_NM_RSRC_MEM_MB[position] * WORKER_COUNT[position]

    # Total LLAP Yarn Queue Requirement (Percent of Root Queue)
    LLAP_QUEUE_MIN_REQUIREMENT[position] = round(float(TOTAL_LLAP_MEM_FOOTPRINT[position]) / \
                                                  TOTAL_MEM_FOOTPRINT[position] * 100, 2)
    calc_deltas()
    check_for_issues()

def calc_deltas():
    WORKER_MEMORY_GB[POS_DELTA[0]] = WORKER_MEMORY_GB[POS_VALUE[0]] - WORKER_MEMORY_GB[POS_CUR_VALUE[0]]
    WORKER_COUNT[POS_DELTA[0]] = WORKER_COUNT[POS_VALUE[0]] - WORKER_COUNT[POS_CUR_VALUE[0]]
    WORKER_CORES[POS_DELTA[0]] = WORKER_CORES[POS_VALUE[0]] - WORKER_CORES[POS_CUR_VALUE[0]]
    YARN_NM_RSRC_MEM_MB[POS_DELTA[0]] = YARN_NM_RSRC_MEM_MB[POS_VALUE[0]] - YARN_NM_RSRC_MEM_MB[POS_CUR_VALUE[0]]
    YARN_SCH_MAX_ALLOC_MEM_MB[POS_DELTA[0]] = YARN_SCH_MAX_ALLOC_MEM_MB[POS_VALUE[0]] - YARN_SCH_MAX_ALLOC_MEM_MB[POS_CUR_VALUE[0]]
    YARN_SCH_MIN_ALLOC_MEM_MB[POS_DELTA[0]] = YARN_SCH_MIN_ALLOC_MEM_MB[POS_VALUE[0]] - YARN_SCH_MIN_ALLOC_MEM_MB[POS_CUR_VALUE[0]]
    TOTAL_MEM_FOOTPRINT[POS_DELTA[0]] = TOTAL_MEM_FOOTPRINT[POS_VALUE[0]] - TOTAL_MEM_FOOTPRINT[POS_CUR_VALUE[0]]

    LLAP_NUM_NODES[POS_DELTA[0]] = LLAP_NUM_NODES[POS_VALUE[0]] - LLAP_NUM_NODES[POS_CUR_VALUE[0]]
    LLAP_NUM_NODES_ALT[POS_DELTA[0]] = LLAP_NUM_NODES_ALT[POS_VALUE[0]] - LLAP_NUM_NODES_ALT[POS_CUR_VALUE[0]]
    LLAP_CONCURRENCY[POS_DELTA[0]] = LLAP_CONCURRENCY[POS_VALUE[0]] - LLAP_CONCURRENCY[POS_CUR_VALUE[0]]
    TEZ_AM_MEM_MB[POS_DELTA[0]] = TEZ_AM_MEM_MB[POS_VALUE[0]] - TEZ_AM_MEM_MB[POS_CUR_VALUE[0]]
    LLAP_NUM_EXECUTORS_PER_DAEMON[POS_DELTA[0]] = LLAP_NUM_EXECUTORS_PER_DAEMON[POS_VALUE[0]] - LLAP_NUM_EXECUTORS_PER_DAEMON[POS_CUR_VALUE[0]]
    LLAP_AM_DAEMON_HEAP_MB[POS_DELTA[0]] = LLAP_AM_DAEMON_HEAP_MB[POS_VALUE[0]] - LLAP_AM_DAEMON_HEAP_MB[POS_CUR_VALUE[0]]
    LLAP_DAEMON_CONTAINER_MEM_MB[POS_DELTA[0]] = LLAP_DAEMON_CONTAINER_MEM_MB[POS_VALUE[0]] - LLAP_DAEMON_CONTAINER_MEM_MB[POS_CUR_VALUE[0]]
    LLAP_DAEMON_HEAP_MEM_MB[POS_DELTA[0]] = LLAP_DAEMON_HEAP_MEM_MB[POS_VALUE[0]] - LLAP_DAEMON_HEAP_MEM_MB[POS_CUR_VALUE[0]]
    LLAP_HEADROOM_MEM_MB[POS_DELTA[0]] = LLAP_HEADROOM_MEM_MB[POS_VALUE[0]] - LLAP_HEADROOM_MEM_MB[POS_CUR_VALUE[0]]
    LLAP_CACHE_MEM_MB[POS_DELTA[0]] = LLAP_CACHE_MEM_MB[POS_VALUE[0]] - LLAP_CACHE_MEM_MB[POS_CUR_VALUE[0]]

    LLAP_IO_THREADPOOL[POS_DELTA[0]] = LLAP_IO_THREADPOOL[POS_VALUE[0]] - LLAP_IO_THREADPOOL[POS_CUR_VALUE[0]]
    TEZ_CONTAINER_SIZE_MB[POS_DELTA[0]] = TEZ_CONTAINER_SIZE_MB[POS_VALUE[0]] - TEZ_CONTAINER_SIZE_MB[POS_CUR_VALUE[0]]
    LLAP_PREWARM_NUM_CONTAINERS[POS_DELTA[0]] = LLAP_PREWARM_NUM_CONTAINERS[POS_VALUE[0]] - LLAP_PREWARM_NUM_CONTAINERS[POS_CUR_VALUE[0]]
    TOTAL_LLAP_DAEMON_FOOTPRINT[POS_DELTA[0]] = TOTAL_LLAP_DAEMON_FOOTPRINT[POS_VALUE[0]] - TOTAL_LLAP_DAEMON_FOOTPRINT[POS_CUR_VALUE[0]]
    TOTAL_LLAP_OTHER_FOOTPRINT[POS_DELTA[0]] = TOTAL_LLAP_OTHER_FOOTPRINT[POS_VALUE[0]] - TOTAL_LLAP_OTHER_FOOTPRINT[POS_CUR_VALUE[0]]
    TOTAL_LLAP_MEM_FOOTPRINT[POS_DELTA[0]] = TOTAL_LLAP_MEM_FOOTPRINT[POS_VALUE[0]] - TOTAL_LLAP_MEM_FOOTPRINT[POS_CUR_VALUE[0]]
    LLAP_QUEUE_MIN_REQUIREMENT[POS_DELTA[0]] = LLAP_QUEUE_MIN_REQUIREMENT[POS_VALUE[0]] - LLAP_QUEUE_MIN_REQUIREMENT[POS_CUR_VALUE[0]]

def check_for_issues():
    del ERROR_MESSAGES[:]
    if LLAP_DAEMON_HEAP_MEM_MB[POS_VALUE[0]] > LLAP_DAEMON_CONTAINER_MEM_MB[POS_VALUE[0]]:
        message = [LLAP_DAEMON_CONTAINER_MEM_MB[POS_SHORT_DESC[0]] + ":" + \
                   str(LLAP_DAEMON_CONTAINER_MEM_MB[POS_VALUE[0]]) + \
                   " can't be less than " + LLAP_DAEMON_HEAP_MEM_MB[POS_SHORT_DESC[0]] + ":" + \
                   str(LLAP_DAEMON_HEAP_MEM_MB[POS_VALUE[0]]),
                   ["Decrease " + LLAP_NUM_EXECUTORS_PER_DAEMON[POS_SHORT_DESC[0]], \
                    "Decrease " + LLAP_MIN_MB_TASK_ALLOCATION[POS_SHORT_DESC[0]]]]
        ERROR_MESSAGES.append(message)


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


def convert(value, original):
    if isinstance(original, int):
        return int(value)
    if isinstance(original, long):
        return long(value)
    if isinstance(original, str):
        return str(value)


def filtered_sections():
    f_sections = []
    for section in SECTIONS:
        for config in LOGICAL_CONFIGS:
            if config[POS_SECTION[0]] == section and config[POS_TYPE[0]] in MODE:
                f_sections.append(section)
                break

    return f_sections


def sections_loop():
    while True:
        # List Sections
        # print ("sections")
        inc = 1
        for section in filtered_sections():
            print (" {0} - {1}".format(inc, section[0]))
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
        if selection > len(filtered_sections()) or selection < 1:
            # print (GO_BACK)
            return

        if not section_loop(selection):
            break


def section_loop(selection):
    while True:
        # Identify Section
        # print ("section")
        section_choice = ""
        inc = 1
        for section in filtered_sections():
            if selection == inc:
                section_choice = section
            inc += 1

        # Find configs in Section that are "TYPE_INPUT"
        section_configs = []
        for config in LOGICAL_CONFIGS:
            if isinstance(config[POS_SECTION[0]], tuple) and config[POS_SECTION[0]][1] == section_choice[1] and config[POS_TYPE[0]] in MODE:
                section_configs.append(config)

        config = select_config(section_choice, section_configs)

        if not config:
            return True

        if not change_config(config):
            return True
        else:
            run_calc(POS_VALUE[0])


def select_config(section, section_configs):
    # List Filtered Sections
    # print ("select")
    print (chr(27) + "[2J")
    print ("===================================")
    print ("   " + section[0])
    print ("===================================")
    inc = 1
    for config in section_configs:
        print (" {0} - {1}: [{2}]".format(inc, config[POS_SHORT_DESC[0]], config[POS_VALUE[0]]))
        inc += 1

    print (ENTER_RETURN)
    print ("===================================")
    # Pick Config to Edit
    try:
        choice = int(raw_input(SELECT_CONFIG))
    except ValueError:
        # print (GO_BACK)
        return True

        # Check selection boundaries
    if choice > (inc) or choice < 1:
        # print (GO_BACK)
        return True

    # Enter New Value
    inc = 1
    # target_config = []
    for config in section_configs:
        if choice == inc:
            return config
        inc += 1


def change_config(config):
    # print ("change")

    try:
        raw_value = raw_input(">>> {0} \"{1}\" [{2}]: ".format(config[POS_SHORT_DESC[0]], config[POS_CONFIG[0]], config[POS_VALUE[0]]))

        if raw_value == "":
            return True
        new_value = convert(raw_value, config[POS_VALUE[0]])
    except:
        # print ("Error Setting Value, try again. Most likely a bad conversion.")
        return False

    config[POS_VALUE[0]] = new_value

    return True


def guided_loop():
    # Find configs in Section that are "TYPE_INPUT"
    print(chr(27) + "[2J")
    print ("")
    environment_status()
    print ("===================================")
    print ("      Guided Configuration      ")
    print ("")
    print ("- Enter value for each setting.")
    print ("- Press 'enter' to keep current.")
    print ("")
    print ("===================================")

    guided_configs = []
    for config in LOGICAL_CONFIGS:
        if config[POS_TYPE[0]] in MODE:
            guided_configs.append(config)

    for config in guided_configs:
        change_config(config)

    run_calc(POS_VALUE[0])
    logical_display()


def edit_loop():
    while True:
        print(chr(27) + "[2J")
        print ("")
        environment_status()
        print ("===================================")
        print ("        Edit Configurations        ")
        print ("===================================")

        # List Sections
        # print ("sections")
        inc = 1
        for section in filtered_sections():
            print (" {0} - {1}".format(inc, section[0]))
            inc += 1

        print (ENTER_RETURN)
        print ("===================================")
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
        if selection > len(filtered_sections()) or selection < 1:
            # print (GO_BACK)
            return

        if not section_loop(selection):
            break

        print ("===================================")


def logical_display():
    run_calc(POS_VALUE[0])

    global LOGICAL_CONFIGS
    pprinttable(LOGICAL_CONFIGS, DISPLAY_COLUMNS)

    print ("")
    environment_status()
    print ("")
    raw_input("press enter...")

def ambari_configs():
    run_calc(POS_VALUE[0])
    print(chr(27) + "[2J")
    print ("===================================")
    print ("       Ambari Configurations       ")
    print ("===================================")

    pprinttable(AMBARI_CONFIGS, DISPLAY_COLUMNS)

    ambaricalls = ambariRestCalls()
    print ("===================================")
    print ("  Ambari REST Call Configurations  ")
    print ("===================================")
    if ERROR_MESSAGES > 0:
        environment_status()
    else:
        for line in ambaricalls:
            print line

    manual = manualCfgs()
    if len(manual) > 0:
        print ("===================================")
        print ("       Manual Configurations       ")
        print ("===================================")

        for cfg in manual:
            print ("Manual Configuration: {0} [{1}]".format(cfg[POS_SHORT_DESC[0]], cfg[POS_VALUE[0]]))

    print ("")
    raw_input("press enter...")

def manualCfgs():
    manual = []
    for cfg in AMBARI_CONFIGS:
        if cfg[POS_SECTION[0]] not in VALID_AMBARI_SECTIONS:
            manual.append(cfg)

    return manual

def ambariRestCalls():
    ambariConfigs = []
    for cfg in AMBARI_CONFIGS:
        if cfg[POS_SECTION[0]] in VALID_AMBARI_SECTIONS:
            ambariConfigs.append(AMBARI_CFG_CMD.format(SSL_CMD, cfg[POS_SECTION[0]][1], cfg[POS_CONFIG[0]], cfg[POS_VALUE[0]]))

    return ambariConfigs


def save():
    lclErrors = getErrors()
    if len(lclErrors) > 0:
        environment_status()
        print ("Fix issues to get script output!")
        print (raw_input(ENTER_CONTINUE))
    else:
        out_file_base = raw_input("Enter Filename(without Extension):")
        myFile = open(out_file_base + ".sh", "w")

        myFile.write("export AMBARI_HOST=<host>\n")
        myFile.write("export AMBARI_PORT=<port>\n")
        myFile.write("export CLUSTER_NAME=<clustername>\n")

        for line in ambariRestCalls():
            myFile.write(line)
            myFile.write('\n')

        myFile.close();

        myFile = open(out_file_base + ".txt", "w")

        # myFile.writelines(buildtable(AMBARI_CONFIGS, DISPLAY_COLUMNS))
        for line in buildtable(AMBARI_CONFIGS, DISPLAY_COLUMNS):
            myFile.write(line)
            myFile.write('\n')

        manual = manualCfgs()
        if len(manual) > 0:
            for line in manual:
                myFile.writelines("Manual Configuration: {0} [{1}]".format(line[POS_SHORT_DESC[0]], line[POS_VALUE[0]]))
                myFile.write('\n')

        myFile.close()
        print ("")
        print ("Saved to: " + out_file_base + ".txt - Configuration Grid")
        print ("Saved to: " + out_file_base + ".sh  - Ambari Configuration REST Script")
        print ("")
        print (raw_input(ENTER_CONTINUE))

def getDisplayColumns():
    rtn = []
    for item in DISPLAY_COLUMNS:
        rtn.append(item[1])
    return rtn


def change_mode():
    while True:
        print(chr(27) + "[2J")
        print ("")
        environment_status()
        print ("===================================")
        print ("            Change Mode       ")
        print ("===================================")
        print (" 1 - Simple Mode")
        print (" 2 - Reference Mode(expose additional settings)")
        print ("")
        print ("===================================")
        print ("    Toggle Columns for Display")
        print ("===================================")
        print (" 3 - Short Desc")
        print (" 4 - Type")
        print (" 5 - Section")
        print (" 6 - Config")
        print (" 7 - Value")
        print (" 8 - Current Value")
        print (" 9 - Options")
        print (" 10 - Long Desc")
        print (" 11 - Delta")
        print ("===================================")
        print (ENTER_RETURN)

        try:
            raw_selection = raw_input(SELECT_MODE)
            if raw_selection == "":
                break
            selection = int(raw_selection)
        except ValueError:
            break

        if selection is not None and selection in (1,2):
            if selection == 1:
                if TYPE_REFERENCE in MODE:
                    MODE.remove(TYPE_REFERENCE)
            else:
                if TYPE_REFERENCE not in MODE:
                    MODE.append(TYPE_REFERENCE)
        elif selection is not None and selection in (3,4,5,6,7,8,9,10,11):
            selectionadjusted = selection - 3
            for i in ALL_DISPLAY_COLUMNS:
                if i[0] == selectionadjusted:
                    if len(DISPLAY_COLUMNS) == 0:
                        DISPLAY_COLUMNS.append(i)
                    elif i in DISPLAY_COLUMNS:
                        DISPLAY_COLUMNS.remove(i)
                    else:
                        spot = i[0]
                        iter = 0
                        for i2 in DISPLAY_COLUMNS:
                            if i2[0] > spot:
                                DISPLAY_COLUMNS.insert(iter,i)
                                break
                            else:
                                iter += 1
                                if iter >= len(DISPLAY_COLUMNS):
                                    DISPLAY_COLUMNS.insert(iter,i)
                                    break
        else:
            break
        print ("________________________________")
        print ("")

def getErrors():
    ERRORS = []
    if len(ERROR_MESSAGES) > 0:
        ERRORS.append ("********************* ERRORS *********************")
        for message in ERROR_MESSAGES:
            ERRORS.append ("Issue: ")
            ERRORS.append ("\t\t" + message[0])
            ERRORS.append ("Options:")
            for opt in message[1]:
                ERRORS.append ("\t\t" + opt)
            ERRORS.append("    ------------------------")
        ERRORS.append ("**************************************************")
    return ERRORS


def environment_status():
    print ("Ambari Integration On:\t("+str(ambari_integration)+")")
    print ("         Current mode:\t*"+str(MODE)+"*")
    print ("      Display Columns:\t" + str(getDisplayColumns()))
    lclErrors = getErrors()
    if len(lclErrors) > 0:
        for line in lclErrors:
            print (line)

def action_loop():
    actions = (
        ("Guided Config", "g"), (), ("Logical Display", "l"), ("Ambari Config List", "a"), (), ("Edit", "e"),
        ("Save", "s"),
        (), ("Mode (expose additional settings)", "m"), (), ("Quit", "q"))

    def validate(choice):
        for action in actions:
            if len(action) > 1 and choice == action[1]:
                return True
    print(chr(27) + "[2J")
    print ("")
    environment_status()
    print ("===================================")
    print ("         MAIN Action Menu          ")
    print ("===================================")
    for action in actions:
        if len(action)>1:
            print (" {1} - {0}".format(action[0], action[1]))
        else:
            print ("       -----------")
    print ("===================================")

    selection = raw_input(SELECT_ACTION)

    if validate(selection):
        # print("Good choice %s" % selection)
        if selection == "q":
            return False
        elif selection == "g":
            guided_loop()
            return True
        elif selection == "e":
            edit_loop()
            return True
        elif selection == "l":
            logical_display()
            return True
        elif selection == "a":
            ambari_configs()
            return True
        elif selection == "s":
            save()
            return True
        elif selection == "m":
            change_mode()
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


def populate_current():
    if not ambari_integration:
        return False

    section_configs = {}
    for configs in VALID_AMBARI_SECTIONS:
        with Capturing() as output:
            get_properties(cluster, configs[1], [], ambari_accessor_api)
        lclJson = "".join(output)
        section_configs[configs[1]] = json.loads(lclJson)

    for scKey in section_configs.keys():
        section_config = section_configs[scKey]

        for configs in VALID_AMBARI_SECTIONS:
            for ambariConfig in AMBARI_CONFIGS:
                if ambariConfig[POS_SECTION[0]][1] == scKey:
                    try:
                    # set_config(ambariConfig, POS_CUR_VALUE[0])
                        ambariConfig[POS_CUR_VALUE[0]] = convert(section_config['properties'][ambariConfig[POS_CONFIG[0]]], ambariConfig[POS_CUR_VALUE[0]])
                        # Set Calc Values to the same.
                        ambariConfig[POS_VALUE[0]] = convert(section_config['properties'][ambariConfig[POS_CONFIG[0]]], ambariConfig[POS_CUR_VALUE[0]])
                    except:
                        print("Skipping property lookup: " + str(ambariConfig[POS_CUR_VALUE[0]]))

    if LLAP_NUM_NODES[POS_CUR_VALUE[0]] != LLAP_NUM_NODES_ALT[POS_CUR_VALUE[0]]:
        print ("WARNING: In your current Ambari Configuration, similar legacy configurations are not in Sync.  These need to be in sync!!!!\n\t" +
               LLAP_NUM_NODES[POS_CONFIG[0]] + ":" + str(LLAP_NUM_NODES[POS_CUR_VALUE[0]]) + "\n\t" +
               LLAP_NUM_NODES_ALT[POS_CONFIG[0]] + ":" + str(LLAP_NUM_NODES_ALT[POS_CUR_VALUE[0]]) +
               "\nOur calculations for the current configuration may be off until these are corrected.")
        raw_input("press enter to continue...")

    run_totals_calc(POS_CUR_VALUE[0])
    # Reset the Calc Values based on initial Ambari Values.
    run_calc(POS_VALUE[0])


def pprinttable(rows, fields):
    output = buildtable(rows, fields)
    for line in output:
        print line

def buildtable(rows, fields):
    str_list = []

    if len(rows) > 0:
        # headers = HEADER._fields
        # headers = HEADER
        lens = []
        for field in fields:
            lens.append(len(field[1]))

        for row in rows:
            inc = 0
            for field in fields:
                if isinstance(row[field[0]], (int, float, long)):
                    if lens[inc] < 16:
                        lens[inc] = 16
                elif isinstance(row[field[0]], (list, tuple)):
                    size = 2
                    for i in range(len(row[field[0]])):
                        size += len(row[field[0]][i]) + 3
                    if size > lens[inc]:
                        lens[inc] = size
                else:
                    if row[field[0]] is not None and (len(row[field[0]]) > lens[inc]):
                        lens[inc] = len(row[field[0]])
                inc += 1

        headerRowSeparator = ""
        headerRow = ""
        for loc in range(len(fields)):
            headerRowSeparator = headerRowSeparator + "|" + "=" * (lens[loc]+1)
            headerRow = headerRow + "| " + center([fields[loc][1]], lens[loc])

        headerRowSeparator = headerRowSeparator + "|"
        headerRow = headerRow + "|"

        str_list.append(headerRowSeparator)
        # print headerRowSeparator
        str_list.append(headerRow)
        # print headerRow
        str_list.append(headerRowSeparator)
        # print headerRowSeparator

        for row in rows:
            inc = 0
            recordRow = ""
            for field in fields:
                if isinstance(row[field[0]], int) or isinstance(row[field[0]], float) or isinstance(row[field[0]], long):
                    recordRow = recordRow + "| " + right(row[field[0]], lens[inc])
                else:
                    recordRow = recordRow + "| " + left(row[field[0]], lens[inc])
                inc += 1
            recordRow = recordRow + "|"

            str_list.append(recordRow)
            # print recordRow

        str_list.append(headerRowSeparator)
        # print headerRowSeparator
    return str_list


def main():
    global ambari_integration
    global cluster
    global version_note
    global ambari_accessor_api

    parser = optparse.OptionParser(usage="usage: %prog [options]")

    login_options_group = OptionGroup(parser, "To specify credentials please use \"-e\" OR \"-u\" and \"-p'\"")
    login_options_group.add_option("-u", "--user", dest="user", default="admin", help="Optional user ID to use for authentication. Default is 'admin'")
    login_options_group.add_option("-p", "--password", dest="password", default="admin", help="Optional password to use for authentication. Default is 'admin'")
    login_options_group.add_option("-e", "--credentials-file", dest="credentials_file", help="Optional file with user credentials separated by new line.")
    parser.add_option_group(login_options_group)

    parser.add_option("-t", "--port", dest="port", default="8080", help="Optional port number for Ambari server. Default is '8080'. Provide empty string to not use port.")
    parser.add_option("-s", "--protocol", dest="protocol", default="http", help="Optional support of SSL. Default protocol is 'http'")
    parser.add_option("--unsafe", action="store_true", dest="unsafe", help="Skip SSL certificate verification.")
    # parser.add_option("-a", "--action", dest="action", help="Script action: <get>, <set>, <delete>")
    parser.add_option("-l", "--host", dest="host", help="Server external host name")
    parser.add_option("-n", "--cluster", dest="cluster", help="Name given to cluster. Ex: 'c1'")
    # parser.add_option("-c", "--config-type", dest="config_type", help="One of the various configuration types in Ambari. Ex: core-site, hdfs-site, mapred-queue-acls, etc.")
    parser.add_option("-b", "--version-note", dest="version_note", default="", help="Version change notes which will help to know what has been changed in this config. This value is optional and is used for actions <set> and <delete>.")
    #
    # config_options_group = OptionGroup(parser, "To specify property(s) please use \"-f\" OR \"-k\" and \"-v'\"")
    # config_options_group.add_option("-f", "--file", dest="file", help="File where entire configurations are saved to, or read from. Supported extensions (.xml, .json>)")
    # config_options_group.add_option("-k", "--key", dest="key", help="Key that has to be set or deleted. Not necessary for 'get' action.")
    # config_options_group.add_option("-v", "--value", dest="value", help="Optional value to be set. Not necessary for 'get' or 'delete' actions.")
    # parser.add_option_group(config_options_group)
    #

    parser.add_option("-w", "--workers", dest="workers", default="10", help="How many worker nodes in the cluster?")
    parser.add_option("-m", "--memory", dest="memory", default="32", help="How much memory does each worker node have (GB)?")

    (options, args) = parser.parse_args()

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    global SSL_CMD

    # options with default value
    if options.protocol:
        SSL_CMD += "-s "
        SSL_CMD += options.protocol

    if options.unsafe:
        SSL_CMD += " --unsafe"

    if not options.credentials_file and (not options.user or not options.password):
        ambari_integration = False
        logger.info("Ambari Credential information missing.  Running in standalone mode.")
        # parser.error("You should use option (-e) to set file with Ambari user credentials"
        #              " OR use (-u) username and (-p) password")

    if options.credentials_file:
        if os.path.isfile(options.credentials_file):
            try:
                with open(options.credentials_file) as credentials_file:
                    file_content = credentials_file.read()
                    login_lines = filter(None, file_content.splitlines())
                    if len(login_lines) == 2:
                        user = login_lines[0]
                        password = login_lines[1]
                    else:
                        logger.error("Incorrect content of {0} file. File should contain Ambari username and password separated by new line.".format(options.credentials_file))
                        return -1
            except Exception as e:
                logger.error("You don't have permissions to {0} file".format(options.credentials_file))
                return -1
        else:
            logger.error("File {0} doesn't exist or you don't have permissions.".format(options.credentials_file))
            return -1
    else:
        user = options.user
        password = options.password

    port = options.port
    protocol = options.protocol

    if options.workers:
        WORKER_COUNT[POS_VALUE[0]] = int(options.workers)
        WORKER_COUNT[POS_CUR_VALUE[0]] = int(options.workers)
    if options.memory:
        WORKER_MEMORY_GB[POS_VALUE[0]] = int(options.memory)
        WORKER_MEMORY_GB[POS_CUR_VALUE[0]] = int(options.memory)

    #options without default value
    if None in [options.host, options.cluster]:
        ambari_integration = False
        logger.info("Ambari Integration information missing.  Running in standalone mode.")
        # parser.error("One of required options is not passed")

    # action = options.action
    host = options.host
    cluster = options.cluster
    # config_type = options.config_type
    version_note = options.version_note

    if ambari_integration:
        ambari_accessor_api = api_accessor(host, user, password, protocol, port, options.unsafe)
        populate_current()

    # Setup Base defaults
    run_calc(POS_VALUE[0])

    while True:
        if not action_loop():
            break


main()
