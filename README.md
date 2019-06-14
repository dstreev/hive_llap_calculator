# Hive LLAP Calculator

Memory / Configuration Calculator for Hive LLAP.

## Assumptions

- Tested on:
    - Mac OS X iTerm and Terminal
    - CentOS 7 bash
- Python 2.7+
- Calculator for Hive 3+ LLAP (HDP 3+) (May work for Hive 2 LLAP, but not tested)

## Directions

Run

```
./config_llap.py
```

Follow the prompts.

'Ambari Config List' will produce commands that can be run with [Ambari's Command Interface](./ambari/configs.py)

You'll need to create a few environment variables:
- AMBARI_HOST
- AMBARI_PORT
- CLUSTER_NAME

Use a 'credentials' file for User/Password information for Ambari.  Create a file in your ${HOME} directory called `.ambari-credentials`

The contents should be 2 lines. First line is the user, second is the password.
```
david
password123
```