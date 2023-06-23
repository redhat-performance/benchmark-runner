{
   "panels": [
      {
         "datasource": {
            "type": "datasource",
            "uid": "-- Mixed --"
         },
         "gridPos": {
            "h": 6,
            "w": 5,
            "x": 0,
            "y": 0
         },
         "id": 1,
         "options": {
            "content": "\n<p style=\"background-color:#000099;text-align: center;\" > > 100% new peak</p>\n<p style=\"background-color:#006600;text-align: center;color:black;\" > 90% - 100% of peak</p>\n<p style=\"background-color:#9fdf9f;text-align: center;color:black;\" > 80% -  90% of peak</p>\n<p style=\"background-color:#cc6600;text-align: center;color:black;\" > 50% -  80% of peak</p>\n<p style=\"background-color:#992600;text-align: center;\" > 0%  -  50% of peak</p>\n\n\n           ",
            "mode": "html"
         },
         "pluginVersion": "8.4.0-pre",
         "targets": [
            {
               "alias": "",
               "bucketAggs": [
                  {
                     "field": "timestamp",
                     "id": "2",
                     "settings": {
                        "interval": "auto"
                     },
                     "type": "date_histogram"
                  }
               ],
               "datasource": {
                  "type": "elasticsearch",
                  "uid": "cd4b9568-576c-4528-b200-89b91a098410"
               },
               "metrics": [
                  {
                     "id": "1",
                     "type": "count"
                  }
               ],
               "query": "",
               "refId": "A",
               "timeField": "timestamp"
            }
         ],
         "title": "Workloads Legend",
         "type": "text"
      },
      {
         "datasource": {
            "type": "datasource",
            "uid": "-- Mixed --"
         },
         "description": "",
         "gridPos": {
            "h": 6,
            "w": 5,
            "x": 19,
            "y": 0
         },
         "id": 2,
         "options": {
            "content": "![Cloud Governance](https://www.cielhr.com/wp-content/uploads/2019/10/PerformancewSpace-1080x675.png \"Tooltip Text\")\n",
            "mode": "markdown"
         },
         "pluginVersion": "8.4.0-pre",
         "targets": [
            {
               "alias": "",
               "bucketAggs": [
                  {
                     "field": "timestamp",
                     "id": "2",
                     "settings": {
                        "interval": "auto"
                     },
                     "type": "date_histogram"
                  }
               ],
               "datasource": {
                  "type": "elasticsearch",
                  "uid": "cd4b9568-576c-4528-b200-89b91a098410"
               },
               "metrics": [
                  {
                     "id": "1",
                     "type": "count"
                  }
               ],
               "query": "",
               "refId": "A",
               "timeField": "timestamp"
            }
         ],
         "title": "placeholder",
         "type": "text"
      },
      {
         "datasource": "Elasticsearch-ci-status",
         "description": "OVN - 09/19",
         "fieldConfig": {
            "defaults": {
               "color": {
                  "fixedColor": "#132dc3",
                  "mode": "fixed"
               },
               "custom": {
                  "fillOpacity": 85,
                  "lineWidth": 0
               },
               "mappings": [ ],
               "thresholds": {
                  "mode": "absolute",
                  "steps": [
                     {
                        "color": "green",
                        "value": null
                     }
                  ]
               }
            },
            "overrides": [ ]
         },
         "gridPos": {
            "h": 6,
            "w": 24,
            "x": 0,
            "y": 6
         },
         "id": 3,
         "interval": "1d",
         "links": [
            {
               "targetBlank": true,
               "title": "OCP version",
               "url": "https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/"
            }
         ],
         "options": {
            "alignValue": "right",
            "legend": {
               "displayMode": "hidden",
               "placement": "bottom"
            },
            "mergeValues": true,
            "rowHeight": 0.84999999999999998,
            "showValue": "always",
            "tooltip": {
               "mode": "single"
            }
         },
         "pluginVersion": "8.4.0-pre",
         "targets": [
            {
               "alias": "Openshift",
               "bucketAggs": [
                  {
                     "field": "timestamp",
                     "id": "2",
                     "settings": {
                        "interval": "auto"
                     },
                     "type": "date_histogram"
                  }
               ],
               "hide": false,
               "metrics": [
                  {
                     "field": "ci_minutes_time",
                     "id": "1",
                     "settings": {
                        "script": "Integer.parseInt(\"0\"+doc[\"ocp_version.keyword\"].value.replace(\".\",\"\").replace(\"r\",\"\").replace(\"c\",\"\").replace(\"f\",\"\").replace(\"-\",\"\").replace(\"e\",\"1\").replace(\"c\",\"\").replace(\"r\",\"\"))"
                     },
                     "type": "max"
                  }
               ],
               "query": "_exists_:ocp_version AND ocp_version:$ocp_version",
               "refId": "A",
               "timeField": "timestamp"
            },
            {
               "alias": "CNV Nightly op.",
               "bucketAggs": [
                  {
                     "field": "timestamp",
                     "id": "2",
                     "settings": {
                        "interval": "auto"
                     },
                     "type": "date_histogram"
                  }
               ],
               "hide": false,
               "metrics": [
                  {
                     "field": "ci_minutes_time",
                     "id": "1",
                     "settings": {
                        "script": "(doc[\"cnv_version.keyword\"].value.indexOf(\" \") == -1) ? Integer.parseInt(\"0\"+doc[\"cnv_version.keyword\"].value.replace(\".\",\"\").replace(\"r\",\"\").replace(\"c\",\"\").replace(\"f\",\"\").replace(\"-\",\"\")) : 0"
                     },
                     "type": "max"
                  }
               ],
               "query": "_exists_:cnv_version AND ocp_version:$ocp_version",
               "refId": "C",
               "timeField": "timestamp"
            },
            {
               "alias": "KATA op.",
               "bucketAggs": [
                  {
                     "field": "timestamp",
                     "id": "2",
                     "settings": {
                        "interval": "auto"
                     },
                     "type": "date_histogram"
                  }
               ],
               "hide": false,
               "metrics": [
                  {
                     "field": "ci_minutes_time",
                     "id": "1",
                     "settings": {
                        "script": "(doc[\"kata_version.keyword\"].value.indexOf(\" \") == -1) ? Integer.parseInt(doc[\"kata_version.keyword\"].value.replace(\".\",\"\")) : 0"
                     },
                     "type": "max"
                  }
               ],
               "query": "_exists_:kata_version AND ocp_version:$ocp_version",
               "refId": "D",
               "timeField": "timestamp"
            },
            {
               "alias": "Kata rpm",
               "bucketAggs": [
                  {
                     "field": "timestamp",
                     "id": "2",
                     "settings": {
                        "interval": "auto"
                     },
                     "type": "date_histogram"
                  }
               ],
               "hide": false,
               "metrics": [
                  {
                     "field": "ci_minutes_time",
                     "id": "1",
                     "settings": {
                        "script": "Integer.parseInt(\"0\"+doc[\"kata_rpm_version.keyword\"].value.replace(\".\",\"\").replace(\"r\",\"\").replace(\"c\",\"\").replace(\"f\",\"\").replace(\"-\",\"\").replace(\"e\",\"1\").replace(\"c\",\"\").replace(\"r\",\"\"))"
                     },
                     "type": "max"
                  }
               ],
               "query": "_exists_:kata_rpm_version AND ocp_version:$ocp_version",
               "refId": "F",
               "timeField": "timestamp"
            },
            {
               "alias": "ODF op.",
               "bucketAggs": [
                  {
                     "field": "timestamp",
                     "id": "2",
                     "settings": {
                        "interval": "auto"
                     },
                     "type": "date_histogram"
                  }
               ],
               "hide": false,
               "metrics": [
                  {
                     "field": "ci_minutes_time",
                     "id": "1",
                     "settings": {
                        "script": "((doc[\"odf_version.keyword\"].size() != 0) ? ((doc[\"odf_version.keyword\"].value.indexOf(\" \") == -1) ? Integer.parseInt(\"0\"+doc[\"odf_version.keyword\"].value.replace(\".\",\"\").replace(\"r\",\"\").replace(\"c\",\"\").replace(\"f\",\"\").replace(\"-\",\"\")) : 0) : 0)"
                     },
                     "type": "max"
                  }
               ],
               "query": "_exists_:odf_version AND ocp_version:$ocp_version",
               "refId": "E",
               "timeField": "timestamp"
            },
            {
               "alias": "ODF # disks",
               "bucketAggs": [
                  {
                     "field": "timestamp",
                     "id": "2",
                     "settings": {
                        "interval": "auto"
                     },
                     "type": "date_histogram"
                  }
               ],
               "hide": false,
               "metrics": [
                  {
                     "field": "odf_disk_count",
                     "id": "1",
                     "settings": { },
                     "type": "max"
                  }
               ],
               "query": "ocp_version:$ocp_version",
               "refId": "B",
               "timeField": "timestamp"
            }
         ],
         "title": "Product Versions",
         "type": "state-timeline"
      },
      {
         "collapsed": true,
         "gridPos": {
            "h": 1,
            "w": 24,
            "x": 0,
            "y": 12
         },
         "id": 4,
         "panels": [
            {
               "datasource": "Elasticsearch-hammerdb-results",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 70,
                        "lineWidth": 0
                     },
                     "mappings": [ ],
                     "min": 0,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "dark-red"
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 50
                           },
                           {
                              "color": "super-light-green",
                              "value": 80
                           },
                           {
                              "color": "dark-green",
                              "value": 90
                           },
                           {
                              "color": "dark-blue",
                              "value": 100
                           }
                        ]
                     }
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 38,
                  "w": 24,
                  "x": 0,
                  "y": 13
               },
               "id": 33,
               "interval": "1d",
               "links": [
                  {
                     "targetBlank": true,
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&viewPanel=128"
                  }
               ],
               "options": {
                  "alignValue": "center",
                  "legend": {
                     "displayMode": "list",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "always",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "pluginVersion": "8.4.0-pre",
               "targets": [
                  {
                     "alias": "{{term db_type.keyword}}  : {{term current_worker}} threads : {{term kind.keyword}}:  {{term storage_type.keyword}}",
                     "bucketAggs": [
                        {
                           "field": "db_type.keyword",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "asc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "current_worker",
                           "id": "4",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "asc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "storage_type.keyword",
                           "id": "5",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "kind.keyword",
                           "id": "6",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "metrics": [
                        {
                           "field": "tpm",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "_exists_:tpm AND db_type:$db_type AND current_worker:$current_worker AND kind:$kind AND ocp_version:$ocp_version",
                     "refId": "A",
                     "timeField": "timestamp"
                  }
               ],
               "title": "HammerDB KTPM",
               "type": "state-timeline"
            }
         ],
         "title": "Hammerdb",
         "type": "row"
      },
      {
         "collapsed": true,
         "gridPos": {
            "h": 1,
            "w": 24,
            "x": 0,
            "y": 13
         },
         "id": 5,
         "panels": [
            {
               "datasource": "Elasticsearch-uperf-results",
               "description": "Lower is better",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 70,
                        "lineWidth": 0
                     },
                     "decimals": 1,
                     "mappings": [ ],
                     "max": -1,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "dark-blue"
                           },
                           {
                              "color": "dark-green",
                              "value": 1
                           },
                           {
                              "color": "super-light-green",
                              "value": 10
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 20
                           },
                           {
                              "color": "dark-red",
                              "value": 50
                           }
                        ]
                     }
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 15,
                  "w": 24,
                  "x": 0,
                  "y": 52
               },
               "id": 41,
               "interval": "1d",
               "links": [
                  {
                     "targetBlank": true,
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&viewPanel=129"
                  }
               ],
               "options": {
                  "alignValue": "center",
                  "legend": {
                     "displayMode": "list",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "always",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "targets": [
                  {
                     "alias": "msg size: {{term read_message_size}} :{{term num_threads}}th: {{term kind.keyword}}",
                     "bucketAggs": [
                        {
                           "field": "read_message_size",
                           "id": "4",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "asc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "num_threads",
                           "id": "5",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "asc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "kind.keyword",
                           "id": "6",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "metrics": [
                        {
                           "field": "norm_ltcy",
                           "id": "1",
                           "settings": { },
                           "type": "avg"
                        }
                     ],
                     "query": "_exists_:norm_ltcy AND read_message_size:(64 OR 1024 OR 8192) AND num_threads:(1) AND test_type:rr AND norm_ltcy:<1000 AND kind:$kind  AND ocp_version:$ocp_version",
                     "refId": "A",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "msg size: {{term read_message_size}} :{{term num_threads}}th: {{term kind.keyword}}",
                     "bucketAggs": [
                        {
                           "field": "read_message_size",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "asc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "num_threads",
                           "id": "4",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "asc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "kind.keyword",
                           "id": "5",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "norm_ltcy",
                           "id": "1",
                           "settings": {
                              "script": "_value*8"
                           },
                           "type": "avg"
                        }
                     ],
                     "query": "_exists_:norm_ltcy AND read_message_size:(64 OR 1024 OR 8192) AND num_threads:(8) AND test_type:rr AND norm_ltcy:<1000 AND kind:$kind  AND ocp_version:$ocp_version",
                     "refId": "B",
                     "timeField": "timestamp"
                  }
               ],
               "title": "Uperf Latency (usecs)",
               "type": "state-timeline"
            },
            {
               "datasource": "Elasticsearch-uperf-results",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 70,
                        "lineWidth": 0
                     },
                     "decimals": 1,
                     "mappings": [ ],
                     "min": 0,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "semi-dark-red"
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 50
                           },
                           {
                              "color": "super-light-green",
                              "value": 80
                           },
                           {
                              "color": "dark-green",
                              "value": 90
                           },
                           {
                              "color": "dark-blue",
                              "value": 100
                           }
                        ]
                     }
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 15,
                  "w": 24,
                  "x": 0,
                  "y": 67
               },
               "id": 42,
               "interval": "1d",
               "links": [
                  {
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&viewPanel=129"
                  }
               ],
               "options": {
                  "alignValue": "center",
                  "legend": {
                     "displayMode": "list",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "always",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "targets": [
                  {
                     "alias": "msg size: {{term read_message_size}} :{{term num_threads}}th: {{term kind.keyword}}",
                     "bucketAggs": [
                        {
                           "field": "read_message_size",
                           "id": "4",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "asc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "num_threads",
                           "id": "5",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "asc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "kind.keyword",
                           "id": "6",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "metrics": [
                        {
                           "field": "norm_byte",
                           "id": "1",
                           "settings": {
                              "script": "_value*8/1000000000"
                           },
                           "type": "avg"
                        }
                     ],
                     "query": "_exists_:norm_ops AND read_message_size:(64 OR 1024 OR 8192) AND num_threads:(1 OR 8) AND test_type:stream AND kind:$kind  AND ocp_version:$ocp_version",
                     "refId": "A",
                     "timeField": "timestamp"
                  }
               ],
               "title": "Uperf Throughput (Gbits/s)",
               "type": "state-timeline"
            }
         ],
         "title": "Uperf",
         "type": "row"
      },
      {
         "collapsed": true,
         "gridPos": {
            "h": 1,
            "w": 24,
            "x": 0,
            "y": 14
         },
         "id": 6,
         "panels": [
            {
               "datasource": "Elasticsearch-vdbench-results",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 70,
                        "lineWidth": 0
                     },
                     "mappings": [ ],
                     "min": 0,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "dark-red"
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 50
                           },
                           {
                              "color": "light-green",
                              "value": 80
                           },
                           {
                              "color": "dark-green",
                              "value": 90
                           },
                           {
                              "color": "dark-blue",
                              "value": 100
                           }
                        ]
                     }
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 48,
                  "w": 24,
                  "x": 0,
                  "y": 83
               },
               "id": 49,
               "interval": "1d",
               "links": [
                  {
                     "targetBlank": true,
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=133"
                  },
                  {
                     "title": "scale  log link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=195"
                  }
               ],
               "options": {
                  "alignValue": "center",
                  "legend": {
                     "displayMode": "list",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "always",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "targets": [
                  {
                     "alias": "{{term Run.keyword}} : {{term Threads}}th : 1 {{term kind.keyword}}",
                     "bucketAggs": [
                        {
                           "field": "Run.keyword",
                           "id": "2",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "kind.keyword",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "Threads",
                           "id": "4",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "metrics": [
                        {
                           "field": "Rate",
                           "id": "1",
                           "type": "avg"
                        }
                     ],
                     "query": "!SCALE AND !Run.keyword=\"fillup\" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "A",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Total {{term kind.keyword}} Memory (GB) [384GB]",
                     "bucketAggs": [
                        {
                           "field": "kind.keyword",
                           "id": "6",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "total_Memory",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "!SCALE AND !Run.keyword=\"fillup\" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "B",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Total {{term kind.keyword}} %CPU [240 cores]",
                     "bucketAggs": [
                        {
                           "field": "kind.keyword",
                           "id": "6",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "total_CPU",
                           "id": "1",
                           "type": "max"
                        }
                     ],
                     "query": "!SCALE AND !Run.keyword=\"fillup\" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "C",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "{{term Run.keyword}} : {{term Threads}}th :{{term scale}} {{term kind.keyword}}s",
                     "bucketAggs": [
                        {
                           "field": "Run.keyword",
                           "id": "2",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "kind.keyword",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "Threads",
                           "id": "4",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "scale",
                           "id": "6",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "Rate",
                           "id": "1",
                           "type": "avg"
                        }
                     ],
                     "query": "SCALE AND !Run.keyword=\"fillup\" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "D",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Total {{term kind.keyword}} Memory (GB) [384GB]",
                     "bucketAggs": [
                        {
                           "field": "kind.keyword",
                           "id": "2",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "total_Memory",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "SCALE AND !Run.keyword=\"fillup\" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "E",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Total {{term kind.keyword}} %CPU [240 cores]",
                     "bucketAggs": [
                        {
                           "field": "kind.keyword",
                           "id": "2",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "total_CPU",
                           "id": "1",
                           "settings": { },
                           "type": "max"
                        }
                     ],
                     "query": "SCALE AND !Run.keyword=\"fillup\" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "F",
                     "timeField": "timestamp"
                  }
               ],
               "title": "vdbench (IOPS)",
               "type": "state-timeline"
            },
            {
               "datasource": "Elasticsearch-vdbench-results",
               "description": "Lower is better",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 70,
                        "lineWidth": 0
                     },
                     "decimals": 1,
                     "mappings": [ ],
                     "max": -1,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "dark-blue"
                           },
                           {
                              "color": "dark-green",
                              "value": 1
                           },
                           {
                              "color": "super-light-green",
                              "value": 10
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 20
                           },
                           {
                              "color": "dark-red",
                              "value": 50
                           }
                        ]
                     }
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 50,
                  "w": 24,
                  "x": 0,
                  "y": 131
               },
               "id": 50,
               "interval": "1d",
               "links": [
                  {
                     "targetBlank": true,
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&editPanel=133&from=now-45d&to=now"
                  }
               ],
               "options": {
                  "alignValue": "center",
                  "legend": {
                     "displayMode": "list",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "always",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "targets": [
                  {
                     "alias": "{{term Run.keyword}} : {{term Threads}}th : 1 {{term kind.keyword}}",
                     "bucketAggs": [
                        {
                           "field": "Run.keyword",
                           "id": "2",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "kind.keyword",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "Threads",
                           "id": "4",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "metrics": [
                        {
                           "field": "Resp",
                           "id": "1",
                           "type": "avg"
                        }
                     ],
                     "query": "!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "A",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "\"Total {{term kind.keyword}} Memory (GB) [384GB]",
                     "bucketAggs": [
                        {
                           "field": "kind.keyword",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "total_Memory",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "B",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Total {{term kind.keyword}} %CPU [240 cores]",
                     "bucketAggs": [
                        {
                           "field": "kind.keyword",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "metrics": [
                        {
                           "field": "total_CPU",
                           "id": "1",
                           "settings": { },
                           "type": "max"
                        }
                     ],
                     "query": "!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "D",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "{{term Run.keyword}} : {{term Threads}}th :{{term scale}} {{term kind.keyword}}s",
                     "bucketAggs": [
                        {
                           "field": "Run.keyword",
                           "id": "2",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "kind.keyword",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "Threads",
                           "id": "4",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "scale",
                           "id": "6",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "Resp",
                           "id": "1",
                           "type": "avg"
                        }
                     ],
                     "query": "SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "C",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Total {{term kind.keyword}} Memory (GB) [384GB]",
                     "bucketAggs": [
                        {
                           "field": "kind.keyword",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "total_Memory",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "E",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Total {{term kind.keyword}} %CPU [240 cores]",
                     "bucketAggs": [
                        {
                           "field": "kind.keyword",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "5",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "total_CPU",
                           "id": "1",
                           "settings": { },
                           "type": "max"
                        }
                     ],
                     "query": "SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version",
                     "refId": "F",
                     "timeField": "timestamp"
                  }
               ],
               "title": "vdbench Latency  (sec)",
               "type": "state-timeline"
            }
         ],
         "title": "Vdbench",
         "type": "row"
      },
      {
         "collapsed": true,
         "gridPos": {
            "h": 1,
            "w": 24,
            "x": 0,
            "y": 19
         },
         "id": 7,
         "panels": [
            {
               "datasource": "Elasticsearch-clusterbuster-cpusoaker-release-results",
               "description": "OVN - 09/19",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 70,
                        "lineWidth": 0
                     },
                     "mappings": [ ],
                     "min": 0,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "red"
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 50
                           },
                           {
                              "color": "super-light-green",
                              "value": 80
                           },
                           {
                              "color": "dark-green",
                              "value": 90
                           },
                           {
                              "color": "dark-blue",
                              "value": 100
                           }
                        ]
                     }
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 36,
                  "w": 24,
                  "x": 0,
                  "y": 261
               },
               "id": 57,
               "interval": "1d",
               "links": [
                  {
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=1659592686997&to=1663480686997&viewPanel=166"
                  }
               ],
               "options": {
                  "alignValue": "left",
                  "legend": {
                     "displayMode": "list",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "auto",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "targets": [
                  {
                     "alias": "pod: max",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "test_description.pods",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc'",
                     "refId": "A",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: max",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "test_description.pods",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata'",
                     "refId": "B",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "pod: Memory per pod (MB)",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "memory_per_pod",
                           "id": "6",
                           "settings": {
                              "script": "_value/1000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc'",
                     "refId": "C",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: Memory per kata  (MB)",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "memory_per_pod",
                           "id": "6",
                           "settings": {
                              "script": "_value/1000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata'",
                     "refId": "D",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "\"pod: start per seconds",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "pod_starts_per_second",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc'",
                     "refId": "E",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: start per seconds",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "pod_starts_per_second",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata'",
                     "refId": "F",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "pod: Iteration cpu sec",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "iterations_cpu_sec",
                           "id": "6",
                           "settings": {
                              "script": "_value/1000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc'",
                     "refId": "G",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: Iteration cpu sec",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "iterations_cpu_sec",
                           "id": "6",
                           "settings": {
                              "script": "_value/1000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata'",
                     "refId": "H",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "pod: Iteration sec",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "iterations_sec",
                           "id": "6",
                           "settings": {
                              "script": "_value/1000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc'",
                     "refId": "I",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: Iteration sec",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "datasource": {
                        "type": "elasticsearch",
                        "uid": "cd4b9568-576c-4528-b200-89b91a098410"
                     },
                     "hide": false,
                     "metrics": [
                        {
                           "field": "iterations_sec",
                           "id": "6",
                           "settings": {
                              "script": "_value/1000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata'",
                     "refId": "J",
                     "timeField": "timestamp"
                  }
               ],
               "title": "clusterbuster-cpusoaker [OVN - 09/19]",
               "type": "state-timeline"
            },
            {
               "datasource": "Elasticsearch-clusterbuster-files-release-results",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 70,
                        "lineWidth": 0
                     },
                     "mappings": [ ],
                     "min": 0,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "red"
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 50
                           },
                           {
                              "color": "super-light-green",
                              "value": 80
                           },
                           {
                              "color": "dark-green",
                              "value": 90
                           },
                           {
                              "color": "dark-blue",
                              "value": 100
                           }
                        ]
                     }
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 36,
                  "w": 24,
                  "x": 0,
                  "y": 297
               },
               "id": 58,
               "interval": "1d",
               "links": [
                  {
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150"
                  }
               ],
               "options": {
                  "alignValue": "left",
                  "legend": {
                     "displayMode": "list",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "auto",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "targets": [
                  {
                     "alias": "pod: create: filesize 4096",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "metrics": [
                        {
                           "field": "create.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc' and test_description.filesize:4096",
                     "refId": "A",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: create: filesize 4096",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "create.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata' and test_description.filesize:4096",
                     "refId": "B",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "pod: read :  filesize 4096",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "read.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc' and test_description.filesize:4096",
                     "refId": "C",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: read:  filesize 4096",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "read.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata' and test_description.filesize:4096",
                     "refId": "D",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "pod: remove :  filesize 4096",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "remove.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc' and test_description.filesize:4096",
                     "refId": "E",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: remove:  filesize 4096",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "remove.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata' and test_description.filesize:4096",
                     "refId": "F",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "pod: create: filesize 262,144",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "create.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc' and test_description.filesize:262144",
                     "refId": "G",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: create:  filesize 262,144",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "create.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata' and test_description.filesize:262144",
                     "refId": "H",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "pod: read :  filesize 262,144",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "read.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc' and test_description.filesize:262144",
                     "refId": "I",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: read :  filesize 262,144",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "read.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata' and test_description.filesize:262144",
                     "refId": "J",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "pod: remove :  filesize 262,144",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "remove.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc' and test_description.filesize:262144",
                     "refId": "K",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata: remove:  filesize 262,144",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "remove.elapsed_time",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata' and test_description.filesize:262144",
                     "refId": "K",
                     "timeField": "timestamp"
                  }
               ],
               "title": "clusterbuster-files: elapsed_time: Direct/ 64 dirs/files",
               "type": "state-timeline"
            },
            {
               "datasource": "Elasticsearch-clusterbuster-fio-release-results",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 70,
                        "lineWidth": 0
                     },
                     "mappings": [ ],
                     "min": 0,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "red"
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 50
                           },
                           {
                              "color": "super-light-green",
                              "value": 80
                           },
                           {
                              "color": "dark-green",
                              "value": 90
                           },
                           {
                              "color": "dark-blue",
                              "value": 100
                           }
                        ]
                     }
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 36,
                  "w": 24,
                  "x": 0,
                  "y": 333
               },
               "id": 59,
               "interval": "1d",
               "links": [
                  {
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150"
                  }
               ],
               "options": {
                  "alignValue": "left",
                  "legend": {
                     "displayMode": "list",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "auto",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "targets": [
                  {
                     "alias": "runc read",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "metrics": [
                        {
                           "field": "read.iops",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc'",
                     "refId": "A",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata read",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "read.iops",
                           "id": "6",
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata'",
                     "refId": "B",
                     "timeField": "timestamp"
                  }
               ],
               "title": "clusterbuster-fio",
               "type": "state-timeline"
            },
            {
               "datasource": "Elasticsearch-clusterbuster-uperf-release-results",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 70,
                        "lineWidth": 0
                     },
                     "mappings": [ ],
                     "min": 0,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "red"
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 50
                           },
                           {
                              "color": "super-light-green",
                              "value": 80
                           },
                           {
                              "color": "dark-green",
                              "value": 90
                           },
                           {
                              "color": "dark-blue",
                              "value": 100
                           }
                        ]
                     }
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 36,
                  "w": 24,
                  "x": 0,
                  "y": 369
               },
               "id": 60,
               "interval": "1d",
               "links": [
                  {
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150"
                  }
               ],
               "options": {
                  "alignValue": "left",
                  "legend": {
                     "displayMode": "list",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "auto",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "targets": [
                  {
                     "alias": "runc rate",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "metrics": [
                        {
                           "field": "rate",
                           "id": "6",
                           "settings": {
                              "script": "_value/1000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='runc'",
                     "refId": "A",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "kata rate",
                     "bucketAggs": [
                        {
                           "field": "timestamp",
                           "id": "7",
                           "settings": {
                              "interval": "auto",
                              "min_doc_count": "0",
                              "timeZone": "utc",
                              "trimEdges": "0"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "rate",
                           "id": "6",
                           "settings": {
                              "script": "_value/1000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "test_description.runtime='kata'",
                     "refId": "B",
                     "timeField": "timestamp"
                  }
               ],
               "title": "clusterbuster-uperf",
               "type": "state-timeline"
            }
         ],
         "title": "Clusterbuster - release",
         "type": "row"
      },
      {
         "collapsed": true,
         "gridPos": {
            "h": 1,
            "w": 24,
            "x": 0,
            "y": 20
         },
         "id": 8,
         "panels": [
            {
               "datasource": "Elasticsearch-bootstorm-results",
               "description": "Time till VM Login - Lower is better",
               "fieldConfig": {
                  "defaults": {
                     "color": {
                        "mode": "thresholds"
                     },
                     "custom": {
                        "fillOpacity": 77,
                        "lineWidth": 0
                     },
                     "decimals": 1,
                     "mappings": [
                        {
                           "options": {
                              "result": {
                                 "color": "transparent",
                                 "index": 0,
                                 "text": "."
                              }
                           },
                           "type": "value"
                        }
                     ],
                     "max": -1,
                     "thresholds": {
                        "mode": "percentage",
                        "steps": [
                           {
                              "color": "dark-blue"
                           },
                           {
                              "color": "dark-green",
                              "value": 1
                           },
                           {
                              "color": "super-light-green",
                              "value": 10
                           },
                           {
                              "color": "semi-dark-orange",
                              "value": 20
                           },
                           {
                              "color": "dark-red",
                              "value": 50
                           }
                        ]
                     },
                     "unit": "none"
                  },
                  "overrides": [ ]
               },
               "gridPos": {
                  "h": 19,
                  "w": 24,
                  "x": 0,
                  "y": 187
               },
               "id": 65,
               "interval": "1d",
               "links": [
                  {
                     "targetBlank": true,
                     "title": "artifacts link",
                     "url": "https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=190"
                  }
               ],
               "options": {
                  "alignValue": "center",
                  "legend": {
                     "displayMode": "hidden",
                     "placement": "bottom"
                  },
                  "mergeValues": false,
                  "rowHeight": 0.90000000000000002,
                  "showValue": "always",
                  "tooltip": {
                     "mode": "single"
                  }
               },
               "targets": [
                  {
                     "alias": "Min",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "bootstorm_time",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000"
                           },
                           "type": "min"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "A",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Max",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "bootstorm_time",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "B",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "bootstorm_time",
                           "id": "1",
                           "settings": {
                              "percents": [
                                 "25",
                                 "50",
                                 "75",
                                 "95",
                                 "99"
                              ],
                              "script": "_value/1000"
                           },
                           "type": "percentiles"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "C",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "AVG. 100 vms {{term node.keyword}}",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "node.keyword",
                           "id": "4",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "asc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "bootstorm_time",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000"
                           },
                           "type": "avg"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "D",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Memory(GB) [384GB]",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "total_Memory",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "F",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Memory Worker-0 (GB) [128GB]",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "worker-0_Memory",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "E",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Memory Worker-1 (GB) [128GB]",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "worker-1_Memory",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "G",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "Memory Worker-2 (GB) [128GB]",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "worker-2_Memory",
                           "id": "1",
                           "settings": {
                              "script": "_value/1000000000"
                           },
                           "type": "max"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "H",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "%CPU [240 cores]",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "total_CPU",
                           "id": "1",
                           "settings": { },
                           "type": "max"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "I",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "%CPU worker-0 [80 cores]",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "worker-0_CPU",
                           "id": "1",
                           "settings": { },
                           "type": "max"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "J",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "%CPU worker-1 [80 cores]",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "worker-1_CPU",
                           "id": "1",
                           "settings": { },
                           "type": "max"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "K",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "%CPU worker-2 [80 cores]",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "field": "worker-2_CPU",
                           "id": "1",
                           "settings": { },
                           "type": "max"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "L",
                     "timeField": "timestamp"
                  },
                  {
                     "alias": "VMs #",
                     "bucketAggs": [
                        {
                           "field": "scale",
                           "id": "3",
                           "settings": {
                              "min_doc_count": "1",
                              "order": "desc",
                              "orderBy": "_term",
                              "size": "10"
                           },
                           "type": "terms"
                        },
                        {
                           "field": "timestamp",
                           "id": "2",
                           "settings": {
                              "interval": "auto"
                           },
                           "type": "date_histogram"
                        }
                     ],
                     "hide": false,
                     "metrics": [
                        {
                           "id": "1",
                           "type": "count"
                        }
                     ],
                     "query": "scale:300 AND ocp_version:$ocp_version",
                     "refId": "M",
                     "timeField": "timestamp"
                  }
               ],
               "title": "300 Fedora37 VMs(Sec)",
               "type": "state-timeline"
            }
         ],
         "title": "BootStorm",
         "type": "row"
      }
   ],
   "refresh": "",
   "schemaVersion": 34,
   "style": "dark",
   "tags": [ ],
   "templating": {
      "list": [
         {
            "allValue": "",
            "datasource": "Elasticsearch-hammerdb-results",
            "hide": 0,
            "includeAll": true,
            "multi": true,
            "name": "ocp_version",
            "query": "{\"find\":\"terms\",\"field\":\"ocp_version.keyword\"}",
            "refresh": 2,
            "regex": "",
            "sort": 6,
            "type": "query"
         },
         {
            "allValue": "",
            "datasource": "Elasticsearch-hammerdb-results",
            "hide": 0,
            "includeAll": true,
            "multi": true,
            "name": "db_type",
            "query": "{\"find\":\"terms\",\"field\":\"db_type.keyword\"}",
            "refresh": 2,
            "regex": "",
            "sort": 1,
            "type": "query"
         },
         {
            "allValue": "",
            "datasource": "Elasticsearch-hammerdb-results",
            "hide": 0,
            "includeAll": true,
            "multi": true,
            "name": "current_worker",
            "query": "{\"find\":\"terms\",\"field\":\"current_worker\"}",
            "refresh": 2,
            "regex": "",
            "sort": 1,
            "type": "query"
         },
         {
            "allValue": "",
            "datasource": "Elasticsearch-hammerdb-results",
            "hide": 0,
            "includeAll": true,
            "multi": true,
            "name": "kind",
            "query": "{\"find\":\"terms\",\"field\":\"kind.keyword\"}",
            "refresh": 2,
            "regex": "",
            "sort": 1,
            "type": "query"
         },
         {
            "allValue": "",
            "datasource": "Elasticsearch-vdbench-results",
            "hide": 0,
            "includeAll": true,
            "multi": true,
            "name": "vdbench_type",
            "query": "{\"find\":\"terms\",\"field\":\"Run.keyword\"}",
            "refresh": 2,
            "regex": "",
            "sort": 6,
            "type": "query"
         }
      ]
   },
   "time": {
      "from": "now-6h",
      "to": "now"
   },
   "timepicker": { },
   "timezone": "",
   "title": "PerfCI-Regression-Summary",
   "uid": "T4775LKnzzmichey",
   "version": 409,
   "weekStart": ""
}
