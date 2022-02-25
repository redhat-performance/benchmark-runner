QUAY_USERNAME={{ quay_username }}
QUAY_PASSWORD={{ quay_password }}
oc get secret pull-secret -n openshift-config -o json | jq -r '.data.".dockerconfigjson"' | base64 -d > global-pull-secret.json
QUAY_AUTH=$(echo -n "${QUAY_USERNAME}:${QUAY_PASSWORD}" | base64 -w 0)
podman login quay.io -u $QUAY_USERNAME -p $QUAY_PASSWORD
QUAY_AUTH=$(cat /run/user/$(id -u)/containers/auth.json | jq -r '.auths["quay.io"].auth')
jq --arg QUAY_AUTH "$QUAY_AUTH" '.auths += {"quay.io/openshift-cnv": {"auth":$QUAY_AUTH,"email":""}}' global-pull-secret.json > global-pull-secret.json.tmp
mv -f global-pull-secret.json.tmp global-pull-secret.json
oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=global-pull-secret.json
rm -f global-pull-secret.json
oc wait mcp master worker --for condition=updated --timeout=20m
