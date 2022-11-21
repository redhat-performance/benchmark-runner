# ocp4.11: solved mssql securityContext permission issue
oc adm policy add-scc-to-group restricted system:authenticated --context admin mssql-db
