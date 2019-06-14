# Hive LLAP Calculator

Memory / Configuration Calculator for Hive LLAP.

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