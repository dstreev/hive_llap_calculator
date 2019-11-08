#!/usr/bin/env python

# use this to parse the Ambari Layout Report that's generated with:
# http://${AMBARI_HOST_PORT}/api/v1/clusters/${CLUSTER_NAME}/hosts?fields=Hosts/host_name,host_components,Hosts/ip,Hosts/total_mem,Hosts/os_arch,Hosts/os_type,Hosts/rack_info,Hosts/cpu_count,Hosts/disk_info,metrics/disk,Hosts/ph_cpu_count

import optparse
import logging
import sys
import json
from common import pprinttable

logger = logging.getLogger('LLAPConfig')

def get_hostname( item ):
    host_info = item["Hosts"]
    return host_info["host_name"]


def is_component( item, componentName ):
    components = item["host_components"]
    for component in components:
        for ckey, cvalue in component.items():
            if ckey == "HostRoles":
                for hkey, hvalue in cvalue.items():
                    if hkey == "component_name":
                        if hvalue == componentName:
                            return True
    return False


def report( layoutFile ):
    layout = json.loads(open (layoutFile).read())
    items = layout['items']

    hosttable = gen_hosttable( items )

    rpt_hosttable( hosttable )
    rpt_totals( hosttable )

def gen_hosttable( items ):
    records = []

    for item in items:
        record = []
        host = item["Hosts"]
        record.append(host["host_name"])
        record.append(host["cpu_count"])
        record.append(host["os_type"])
        record.append(host["total_mem"] / (1024 * 1024))
        record.append(host["rack_info"])

        record.append(is_component(item, "DATANODE"))
        record.append(is_component(item, "NODEMANAGER"))
        records.append(record)

    return records

def rpt_hosttable ( hosttable ):
        # master = datanode & compute
    fields = [[0,"Host"], [1,"CPU Count"], [2,"OS"], [3,"Memory"], [4,"Rack"], [5,"Data Node"], [6,"Compute Node"]]
    pprinttable(hosttable, fields)


def rpt_totals ( hosttable ):
    totalFields = [[0,"Type"],[1,"Count"],[2, "OS"],[3,"CPU-Min"], [4,"CPU-Max"], [5,"Mem-Min"],[6,"Mem-Max"]]
    totalType = []

    datanodes = ["Data Nodes", 0, [], 10000, 0, 100000, 0]
    for record in hosttable:
        if record[5]:
            datanodes[1] += 1
            if (record[2] not in datanodes[2]):
                datanodes[2].append(record[2])
            # CPU Min
            if record[1] < datanodes[3]:
                datanodes[3] = record[1]
            # CPU Max
            if record[1] > datanodes[4]:
                datanodes[4] = record[1]
            # Mem Min
            if record[3] < datanodes[5]:
                datanodes[5] = record[3]
            # Mem Max
            if record[3] > datanodes[6]:
                datanodes[6] = record[3]

    totalType.append(datanodes)

    computeNodes = ["Compute Nodes", 0, [], 10000, 0, 100000, 0]
    for record in hosttable:
        if record[6]:
            computeNodes[1] += 1
            if (record[2] not in computeNodes[2]):
                computeNodes[2].append(record[2])
            # CPU Min
            if record[1] < computeNodes[3]:
                computeNodes[3] = record[1]
            # CPU Max
            if record[1] > computeNodes[4]:
                computeNodes[4] = record[1]
            # Mem Min
            if record[3] < computeNodes[5]:
                computeNodes[5] = record[3]
            # Mem Max
            if record[3] > computeNodes[6]:
                computeNodes[6] = record[3]

    totalType.append(computeNodes)

    pprinttable(totalType, totalFields)


def main():
    # global ambari_integration
    global cluster
    # global version_note
    # global ambari_accessor_api

    parser = optparse.OptionParser(usage="usage: %prog [options]")

    parser.add_option("-l", "--ambari-layout", dest="ambari_layout", help=".")

    (options, args) = parser.parse_args()

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    if options.ambari_layout:
        report(options.ambari_layout)

main()
