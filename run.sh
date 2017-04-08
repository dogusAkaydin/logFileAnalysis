#!/usr/bin/env bash

#clear ; ./src/process_log.py ./log_input/logAll.txt dummyForHosts.txt dummyForResources.txt
#clear ; ./src/process_log.py ./log_input/log.txt dummyForHosts.txt dummyForResources.txt
clear ; ./src/process_log.py ./log_input/log.txt ./log_output/hosts.txt ./log_output/resources.txt ./log_output/hours.txt ./log_output/blocked.txt

