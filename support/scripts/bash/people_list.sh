#!/usr/bin/env bash

source config.cfg

export URL=$HOST/PEOPLE/list

curl -X POST --data "api_key=$KEY" $URL #| jq '{ emails: .rows[].EMAIL, pids: .rows[].PEOPLE_ID }' 

