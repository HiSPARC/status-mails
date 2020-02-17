#!/bin/bash
# from github.com/sara-nl/jupyter/ 

url="https://api.hisparc.k8s.surfsara.nl/usermgmtapi/v1/jaas-ldap-rest/user/"
application="jaas-ldap-api"
source "geheim-api-token-niet-committen"
#key="GEHEIM"
input="users.csv"

while IFS=',' read -r f1 f2 f3 f4 f5
do
# Add user
curl -X PUT "$url" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -H "X-API-Application: $application" \
    -H "X-API-Key: $key" \
    --data @- <<END;
    {
       "givenName": "$f2", \
       "sn": "$f3",
       "cn": "$f1",
       "uid": "$f1",
       "userPassword": "$f4",
       "homeDirectory": "",
       "loginShell": "",
       "mail": "$f5",
       "employeeType": "portal"
    }
END

    done < "$input"
