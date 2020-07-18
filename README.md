# Hive LLAP Calculator

Memory / Configuration Calculator for Hive LLAP.

## Change Log

| Date | Change | Issues Link |
| :------ | :----- | :--- |
| 2020-07-17 | Moved up 'pmem' check to recommendation for all configs. | [#19](https://github.com/dstreev/hive_llap_calculator/issues/19) |
| 2019-11-21 | Added ability to define separate Concurrency Queue | [#17](https://github.com/dstreev/hive_llap_calculator/issues/17) |
| 2019-11-15 | Displays, defaults and auto guide. Reverted Issue #14 after more research | [#16](https://github.com/dstreev/hive_llap_calculator/issues/16) |
| 2019-11-07 | Change threshold to property for: `hive.llap.daemon.memory.per.instance.mb`. Default Percent for Executors increased to 100 | [#14](https://github.com/dstreev/hive_llap_calculator/issues/14) [#15](https://github.com/dstreev/hive_llap_calculator/issues/15) | 
| 2019-10-30 | Added Rules to Save Action | |
| 2019-10-29 | Added Rule to check imbalance of cores and memory | |
| 2019-10-29 | Added support for pulling current values from Ambari Blueprint | [#3](https://github.com/dstreev/hive_llap_calculator/issues/3) |
| 2019-10-16 | Added Safety Valve for Daemons over 256Gb. Grace space to help reduce YARN container KILLs | |
| 2019-10-09 | Added Issue/Solution Description for Daemon Sizes over 256Gb | |
| 2019-09-19 | Added integration with 'working' values on initial collection with ambari integration. Allow mods to LLAP Min Task Allocation.  Ability to control output display columns (see m:mode). Save to File. Initial Error Printouts | [#5](https://github.com/dstreev/hive_llap_calculator/issues/5) [#6](https://github.com/dstreev/hive_llap_calculator/issues/6) [#8](https://github.com/dstreev/hive_llap_calculator/issues/8) [#11](https://github.com/dstreev/hive_llap_calculator/issues/11) [#12](https://github.com/dstreev/hive_llap_calculator/issues/12)|
| 2019-09-18 | Add Min check for LLAP Daemon Heap.  This value must be no less then 4gb * Number of Executors configured | [#1](https://github.com/dstreev/hive_llap_calculator/issues/1) |
|2019-09-17 | Changed the method for calculating total memory and resources for LLAP in the Cluster.  We use to use a 'percentage' of the cluster as a starting point for calculating the number of LLAP nodes.  This was a little cryptic.  The new method asks how many 'nodes' you want to run LLAP on.  The assumption now is that LLAP will consume the whole node.  So memory calculations start from the available YARN memory on a node and not a 'percentage' of that memory. | [#2](https://github.com/dstreev/hive_llap_calculator/issues/2) [#4](https://github.com/dstreev/hive_llap_calculator/issues/4) |

## Assumptions

- Tested on:
    - Mac OS X iTerm and Terminal
    - CentOS 7 bash
- Python 2.7+
- Calculator for Hive 3+ LLAP (HDP 3+) (May work for Hive 2 LLAP, but not tested)

## Limitations

This tool does NOT support 'heterogenous' environment calculations.  Calculations are based on a 'homogenous' compute configuration.  If you have a 'heterogenous' compute environment, limit the calculations to a subset of 'heterogenous' nodes where LLAP daemons will run.  In this scenario, the calculations for Queue sizes and overall footprint percentages will NOT be accurate.  Please use the numbers provided as a base to calculate those values for the full cluster.

## Directions

Run

```
./config_llap.py
```

Follow the prompts.

'Ambari Config List' will produce commands that can be run with [Ambari's Command Interface](ambari_configs.py)

You'll need to create a few environment variables to support running the Ambari command outputs:
- AMBARI_HOST
- AMBARI_PORT
- CLUSTER_NAME

Use a 'credentials' file for User/Password information for Ambari.  Create a file in your ${HOME} directory called `.ambari-credentials`

The contents should be 2 lines. First line is the user, second is the password. NOTE: This user should be a 'local' account.  You may have issues with 'remote' accounts and/or SSO accounts.

```
david
password123
```

## Help
```
./config_llap.py --help
```
```
Usage: config_llap.py [options]

Options:
  -h, --help            show this help message and exit
  -t PORT, --port=PORT  Optional port number for Ambari server. Default is
                        '8080'. Provide empty string to not use port.
  -s PROTOCOL, --protocol=PROTOCOL
                        Optional support of SSL. Default protocol is 'http'
  --unsafe              Skip SSL certificate verification.
  -l HOST, --host=HOST  Server external host name
  -n CLUSTER, --cluster=CLUSTER
                        Name given to cluster. Ex: 'c1'
  -v VERSION_NOTE, --version-note=VERSION_NOTE
                        Version change notes which will help to know what has
                        been changed in this config. This value is optional
                        and is used for actions <set> and <delete>.
  -w WORKERS, --workers=WORKERS
                        How many worker nodes in the cluster?
  -m MEMORY, --memory=MEMORY
                        How much memory does each worker node have (GB)?
  -b AMBARI_BLUEPRINT, --ambari-blueprint=AMBARI_BLUEPRINT
                        Use an Ambari Blueprint to pull configs.

  To specify credentials please use "-e" OR "-u" and "-p'":
    -u USER, --user=USER
                        Optional user ID to use for authentication. Default is
                        'admin'
    -p PASSWORD, --password=PASSWORD
                        Optional password to use for authentication. Default
                        is 'admin'
    -e CREDENTIALS_FILE, --credentials-file=CREDENTIALS_FILE
                        Optional file with user credentials separated by new
                        line.
```
                        
## Ambari Integration
You can pull most of the current configurations from Ambari by supplying the following parameters
 - [--host, --port, --credentials-file, --cluster]

If you supply details of the cluster size with 

 - [--workers, --memory]

the system will estimate additional 'totals' for the current environment.  Which you can use for validation.

Example:
```
# Connecting to an Ambari Server basic configuration
./config_llap.py --host <ambari_host> --port <ambari_port> --cluster <cluster_name> --credentials-file credentials.txt --workers 50 --memory 256


# Connecting to an Ambari Server with a Self-Signed SSL Cert
./config_llap.py --host <ambari_host> --port <ambari_port> --cluster <cluster_name> --credentials-file credentials.txt -s https --unsafe --workers 50 --memory 256
```

## Notes

[Ambari-Config](./ambari_configs.py) is a copy of the 'configs.py' resource for Ambari-Server found at `/var/lib/ambari-server/resources/scripts` .  The version here was pulled from Ambari 2.7.3.0.