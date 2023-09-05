#!/bin/sh

set -eo pipefail

if [ "$ACORN_EVENT" = "delete" ]; then
  atlas dbusers delete --force ${DB_USER}
  atlas cluster delete --force test
  exit 0
fi

# Get Cluster
clusterName=$(atlas clusters list -o json | jq -r '.results[]|[.name]|.[]')
echo "ClusterName: ${clusterName}"

# Make sure the cluster was created correctly
if [ $? -ne 0 ]; then
  echo $result
  exit 1
fi

# Wait for Atlas to provide cluster's connection string
while true; do
  DB_ADDRESS=$(atlas cluster describe ${clusterName} -o json | jq -r .connectionStrings.standardSrv)
  echo ${DB_ADDRESS}
  if [ "${DB_ADDRESS}" = "null" ]; then
      sleep 2
  else
    break
  fi
done

# Allow database network access from current IP
atlas accessList create --currentIp

# Extract proto and host from address returned
DB_PROTO=$(echo $DB_ADDRESS | cut -d':' -f1)
DB_HOST=$(echo $DB_ADDRESS | cut -d'/' -f3)
echo "DB_ADDRESS: [${DB_ADDRESS}] / DB_PROTO:[${DB_PROTO}] / DB_HOST:[${DB_HOST}]"

# Print Mongo Connection URI
echo "MONGO_URI: ${DB_PROTO}://${DB_USER}:${DB_PASS}@@${DB_HOST}/?retryWrites=true&w=majority"

cat > /run/secrets/output<<EOF
services: atlas: {
  address: "${DB_HOST}"
  secrets: ["db-creds"]
  data: {
    proto: "${DB_PROTO}"
  }
}
secrets: "db-creds": {
  type: "basic"
  data: {
    username: "${DB_USER}"
    password: "${DB_PASS}"
  }
}
EOF
