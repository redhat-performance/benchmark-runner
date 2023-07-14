local g = import 'g.libsonnet';
local grafonnet = import 'github.com/grafana/grafonnet/gen/grafonnet-latest/main.libsonnet';
local elasticsearch = grafonnet.query.elasticsearch;
local stateTimeline = grafonnet.panel.stateTimeline;
local var = g.dashboard.variable;


g.dashboard.new('PerfCI-Regression-Summary')
+ g.dashboard.time.withFrom('now-45d')
+ g.dashboard.time.withTo('now')
+ g.dashboard.withTimepicker({},)
+ g.dashboard.withTimezone("")
+ g.dashboard.withUid('T4775LKnzzmichey')
+ g.dashboard.withVersion(409)
+ g.dashboard.withWeekStart("")
+ g.dashboard.withLiveNow(false)


+ g.dashboard.withLinks([
  g.dashboard.link.link.new('Details', 'https://docs.google.com/spreadsheets/d/1eSOmyZKJ6f0RIHN0zJNnH-S2YrqrU0oyzp7PNSQvksE/edit#gid=0')
  + g.dashboard.link.link.options.withAsDropdown(false)
  + g.dashboard.link.link.withIcon('info')
  + g.dashboard.link.link.options.withIncludeVars(false)
  + g.dashboard.link.link.options.withKeepTime(false)
  + g.dashboard.link.link.options.withTargetBlank(true),

  g.dashboard.link.link.new('Issues', 'https://docs.google.com/spreadsheets/d/1vZtg0Gj8IxKPGLWAkB4iD1O59u_WA4ky5P7gGX6xW3M/edit#gid=0')
  + g.dashboard.link.link.options.withAsDropdown(false)
  + g.dashboard.link.link.withIcon('bolt')
  + g.dashboard.link.link.options.withIncludeVars(false)
  + g.dashboard.link.link.options.withKeepTime(false)
  + g.dashboard.link.link.options.withTargetBlank(true),


])


//////////////////////////////////////////////////////
+ g.dashboard.templating.withList([
  /*
  
  g.dashboard.variable.datasource.new('Elasticsearch-hammerdb-results', 'elasticsearch')
  + g.dashboard.variable.datasource.withRegex('/^Elasticsearch-hammerdb-results/'),

  g.dashboard.variable.datasource.new('Elasticsearch-ci-status', 'elasticsearch')
  + g.dashboard.variable.datasource.withRegex('/^Elasticsearch-ci-status/'),

  g.dashboard.variable.datasource.new('Elasticsearch-uperf-results', 'elasticsearch')
  + g.dashboard.variable.datasource.withRegex('/^Elasticsearch-uperf-results/'),

  g.dashboard.variable.datasource.new('Elasticsearch-vdbench-results', 'elasticsearch')
  + g.dashboard.variable.datasource.withRegex('/^Elasticsearch-vdbench-results/'),
  
*/


  g.dashboard.variable.query.new('ocp_version', '{\"find\":\"terms\",\"field\":\"ocp_version.keyword\"}')
  + elasticsearch.withDatasource('Elasticsearch-hammerdb-results')
  + g.query.azureMonitor.withHide(0)
  + g.dashboard.variable.query.selectionOptions.withIncludeAll(true, '')
  + g.dashboard.variable.query.selectionOptions.withMulti(true)
  + g.dashboard.variable.query.withRegex('')
  + g.dashboard.variable.query.withSort(6)
  + g.dashboard.variable.query.withRefresh(2),

  g.dashboard.variable.query.new('db_type', '{\"find\":\"terms\",\"field\":\"db_type.keyword\"}')
  + elasticsearch.withDatasource('Elasticsearch-hammerdb-results')
  + g.query.azureMonitor.withHide(0)
  + g.dashboard.variable.query.selectionOptions.withIncludeAll(true, '')
  + g.dashboard.variable.query.selectionOptions.withMulti(true)
  + g.dashboard.variable.query.withRegex('')
  + g.dashboard.variable.query.withSort(1)
  + g.dashboard.variable.query.withRefresh(2),

  g.dashboard.variable.query.new('current_worker', '{\"find\":\"terms\",\"field\":\"current_worker\"}')
  + elasticsearch.withDatasource('Elasticsearch-hammerdb-results')
  + g.query.azureMonitor.withHide(0)
  + g.dashboard.variable.query.selectionOptions.withIncludeAll(true, '')
  + g.dashboard.variable.query.selectionOptions.withMulti(true)
  + g.dashboard.variable.query.withRegex('')
  + g.dashboard.variable.query.withSort(1)
  + g.dashboard.variable.query.withRefresh(2),

  g.dashboard.variable.query.new('kind', '{\"find\":\"terms\",\"field\":\"kind.keyword\"}')
  + elasticsearch.withDatasource('Elasticsearch-hammerdb-results')
  + g.query.azureMonitor.withHide(0)
  + g.dashboard.variable.query.selectionOptions.withIncludeAll(true, '')
  + g.dashboard.variable.query.selectionOptions.withMulti(true)
  + g.dashboard.variable.query.withRegex('')
  + g.dashboard.variable.query.withSort(1)
  + g.dashboard.variable.query.withRefresh(2),

  g.dashboard.variable.query.new('vdbench_type', '{\"find\":\"terms\",\"field\":\"Run.keyword\"}')
  + elasticsearch.withDatasource('Elasticsearch-vdbench-results')
  + g.query.azureMonitor.withHide(0)
  + g.dashboard.variable.query.selectionOptions.withIncludeAll(true, '')
  + g.dashboard.variable.query.selectionOptions.withMulti(true)
  + g.dashboard.variable.query.withRegex('')
  + g.dashboard.variable.query.withSort(6)
  + g.dashboard.variable.query.withRefresh(2),


  
  
  

  
])

///////////////////////////////////////////////////////

+ g.dashboard.withRefresh('')
+ g.dashboard.withSchemaVersion(34)
+ g.dashboard.withStyle('dark')
+ g.dashboard.withTags([],)


+ g.dashboard.withPanels([
/////////////////////////////////////////


///////////////////////////////////////////
  g.panel.text.new('Workloads Legend')

    + g.panel.text.gridPos.withH(6)
    + g.panel.text.gridPos.withW(5)
    + g.panel.text.gridPos.withX(0)
    + g.panel.text.gridPos.withY(0)

    + g.panel.text.withId('188')

    + g.panel.text.options.withContent('\n<p style=\"background-color:#000099;text-align: center;\" > > 100% new peak</p>\n<p style=\"background-color:#006600;text-align: center;color:black;\" > 90% - 100% of peak</p>\n<p style=\"background-color:#9fdf9f;text-align: center;color:black;\" > 80% -  90% of peak</p>\n<p style=\"background-color:#cc6600;text-align: center;color:black;\" > 50% -  80% of peak</p>\n<p style=\"background-color:#992600;text-align: center;\" > 0%  -  50% of peak</p>\n\n\n           ')
      + g.panel.text.options.withMode("html")

    + g.panel.text.withPluginVersion('8.4.0-pre')

    + g.panel.text.withTargets([

      elasticsearch.withAlias('')

      + elasticsearch.withBucketAggs([
        elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
        + elasticsearch.bucketAggs.DateHistogram.withId('2')
        + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
        + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      ])
       
      + g.panel.text.datasource.withType('elasticsearch')
      + g.panel.text.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')

      + elasticsearch.withMetrics([
         elasticsearch.metrics.Count.withId('1')
         + elasticsearch.metrics.Count.withType('count')
         
      ])

      + elasticsearch.withQuery('')
      + elasticsearch.withRefId('A')
      + elasticsearch.withTimeField('timestamp')


    ]),

    ////////////////////////////////////////////
    g.panel.text.new('')
      + g.panel.text.panelOptions.withDescription("")

      + g.panel.text.gridPos.withH(6)
      + g.panel.text.gridPos.withW(5)
      + g.panel.text.gridPos.withX(19)
      + g.panel.text.gridPos.withY(0)

      + g.panel.text.withId('187')

      + g.panel.text.options.withContent('![Cloud Governance](https://www.cielhr.com/wp-content/uploads/2019/10/PerformancewSpace-1080x675.png \"Tooltip Text\")\n')
      + g.panel.text.options.withMode("markdown")

      + g.panel.text.withPluginVersion('8.4.0-pre')


      + g.panel.text.withTargets([

      elasticsearch.withAlias('')

      + elasticsearch.withBucketAggs([
        elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
        + elasticsearch.bucketAggs.DateHistogram.withId('2')
        + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
        + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      ])
       
      + g.panel.text.datasource.withType('elasticsearch')
      + g.panel.text.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')

      + elasticsearch.withMetrics([
         elasticsearch.metrics.Count.withId('1')
         + elasticsearch.metrics.Count.withType('count')
         
      ])

      + elasticsearch.withQuery('')
      + elasticsearch.withRefId('A')
      + elasticsearch.withTimeField('timestamp')


    ]),







    ////////////////////////////////////////
    stateTimeline.new('Product Versions')
      

      + stateTimeline.withDescription("OVN - 09/19")
      
      + stateTimeline.queryOptions.withDatasource('Elasticsearch-ci-status')
      + stateTimeline.standardOptions.color.withFixedColor('#132dc3')
      + stateTimeline.standardOptions.color.withMode('fixed')
      + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(85)
      + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

      + stateTimeline.fieldConfig.defaults.withMappings([
        stateTimeline.valueMapping.RegexMap.withOptions(
              {
                "102": {
                  "index": 13,
                  "text": "1.0.2"
                },
                "110": {
                  "index": 14,
                  "text": "1.1.0"
                },
                "120": {
                  "index": 15,
                  "text": "1.2.0"
                },
                "121": {
                  "index": 16,
                  "text": "1.2.1"
                },
                "130": {
                  "index": 45,
                  "text": "1.3.0"
                },
                "131": {
                  "index": 117,
                  "text": "1.3.1"
                },
                "132": {
                  "index": 76,
                  "text": "1.3.2"
                },
                "133": {
                  "index": 77,
                  "text": "1.3.3"
                },
                "140": {
                  "index": 118,
                  "text": "1.4.0"
                },
                "483": {
                  "index": 0,
                  "text": "4.8.3"
                },
                "484": {
                  "index": 1,
                  "text": "4.8.4"
                },
                "485": {
                  "index": 2,
                  "text": "4.8.5"
                },
                "486": {
                  "index": 3,
                  "text": "4.8.6"
                },
                "487": {
                  "index": 4,
                  "text": "4.8.7"
                },
                "488": {
                  "index": 5,
                  "text": "4.8.8"
                },
                "3025": {
                  "index": 86,
                  "text": "3.0.2-5"
                },
                "3026": {
                  "index": 119,
                  "text": "3.0.2-6"
                },
                "4102": {
                  "index": 33,
                  "text": "4.10.2"
                },
                "4104": {
                  "index": 34,
                  "text": "4.10.4"
                },
                "4105": {
                  "index": 35,
                  "text": "4.10.5"
                },
                "4106": {
                  "index": 36,
                  "text": "4.10.6"
                },
                "4108": {
                  "index": 37,
                  "text": "4.10.8"
                },
                "4109": {
                  "index": 38,
                  "text": "4.10.9"
                },
                "4114": {
                  "index": 54,
                  "text": "4.11.4"
                },
                "4115": {
                  "index": 55,
                  "text": "4.11.5"
                },
                "4116": {
                  "index": 56,
                  "text": "4.11.6"
                },
                "4117": {
                  "index": 57,
                  "text": "4.11.7"
                },
                "4118": {
                  "index": 58,
                  "text": "4.11.8"
                },
                "4119": {
                  "index": 59,
                  "text": "4.11.9"
                },
                "4120": {
                  "index": 68,
                  "text": "4.12.0"
                },
                "4121": {
                  "index": 69,
                  "text": "4.12.1"
                },
                "4122": {
                  "index": 70,
                  "text": "4.12.2"
                },
                "4124": {
                  "index": 80,
                  "text": "4.12.4"
                },
                "4130": {
                  "index": 106,
                  "text": "4.13.0"
                },
                "4131": {
                  "index": 109,
                  "text": "4.13.1"
                },
                "4132": {
                  "index": 110,
                  "text": "4.13.2"
                },
                "4133": {
                  "index": 111,
                  "text": "4.13.3"
                },
                "4814": {
                  "index": 6,
                  "text": "4.8.14"
                },
                "4932": {
                  "index": 8,
                  "text": "4.9.3-2"
                },
                "4947": {
                  "index": 9,
                  "text": "4.9.4-7"
                },
                "4955": {
                  "index": 10,
                  "text": "4.9.5-5"
                },
                "4961": {
                  "index": 11,
                  "text": "4.9.6-1"
                },
                "4972": {
                  "index": 12,
                  "text": "4.9.7-2"
                },
                "41002": {
                  "index": 30,
                  "text": "4.10.0-rc.2"
                },
                "41003": {
                  "index": 31,
                  "text": "4.10.0-rc.3"
                },
                "41007": {
                  "index": 32,
                  "text": "4.10.0-rc.7"
                },
                "41010": {
                  "index": 39,
                  "text": "4.10.10"
                },
                "41011": {
                  "index": 40,
                  "text": "4.10.11"
                },
                "41012": {
                  "index": 41,
                  "text": "4.10.12"
                },
                "41013": {
                  "index": 42,
                  "text": "4.10.13"
                },
                "41014": {
                  "index": 43,
                  "text": "4.10.14"
                },
                "41015": {
                  "index": 44,
                  "text": "4.10.15"
                },
                "41016": {
                  "index": 21,
                  "text": "4.10.1-6"
                },
                "41021": {
                  "index": 28,
                  "text": "4.10.2-1"
                },
                "41023": {
                  "index": 29,
                  "text": "4.10.2-3"
                },
                "41054": {
                  "index": 49,
                  "text": "4.10.5-4"
                },
                "41066": {
                  "index": 48,
                  "text": "4.10.6-6"
                },
                "41110": {
                  "index": 60,
                  "text": "4.11.10"
                },
                "41111": {
                  "index": 61,
                  "text": "4.11.11"
                },
                "41112": {
                  "index": 62,
                  "text": "4.11.12"
                },
                "41113": {
                  "index": 63,
                  "text": "4.11.13"
                },
                "41114": {
                  "index": 64,
                  "text": "4.11.14"
                },
                "41144": {
                  "index": 78,
                  "text": "4.11.4-4"
                },
                "41159": {
                  "index": 79,
                  "text": "4.11.5-9"
                },
                "41206": {
                  "index": 65,
                  "text": "4.12.0.6"
                },
                "41207": {
                  "index": 66,
                  "text": "4.12.0.7"
                },
                "41208": {
                  "index": 67,
                  "text": "4.12.0.8"
                },
                "41218": {
                  "index": 73,
                  "text": "4.12.1-8"
                },
                "41224": {
                  "index": 85,
                  "text": "4.12.2-4"
                },
                "41304": {
                  "index": 102,
                  "text": "4.13.0-rc.4"
                },
                "41305": {
                  "index": 103,
                  "text": "4.13.0-rc.5"
                },
                "41307": {
                  "index": 104,
                  "text": "4.13.0-rc.7"
                },
                "41308": {
                  "index": 105,
                  "text": "4.13.0-rc.8"
                },
                "49211": {
                  "index": 7,
                  "text": "4.9.2-11"
                },
                "410129": {
                  "index": 22,
                  "text": "4.10.1-29"
                },
                "410136": {
                  "index": 23,
                  "text": "4.10.1-36"
                },
                "410160": {
                  "index": 24,
                  "text": "4.10.1-60"
                },
                "410170": {
                  "index": 25,
                  "text": "4.10.1-70"
                },
                "410197": {
                  "index": 26,
                  "text": "4.10.1-97"
                },
                "411115": {
                  "index": 52,
                  "text": "4.11.1-15"
                },
                "411121": {
                  "index": 51,
                  "text": "4.11.1-21"
                },
                "411135": {
                  "index": 46,
                  "text": "4.11.1-35"
                },
                "411142": {
                  "index": 47,
                  "text": "4.11.1-42"
                },
                "411605": {
                  "index": 53,
                  "text": "4.11.6-5"
                },
                "412116": {
                  "index": 74,
                  "text": "4.12.1-16"
                },
                "412119": {
                  "index": 84,
                  "text": "4.12.1-19"
                },
                "412122": {
                  "index": 75,
                  "text": "4.12.1-22"
                },
                "412139": {
                  "index": 82,
                  "text": "4.12.1-39"
                },
                "412140": {
                  "index": 81,
                  "text": "4.12.1-40"
                },
                "412317": {
                  "index": 121,
                  "text": "4.12.3-17"
                },
                "413014": {
                  "index": 101,
                  "text": "4.13.0-ec.4"
                },
                "413118": {
                  "index": 113,
                  "text": "4.13.1-18"
                },
                "413140": {
                  "index": 114,
                  "text": "4.13.1-40"
                },
                "4100683": {
                  "index": 17,
                  "text": "4.10.0-683"
                },
                "4100688": {
                  "index": 18,
                  "text": "4.10.0-688"
                },
                "4100700": {
                  "index": 19,
                  "text": "4.10.0-700"
                },
                "4100729": {
                  "index": 20,
                  "text": "4.10.0-729"
                },
                "4101101": {
                  "index": 27,
                  "text": "4.10.1-101"
                },
                "4110137": {
                  "index": 50,
                  "text": "4.11.0-137"
                },
                "4120173": {
                  "index": 83,
                  "text": "4.12.0-173"
                },
                "4120777": {
                  "index": 71,
                  "text": "4.12.0-777"
                },
                "4120781": {
                  "index": 72,
                  "text": "4.12.0-781"
                },
                "4131154": {
                  "index": 115,
                  "text": "4.13.1-154"
                },
                "41301586": {
                  "index": 88,
                  "text": "4.13.0-1586"
                },
                "41301649": {
                  "index": 89,
                  "text": "4.13.0-1649"
                },
                "41301666": {
                  "index": 91,
                  "text": "4.13.0-1666"
                },
                "41301689": {
                  "index": 90,
                  "text": "4.13.0-1689"
                },
                "41301782": {
                  "index": 92,
                  "text": "4.13.0-1782"
                },
                "41301856": {
                  "index": 93,
                  "text": "4.13.0-1856"
                },
                "41301938": {
                  "index": 94,
                  "text": "4.13.0-1938"
                },
                "41301943": {
                  "index": 95,
                  "text": "4.13.0-1943"
                },
                "41302115": {
                  "index": 96,
                  "text": "4.13.0-2115"
                },
                "41302176": {
                  "index": 97,
                  "text": "4.13.0-2176"
                },
                "41302229": {
                  "index": 98,
                  "text": "4.13.0-2229"
                },
                "41302251": {
                  "index": 99,
                  "text": "4.13.0-2251"
                },
                "41302269": {
                  "index": 100,
                  "text": "4.13.0-2269"
                },
                "4130ec3": {
                  "index": 87,
                  "text": "4.13.0-ec.3"
                },
                "CNV": {
                  "index": 112,
                  "text": "CNV"
                },
                "KATA": {
                  "index": 116,
                  "text": "KATA"
                },
                "OCP": {
                  "index": 108,
                  "text": "OCP"
                },
                "ODF": {
                  "index": 120,
                  "text": "ODF"
                },
                "Product Versions": {
                  "index": 107,
                  "text": "Product Versions"
                }
              }
        )
        + stateTimeline.valueMapping.RegexMap.withType('value')
        

      ])

      + stateTimeline.fieldConfig.defaults.thresholds.withMode('absolute')
      + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
        g.panel.alertGroups.thresholdStep.withColor('green')
        + g.panel.alertGroups.thresholdStep.withValue(null)

      ])

      + stateTimeline.fieldConfig.withOverrides([])

      + stateTimeline.gridPos.withH(6)
      + stateTimeline.gridPos.withW(24)
      + stateTimeline.gridPos.withX(0)
      + stateTimeline.gridPos.withY(6)

      + stateTimeline.withId(171)
      + stateTimeline.queryOptions.withInterval("1d")

      + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('OCP version')
              + stateTimeline.link.withUrl('https://openshift-release.apps.ci.l2s4.p1.openshiftapps.com/')

      ])

      + stateTimeline.options.withAlignValue("right")
      + stateTimeline.options.legend.withDisplayMode("hidden")
      + stateTimeline.options.legend.withPlacement("bottom")
      + stateTimeline.options.withMergeValues(true)
      + stateTimeline.options.withRowHeight(0.85)
      + stateTimeline.options.withShowValue("always")
      + stateTimeline.options.tooltip.withMode("single")

      + stateTimeline.withPluginVersion('8.4.0-pre')

      + g.panel.stateTimeline.withTargets([

        elasticsearch.withAlias('Openshift')
          + elasticsearch.withBucketAggs([
            elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
            + elasticsearch.bucketAggs.DateHistogram.withId('2')
            + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
            + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
          ])
       

          + elasticsearch.withHide(false)

          + elasticsearch.withMetrics([
            elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('ci_minutes_time')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('Integer.parseInt(\"0\"+doc["ocp_version.keyword"].value.replace(\".\",\"\").replace(\"r\",\"\").replace(\"c\",\"\").replace(\"f\",\"\").replace(\"-\",\"\").replace(\"e\",\"1\").replace(\"c\",\"\").replace(\"r\",\"\"))')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
          ])

          + elasticsearch.withQuery('_exists_:ocp_version AND ocp_version:$ocp_version')
          + elasticsearch.withRefId('A')
          + elasticsearch.withTimeField('timestamp'),

        ////

        elasticsearch.withAlias('CNV Nightly op.')
          + elasticsearch.withBucketAggs([
            elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
            + elasticsearch.bucketAggs.DateHistogram.withId('2')
            + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
            + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
          ])

          + elasticsearch.withHide(false)

          + elasticsearch.withMetrics([
            elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('ci_minutes_time')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('(doc["cnv_version.keyword"].value.indexOf(\" \") == -1) ? Integer.parseInt(\"0\"+doc["cnv_version.keyword"].value.replace(\".\",\"\").replace(\"r\",\"\").replace(\"c\",\"\").replace(\"f\",\"\").replace(\"-\",\"\")) : 0')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
          ])

          + elasticsearch.withQuery('_exists_:cnv_version AND ocp_version:$ocp_version')
          + elasticsearch.withRefId('C')
          + elasticsearch.withTimeField('timestamp'),

        ////
        elasticsearch.withAlias('KATA op.')
          + elasticsearch.withBucketAggs([
            elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
            + elasticsearch.bucketAggs.DateHistogram.withId('2')
            + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
            + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
          ])

          + elasticsearch.withHide(false)

          + elasticsearch.withMetrics([
            elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('ci_minutes_time')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('(doc["kata_version.keyword"].value.indexOf(\" \") == -1) ? Integer.parseInt(doc["kata_version.keyword"].value.replace(\".\",\"\")) : 0')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
          ])

          + elasticsearch.withQuery('_exists_:kata_version AND ocp_version:$ocp_version')
          + elasticsearch.withRefId('D')
          + elasticsearch.withTimeField('timestamp'),

        ////
        elasticsearch.withAlias('Kata rpm')
          + elasticsearch.withBucketAggs([
            elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
            + elasticsearch.bucketAggs.DateHistogram.withId('2')
            + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
            + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
          ])
       

          + elasticsearch.withHide(false)

          + elasticsearch.withMetrics([
            elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('ci_minutes_time')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('Integer.parseInt(\"0\"+doc["kata_rpm_version.keyword"].value.replace(\".\",\"\").replace(\"r\",\"\").replace(\"c\",\"\").replace(\"f\",\"\").replace(\"-\",\"\").replace(\"e\",\"1\").replace(\"c\",\"\").replace(\"r\",\"\"))')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
          ])

          + elasticsearch.withQuery('_exists_:kata_rpm_version AND ocp_version:$ocp_version')
          + elasticsearch.withRefId('F')
          + elasticsearch.withTimeField('timestamp'),

        ////
        elasticsearch.withAlias('ODF op.')
          + elasticsearch.withBucketAggs([
            elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
            + elasticsearch.bucketAggs.DateHistogram.withId('2')
            + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
            + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
          ])
       

          + elasticsearch.withHide(false)

          + elasticsearch.withMetrics([
            elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('ci_minutes_time')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('((doc["odf_version.keyword"].size() != 0) ? ((doc["odf_version.keyword"].value.indexOf(\" \") == -1) ? Integer.parseInt(\"0\"+doc["odf_version.keyword"].value.replace(\".\",\"\").replace(\"r\",\"\").replace(\"c\",\"\").replace(\"f\",\"\").replace(\"-\",\"\")) : 0) : 0)')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
          ])

          + elasticsearch.withQuery('_exists_:odf_version AND ocp_version:$ocp_version')
          + elasticsearch.withRefId('E')
          + elasticsearch.withTimeField('timestamp'),

        ////
        elasticsearch.withAlias('ODF # disks')
          + elasticsearch.withBucketAggs([
            elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
            + elasticsearch.bucketAggs.DateHistogram.withId('2')
            + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
            + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
          ])

          + elasticsearch.withHide(false)

          + elasticsearch.withMetrics([
            elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('odf_disk_count')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
          ])

          + elasticsearch.withQuery('ocp_version:$ocp_version')
          + elasticsearch.withRefId('B')
          + elasticsearch.withTimeField('timestamp')


      ]),

//////////////////////////////////////////
      g.panel.row.new("Hammerdb")
        + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(12)

        + g.panel.row.withId(136)
        + g.panel.row.withPanels([

          g.panel.stateTimeline.new('HammerDB KTPM')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-hammerdb-results')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(38)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(13)

            + stateTimeline.withId(120)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&viewPanel=128')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + stateTimeline.withPluginVersion('8.4.0-pre')


            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('{{term db_type.keyword}}  : {{term current_worker}} threads : {{term kind.keyword}}:  {{term storage_type.keyword}}')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('db_type.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('current_worker')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('storage_type.keyword')
                + elasticsearch.bucketAggs.Terms.withId('5')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      


      
              ])
    
              
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('tpm')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')


              ])
              + elasticsearch.withQuery('_exists_:tpm AND db_type:$db_type AND current_worker:$current_worker AND kind:$kind AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')
            ])





        ]),
      

        




        //////////////////////////////////////////




        


      g.panel.row.new("Uperf")
        
        + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(13)

        + g.panel.row.withId(138)
        + g.panel.row.withPanels([

          g.panel.stateTimeline.new('Uperf Latency (usecs)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-uperf-results')
            
            + g.panel.stateTimeline.withDescription('Lower is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withDecimals(1)
            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMax(-1)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-blue'),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(1),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(10),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(20),

              stateTimeline.thresholdStep.withColor('dark-red')
              + stateTimeline.thresholdStep.withValue(50)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(15)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(52)

            + stateTimeline.withId(116)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&viewPanel=129')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('msg size: {{term read_message_size}} :{{term num_threads}}th: {{term kind.keyword}}')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('read_message_size')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('num_threads')
                + elasticsearch.bucketAggs.Terms.withId('5')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      


      
              ])
    
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('norm_ltcy')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])

              +elasticsearch.withQuery('_exists_:norm_ltcy AND read_message_size:(64 OR 1024 OR 8192) AND num_threads:(1) AND test_type:rr AND norm_ltcy:<1000 AND kind:$kind  AND ocp_version:$ocp_version')
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('msg size: {{term read_message_size}} :{{term num_threads}}th: {{term kind.keyword}}')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('read_message_size')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('num_threads')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('5')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('norm_ltcy')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value*8')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])

              +elasticsearch.withQuery('_exists_:norm_ltcy AND read_message_size:(64 OR 1024 OR 8192) AND num_threads:(8) AND test_type:rr AND norm_ltcy:<1000 AND kind:$kind  AND ocp_version:$ocp_version')
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp')



            ]),

            g.panel.stateTimeline.new('Uperf Throughput (Gbits/s)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-uperf-results')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withDecimals(1)
            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('semi-dark-red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(15)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(67)

            + stateTimeline.withId(115)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&viewPanel=129')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('msg size: {{term read_message_size}} :{{term num_threads}}th: {{term kind.keyword}}')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('read_message_size')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('num_threads')
                + elasticsearch.bucketAggs.Terms.withId('5')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      


      
              ])
    
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('norm_byte')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value*8/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])

              +elasticsearch.withQuery('_exists_:norm_ops AND read_message_size:(64 OR 1024 OR 8192) AND num_threads:(1 OR 8) AND test_type:stream AND kind:$kind  AND ocp_version:$ocp_version')
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp')

            ])


        ]),


        




        //////////////////////////////////////////






      g.panel.row.new("Vdbench")
        + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(14)

        + g.panel.row.withId(142)
        + g.panel.row.withPanels([

          g.panel.stateTimeline.new('vdbench (IOPS)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-vdbench-results')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(48)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(83)

            + stateTimeline.withId(132)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=133'),

              stateTimeline.link.withTitle('scale  log link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=195')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('{{term Run.keyword}} : {{term Threads}}th : 1 {{term kind.keyword}}')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('Run.keyword')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('Threads')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      


      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('Rate')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')

              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('Total {{term kind.keyword}} Memory (GB) [384GB]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')


              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('Total {{term kind.keyword}} %CPU [240 cores]')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])


              + elasticsearch.withHide(false)
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('C')
              +elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('{{term Run.keyword}} : {{term Threads}}th :{{term scale}} {{term kind.keyword}}s')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('Run.keyword')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('Threads')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
 
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('Rate')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('D')
              +elasticsearch.withTimeField('timestamp'),


              ////

              elasticsearch.withAlias('Total {{term kind.keyword}} Memory (GB) [384GB]')
    
              + elasticsearch.withBucketAggs([

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')


              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('E')
              +elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('Total {{term kind.keyword}} %CPU [240 cores]')
    
              + elasticsearch.withBucketAggs([

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
  
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')


              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('F')
              +elasticsearch.withTimeField('timestamp'),




            ]),

            ////

            g.panel.stateTimeline.new('vdbench Latency  (sec)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-vdbench-results')

            
            + g.panel.stateTimeline.withDescription('Lower is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withDecimals(1)
            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMax(-1)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-blue'),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(1),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(10),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(20),

              stateTimeline.thresholdStep.withColor('dark-red')
              + stateTimeline.thresholdStep.withValue(50)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(50)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(131)

            + stateTimeline.withId(134)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&editPanel=133&from=now-45d&to=now')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('{{term Run.keyword}} : {{term Threads}}th : 1 {{term kind.keyword}}')
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('Run.keyword')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('Threads')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      


      
              ])

    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('Resp')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),

            ////


              elasticsearch.withAlias('"Total {{term kind.keyword}} Memory (GB) [384GB]')
              + elasticsearch.withBucketAggs([

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
              ])

              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')


              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp'),

            ////



            elasticsearch.withAlias('Total {{term kind.keyword}} %CPU [240 cores]')
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('D')
              +elasticsearch.withTimeField('timestamp'),

            ////


            elasticsearch.withAlias('{{term Run.keyword}} : {{term Threads}}th :{{term scale}} {{term kind.keyword}}s')
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('Run.keyword')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('Threads')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
              ])

              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('Resp')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])

              +elasticsearch.withQuery("SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('C')
              +elasticsearch.withTimeField('timestamp'),

            ////


            elasticsearch.withAlias('Total {{term kind.keyword}} Memory (GB) [384GB]')
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('E')
              +elasticsearch.withTimeField('timestamp'),

            ////

            elasticsearch.withAlias('Total {{term kind.keyword}} %CPU [240 cores]')
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('F')
              +elasticsearch.withTimeField('timestamp')

            ////



            ])



        ]),
      
      //////////////////////////////

       g.panel.row.new("Clusterbuster - Cpusoaker")
       + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(15)

        + g.panel.row.withId(180)

          + g.panel.row.withPanels([
            g.panel.stateTimeline.new('Cpusoaker')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-cpusoaker-results')
            + g.panel.stateTimeline.withDescription('Higher is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(10)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(182)

            + stateTimeline.withId(192)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])

            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.7)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('Max {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('test_description.pods')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('CPU Iterations/sec {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('iterations_cpu_sec')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("")
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp')

            ])
            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "Diff Max ( runc - kata)",
                "binary": {
                  "left": "Max runc",
                  "operator": "-",
                  "reducer": "sum",
                  "right": "Max kata"
                },
                "mode": "reduceRow",
                "reduce": {
                  "include": [
                    "Max kata",
                    "Max runc"
                  ],
                  "reducer": "range"
                }
                }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "Diff CPU( kata / runc)",
                "binary": {
                  "left": "CPU Iterations/sec kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "CPU Iterations/sec runc"
                },
                "mode": "binary",
                "reduce": {
                  "include": [
                    "CPU Iterations/sec runc",
                    "CPU Iterations/sec kata"
                  ],
                  "reducer": "diff"
                }
                }),
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "CPU Iterations/sec clusterbuster-ci": true,
                  "Diff Max ( runc - kata)": true,
                  "Max clusterbuster-ci": true
                },
                "indexByName": {
                  "CPU Iterations/sec clusterbuster-ci": 5,
                  "CPU Iterations/sec kata": 3,
                  "CPU Iterations/sec runc": 2,
                  "Diff CPU( kata / runc)": 6,
                  "Diff Max ( runc - kata)": 1,
                  "Max clusterbuster-ci": 4,
                  "Max kata": 8,
                  "Max runc": 7,
                  "Time": 0
                },
                "renameByName": {}
                }),
              stateTimeline.transformation.withId('convertFieldType')
                + stateTimeline.transformation.withOptions({
                "conversions": [
                  {
                    "destinationType": "number",
                    "targetField": "Ratio Last( kata/ runc)"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "Diff CPU( kata / runc)"
                  }
                ],
                "fields": {}
              }),
              





          
            ]),
          

            ////////////////////////////////

            g.panel.stateTimeline.new('')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-cpusoaker-results')
            + g.panel.stateTimeline.withDescription('Lower is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)
            
            + stateTimeline.fieldConfig.defaults.withDecimals(1)
            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMax(-1)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-blue'),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(1),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(10),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(20),

              stateTimeline.thresholdStep.withColor('dark-red')
              + stateTimeline.thresholdStep.withValue(50)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(3)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(192)

            + stateTimeline.withId(191)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])

            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.7)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('Max {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('test_description.pods')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////

            ])
            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "Diff Max ( runc - kata)",
                "binary": {
                  "left": "Max runc",
                  "operator": "-",
                  "reducer": "sum",
                  "right": "Max kata"
                },
                "mode": "reduceRow",
                "reduce": {
                  "include": [
                    "Max kata",
                    "Max runc"
                  ],
                  "reducer": "range"
                }
                }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "Diff CPU( kata / runc)",
                "binary": {
                  "left": "CPU Iterations/sec kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "CPU Iterations/sec runc"
                },
                "mode": "binary",
                "reduce": {
                  "include": [
                    "CPU Iterations/sec runc",
                    "CPU Iterations/sec kata"
                  ],
                  "reducer": "diff"
                }
                }),
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "CPU Iterations/sec clusterbuster-ci": true,
                  "Diff Max ( runc - kata)": false,
                  "Max clusterbuster-ci": true,
                  "Max kata": true,
                  "Max runc": true,
                  "Time": false
                },
                "indexByName": {
                  "CPU Iterations/sec kata": 14,
                  "CPU Iterations/sec runc": 13,
                  "Diff CPU( kata - runc)": 15,
                  "Diff First( kata - runc)": 6,
                  "Diff Max ( runc - kata)": 3,
                  "Diff Memory( kata - runc)": 12,
                  "First start (sec) kata": 5,
                  "First start (sec) runc": 4,
                  "Last start (sec) kata": 8,
                  "Last start (sec) runc": 7,
                  "Max kata": 2,
                  "Max runc": 1,
                  "Memory (GB) kata": 11,
                  "Memory (GB) runc": 10,
                  "Ratio Last( kata/ runc)": 9,
                  "Time": 0
                },
                "renameByName": {}
              }),
              stateTimeline.transformation.withId('convertFieldType')
                + stateTimeline.transformation.withOptions({
                "conversions": [
                  {
                    "destinationType": "number",
                    "targetField": "Ratio Last( kata/ runc)"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "Diff CPU( kata / runc)"
                  }
                ],
                "fields": {}
              }),
              





          
            ]),

            ////////////////////////////////

            g.panel.stateTimeline.new('')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-cpusoaker-results')
            + g.panel.stateTimeline.withDescription('Lower is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)
            
            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMax(-1)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-blue'),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(1),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(10),

              stateTimeline.thresholdStep.withColor('light-red')
              + stateTimeline.thresholdStep.withValue(20),

              stateTimeline.thresholdStep.withColor('dark-red')
              + stateTimeline.thresholdStep.withValue(50)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(10)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(195)

            + stateTimeline.withId(185)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])

            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('First start (sec) {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('first_pod_start')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              ////////

              elasticsearch.withAlias('Last start (sec) {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('last_pod_start')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("")
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp'),


              ///////

              elasticsearch.withAlias('Memory (MB) {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('memory_per_pod')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("")
              +elasticsearch.withRefId('C')
              +elasticsearch.withTimeField('timestamp'),





              //////

            ])
            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "Diff First( kata - runc)",
                "mode": "reduceRow",
                "reduce": {
                  "include": [
                    "First start (sec) runc",
                    "First start (sec) kata"
                  ],
                  "reducer": "diff"
                },
                "replaceFields": false
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "Ratio Last( kata/ runc)",
                "binary": {
                  "left": "Last start (sec) kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "Last start (sec) runc"
                },
                "mode": "binary",
                "reduce": {
                  "include": [
                    "Last start (sec) runc",
                    "Last start (sec) kata"
                  ],
                  "reducer": "diff"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "Diff Memory( kata - runc)",
                "binary": {
                  "left": "Memory (GB) runc",
                  "operator": "-",
                  "reducer": "sum",
                  "right": "Memory (GB) kata"
                },
                "mode": "reduceRow",
                "reduce": {
                  "include": [
                    "Memory (MB) runc",
                    "Memory (MB) kata"
                  ],
                  "reducer": "diff"
                }
              }),
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "First start (sec) clusterbuster-ci": true,
                  "Last start (sec) clusterbuster-ci": true,
                  "Memory (MB) clusterbuster-ci": true
                },
                "indexByName": {
                  "Diff First( kata - runc)": 3,
                  "Diff Memory( kata - runc)": 11,
                  "First start (sec) clusterbuster-ci": 7,
                  "First start (sec) kata": 2,
                  "First start (sec) runc": 1,
                  "Last start (sec) clusterbuster-ci": 8,
                  "Last start (sec) kata": 5,
                  "Last start (sec) runc": 4,
                  "Memory (MB) clusterbuster-ci": 12,
                  "Memory (MB) kata": 10,
                  "Memory (MB) runc": 9,
                  "Ratio Last( kata/ runc)": 6,
                  "Time": 0
                },
                "renameByName": {}
              }),
              stateTimeline.transformation.withId('convertFieldType')
                + stateTimeline.transformation.withOptions({
                "conversions": [
                  {
                    "destinationType": "number",
                    "targetField": "Ratio Last( kata/ runc)"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "Diff CPU( kata / runc)"
                  }
                ],
                "fields": {}
              }),
              





          
            ]),







          
          ]),




      ///////////////////////////////

      g.panel.row.new("Clusterbuster - FIO")
       + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(16)
        
        + g.panel.row.withId(148)

        + g.panel.row.withPanels([
        
          g.panel.stateTimeline.new('FIO (IOPS/Throughtput)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-fio-results')
            + g.panel.stateTimeline.withDescription('Higher is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(15)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(183)

            + stateTimeline.withId(167)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])
            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
               elasticsearch.withAlias('read.iops: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.iops')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('')
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('write.iops: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('write.iops')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('')
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('total.iops: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total.iops')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('')
              +elasticsearch.withRefId('C')
              +elasticsearch.withTimeField('timestamp'),


              //////

              elasticsearch.withAlias('read.throughput: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.throughput')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('')
              +elasticsearch.withRefId('D')
              +elasticsearch.withTimeField('timestamp'),


              //////

              elasticsearch.withAlias('write.throughput: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('write.throughput')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('')
              +elasticsearch.withRefId('E')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('total.throughput: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total.throughput')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('')
              +elasticsearch.withRefId('F')
              +elasticsearch.withTimeField('timestamp')
              
            ])

            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "read.iops kata/runc",
                "binary": {
                  "left": "read.iops: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "read.iops: runc"
                },
                "mode": "binary",
                "reduce": {
                  "include": [
                    "read.iops: runc",
                    "read.iops: kata"
                  ],
                  "reducer": "diffperc"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "write.iops kata/runc",
                "binary": {
                  "left": "write.iops: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "write.iops: runc"
                },
                "mode": "binary",
                "reduce": {
                  "include": [
                    "write.iops: runc",
                    "write.iops: kata"
                  ],
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "total.iops  kata/runc",
                "binary": {
                  "left": "total.iops: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "total.iops: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "read.throughput  kata/runc",
                "binary": {
                  "left": "read.throughput: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "read.throughput: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "write.throughput kata/runc",
                "binary": {
                  "left": "write.throughput: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "write.throughput: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "total.throughput kata/runc",
                "binary": {
                  "left": "total.throughput: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "total.throughput: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "read.iops: clusterbuster-ci": true,
                  "read.throughput: clusterbuster-ci": true,
                  "total.iops: clusterbuster-ci": true,
                  "total.throughput: clusterbuster-ci": true,
                  "write.iops: clusterbuster-ci": true,
                  "write.throughput: clusterbuster-ci": true
                },
                "indexByName": {
                  "Time": 0,
                  "read.iops kata/runc": 3,
                  "read.iops: kata": 2,
                  "read.iops: runc": 1,
                  "read.throughput  kata/runc": 12,
                  "read.throughput: kata": 11,
                  "read.throughput: runc": 10,
                  "total.iops  kata/runc": 9,
                  "total.iops: kata": 8,
                  "total.iops: runc": 7,
                  "total.throughput kata/runc": 18,
                  "total.throughput: kata": 17,
                  "total.throughput: runc": 16,
                  "write.iops kata/runc": 6,
                  "write.iops: kata": 5,
                  "write.iops: runc": 4,
                  "write.throughput kata/runc": 15,
                  "write.throughput: kata": 14,
                  "write.throughput: runc": 13
                },
                "renameByName": {}
              }),
              stateTimeline.transformation.withId('convertFieldType')
                + stateTimeline.transformation.withOptions({
                "conversions": [
                  {
                    "destinationType": "number",
                    "targetField": "read.iops kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "write.iops kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "total.iops  kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "read.throughput  kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "write.throughput kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "total.throughput kata/runc"
                  }
                ],
                "fields": {}
              }),
              





          
            ]),
            



        ]),


      ///////////////////////////////



      g.panel.row.new("Clusterbuster - Files")
       + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(17)
        
        + g.panel.row.withId(182)

        + g.panel.row.withPanels([
        
          g.panel.stateTimeline.new('Files (sec)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-files-results')
            + g.panel.stateTimeline.withDescription('Lower is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withDecimals(2)
            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMax(-1)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-blue'),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(1),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(10),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(20),

              stateTimeline.thresholdStep.withColor('dark-red')
              + stateTimeline.thresholdStep.withValue(50)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(16)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(184)

            + stateTimeline.withId(165)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])
            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
               elasticsearch.withAlias('create: 4096: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('create.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('test_description.filesize:4096')
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('create: 262,144:  {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('create.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('test_description.filesize:262144')
              +elasticsearch.withRefId('G')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('read : 4096: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('test_description.filesize:4096')
              +elasticsearch.withRefId('C')
              +elasticsearch.withTimeField('timestamp'),


              //////

              elasticsearch.withAlias('read : 262,144: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('test_description.filesize:262144')
              +elasticsearch.withRefId('I')
              +elasticsearch.withTimeField('timestamp'),


              //////

              elasticsearch.withAlias('remove : 4096: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('remove.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('test_description.filesize:4096')
              +elasticsearch.withRefId('E')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('remove : 262,144: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('remove.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('test_description.filesize:262144')
              +elasticsearch.withRefId('K')
              +elasticsearch.withTimeField('timestamp')
              
            ])

            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "create 4096 kata/runc",
                "binary": {
                  "left": "create: 4096: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "create: 4096: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "create 262,144 kata/runc",
                "binary": {
                  "left": "create: 262,144:  kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "create: 262,144:  runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "read 4096 kata/runc",
                "binary": {
                  "left": "read : 4096: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "read : 4096: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "read 262,144  kata/runc",
                "binary": {
                  "left": "read : 262,144: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "read : 262,144: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "remove 4096  kata/runc",
                "binary": {
                  "left": "remove : 4096: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "remove : 4096: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "remove 262,144 kata/runc",
                "binary": {
                  "left": "remove : 262,144: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "remove : 262,144: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "create: 262,144:  clusterbuster-ci": true,
                  "create: 4096: clusterbuster-ci": true,
                  "read : 262,144: clusterbuster-ci": true,
                  "read : 4096: clusterbuster-ci": true,
                  "remove : 262,144: clusterbuster-ci": true,
                  "remove : 4096: clusterbuster-ci": true
                },
                "indexByName": {
                  "Time": 0,
                  "create 262,144 kata/runc": 6,
                  "create 4096 kata/runc": 3,
                  "create: 262,144:  kata": 5,
                  "create: 262,144:  runc": 4,
                  "create: 4096: kata": 2,
                  "create: 4096: runc": 1,
                  "read 262,144  kata/runc": 12,
                  "read 4096 kata/runc": 9,
                  "read : 262,144: kata": 11,
                  "read : 262,144: runc": 10,
                  "read : 4096: kata": 8,
                  "read : 4096: runc": 7,
                  "remove 262,144 kata/runc": 18,
                  "remove 4096  kata/runc": 15,
                  "remove : 262,144: kata": 17,
                  "remove : 262,144: runc": 16,
                  "remove : 4096: kata": 14,
                  "remove : 4096: runc": 13
                },
                "renameByName": {}
              }),
              stateTimeline.transformation.withId('convertFieldType')
                + stateTimeline.transformation.withOptions({
                "conversions": [
                  {
                    "destinationType": "number",
                    "targetField": "create 4096 kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "create 262,144 kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "read 4096 kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "read 262,144  kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "remove 4096  kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "remove 262,144 kata/runc"
                  }
                ],
                "fields": {}
              }),
              





          
            ]),
            



        ]),


      ///////////////////////////////


       g.panel.row.new("Clusterbuster - Uperf")
       + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(18)
        
        + g.panel.row.withId(184)

        + g.panel.row.withPanels([
        
          g.panel.stateTimeline.new('Uperf (Latency)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-uperf-results')
            + g.panel.stateTimeline.withDescription('Lower is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withDecimals(2)
            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMax(-1)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-blue'),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(1),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(10),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(20),

              stateTimeline.thresholdStep.withColor('dark-red')
              + stateTimeline.thresholdStep.withValue(50)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(9)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(185)

            + stateTimeline.withId(169)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])
            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.7)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
               elasticsearch.withAlias('latency: {{term test_description.msgsize}}: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                 elasticsearch.bucketAggs.Terms.withField('test_description.msgsize')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('9')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('max_time_op')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value*1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('')
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////


            ])

            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "rate:64 kata/runc",
                "binary": {
                  "left": "rate: 64: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "rate: 64: runc"
                },
                "mode": "binary",
                "reduce": {
                  "include": [
                    "rate: 64: runc",
                    "rate: 64: kata"
                  ],
                  "reducer": "sum"
                },
                "replaceFields": false
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "rate:1024 kata/runc",
                "binary": {
                  "left": "rate: 1024: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "rate: 1024: runc"
                },
                "mode": "binary",
                "reduce": {
                  "include": [
                    "rate: 1024: runc",
                    "rate: 1024: kata"
                  ],
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "rate:8192 kata/runc",
                "binary": {
                  "left": "rate: 8192: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "rate: 8192: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "latency: 1024: clusterbuster-ci": true,
                  "latency: 64: clusterbuster-ci": true,
                  "latency: 8192: clusterbuster-ci": true
                },
                "indexByName": {
                  "Time": 0,
                  "rate: 1024: kata": 5,
                  "rate: 1024: runc": 4,
                  "rate: 64: kata": 2,
                  "rate: 64: runc": 1,
                  "rate: 8192: kata": 8,
                  "rate: 8192: runc": 7,
                  "rate:1024 kata/runc": 6,
                  "rate:64 kata/runc": 3,
                  "rate:8192 kata/runc": 9
                },
                "renameByName": {}
              }),
              stateTimeline.transformation.withId('convertFieldType')
                + stateTimeline.transformation.withOptions({
                "conversions": [
                  {
                    "destinationType": "number",
                    "targetField": "rate:64 kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "rate:1024 kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "rate:8192 kata/runc"
                  }
                ],
                "fields": {}
              }),
              





          
            ]),

        ///////////////
            


          g.panel.stateTimeline.new('Uperf (Throughput)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-uperf-results')
            + g.panel.stateTimeline.withDescription('Higher is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(12)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(194)

            + stateTimeline.withId(174)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])
            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.7)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
               elasticsearch.withAlias('rate: {{term test_description.msgsize}}: {{term test_description.runtime.keyword}}')
    
              + elasticsearch.withBucketAggs([
                 elasticsearch.bucketAggs.Terms.withField('test_description.msgsize')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
                
                 elasticsearch.bucketAggs.Terms.withField('test_description.runtime.keyword')
                + elasticsearch.bucketAggs.Terms.withId('9')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('rate')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery('')
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////


            ])

            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "rate: 64 kata/runc",
                "binary": {
                  "left": "rate: 64: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "rate: 64: runc"
                },
                "mode": "binary",
                "reduce": {
                  "include": [
                    "rate: 64: runc",
                    "rate: 64: kata"
                  ],
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "rate: 1024: kata/runc",
                "binary": {
                  "left": "rate: 1024: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "rate: 1024: runc"
                },
                "mode": "binary",
                "reduce": {
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('calculateField')
                + stateTimeline.transformation.withOptions({
                "alias": "rate:8192: kata/runc",
                "binary": {
                  "left": "rate: 8192: kata",
                  "operator": "/",
                  "reducer": "sum",
                  "right": "rate: 8192: runc"
                },
                "mode": "binary",
                "reduce": {
                  "include": [
                    "rate: 8192: runc",
                    "rate: 8192: kata"
                  ],
                  "reducer": "sum"
                }
              }),
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "rate: 1024: clusterbuster-ci": true,
                  "rate: 64: clusterbuster-ci": true,
                  "rate: 8192: clusterbuster-ci": true
                },
                "indexByName": {
                  "Time": 0,
                  "rate: 1024: kata": 5,
                  "rate: 1024: kata/runc": 6,
                  "rate: 1024: runc": 4,
                  "rate: 64 kata/runc": 3,
                  "rate: 64: kata": 2,
                  "rate: 64: runc": 1,
                  "rate: 8192: kata": 8,
                  "rate: 8192: runc": 7,
                  "rate:8192: kata/runc": 9
                },
                "renameByName": {}
              }),
              stateTimeline.transformation.withId('convertFieldType')
                + stateTimeline.transformation.withOptions({
                "conversions": [
                  {
                    "destinationType": "number",
                    "targetField": "rate: 64 kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "rate: 1024: kata/runc"
                  },
                  {
                    "destinationType": "number",
                    "targetField": "rate:8192: kata/runc"
                  }
                ],
                "fields": {}
              }),
              





          
            ])
        ]),


        




      ///////////////////////////////



      

      g.panel.row.new("Clusterbuster - release")
       + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(19)

        + g.panel.row.withId(157)

          + g.panel.row.withPanels([
            g.panel.stateTimeline.new('clusterbuster-cpusoaker [OVN - 09/19]')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-cpusoaker-release-results')
            + g.panel.stateTimeline.withDescription('OVN - 09/19')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(36)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(261)

            + stateTimeline.withId(164)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=1659592686997&to=1663480686997&viewPanel=166')

            ])

            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('pod: max')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('test_description.pods')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc'")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata: max')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('test_description.pods')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata'")
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp'),


                //////


              elasticsearch.withAlias('pod: Memory per pod (MB)')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('memory_per_pod')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc'")
              +elasticsearch.withRefId('C')
              +elasticsearch.withTimeField('timestamp'),


                //////


              elasticsearch.withAlias('kata: Memory per kata  (MB)')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('memory_per_pod')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata'")
              +elasticsearch.withRefId('D')
              +elasticsearch.withTimeField('timestamp'),

              //////


              elasticsearch.withAlias('"pod: start per seconds')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('pod_starts_per_second')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc'")
              +elasticsearch.withRefId('E')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata: start per seconds')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('pod_starts_per_second')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata'")
              +elasticsearch.withRefId('F')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('pod: Iteration cpu sec')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('iterations_cpu_sec')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc'")
              +elasticsearch.withRefId('G')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata: Iteration cpu sec')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('iterations_cpu_sec')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata'")
              +elasticsearch.withRefId('H')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('pod: Iteration sec')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('iterations_sec')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc'")
              +elasticsearch.withRefId('I')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata: Iteration sec')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
              + stateTimeline.datasource.withType('elasticsearch')
              + stateTimeline.datasource.withUid('cd4b9568-576c-4528-b200-89b91a098410')
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('iterations_sec')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata'")
              +elasticsearch.withRefId('J')
              +elasticsearch.withTimeField('timestamp')


            ]),






            /////////////////////////////////////////////





            g.panel.stateTimeline.new('clusterbuster-files: elapsed_time: Direct/ 64 dirs/files')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-files-release-results')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(36)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(297)

            + stateTimeline.withId(153)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])

            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('pod: create: filesize 4096')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('create.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc' and test_description.filesize:4096")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata: create: filesize 4096')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('create.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata' and test_description.filesize:4096")
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp'),


                //////


              elasticsearch.withAlias('pod: read :  filesize 4096')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc' and test_description.filesize:4096")
              +elasticsearch.withRefId('C')
              +elasticsearch.withTimeField('timestamp'),


                //////


              elasticsearch.withAlias('kata: read:  filesize 4096')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata' and test_description.filesize:4096")
              +elasticsearch.withRefId('D')
              +elasticsearch.withTimeField('timestamp'),

              //////


              elasticsearch.withAlias('pod: remove :  filesize 4096')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('remove.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc' and test_description.filesize:4096")
              +elasticsearch.withRefId('E')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata: remove:  filesize 4096')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('remove.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata' and test_description.filesize:4096")
              +elasticsearch.withRefId('F')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('pod: create: filesize 262,144')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('create.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc' and test_description.filesize:262144")
              +elasticsearch.withRefId('G')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata: create:  filesize 262,144')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('create.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata' and test_description.filesize:262144")
              +elasticsearch.withRefId('H')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('pod: read :  filesize 262,144')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc' and test_description.filesize:262144")
              +elasticsearch.withRefId('I')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata: read :  filesize 262,144')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata' and test_description.filesize:262144")
              +elasticsearch.withRefId('J')
              +elasticsearch.withTimeField('timestamp'),


               //////


              elasticsearch.withAlias('pod: remove :  filesize 262,144')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('remove.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc' and test_description.filesize:262144")
              +elasticsearch.withRefId('K')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata: remove:  filesize 262,144')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('remove.elapsed_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata' and test_description.filesize:262144")
              +elasticsearch.withRefId('K')
              +elasticsearch.withTimeField('timestamp')


            ]),







              /////////////////////////////////////////////





            g.panel.stateTimeline.new('clusterbuster-fio')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-fio-release-results')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(36)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(333)

            + stateTimeline.withId(168)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])

            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('runc read')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.iops')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc'")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata read')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('read.iops')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata'")
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp')
            ]),






              /////////////////////////////////////////////





            g.panel.stateTimeline.new('clusterbuster-uperf')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-clusterbuster-uperf-release-results')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(70)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withMappings([])
            + stateTimeline.standardOptions.withMin(0)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('red'),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(36)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(369)

            + stateTimeline.withId(170)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=150')

            ])

            + stateTimeline.options.withAlignValue('left')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('auto')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('runc rate')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('rate')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='runc'")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),


              //////


              elasticsearch.withAlias('kata rate')
    
              + elasticsearch.withBucketAggs([
                
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

      
              ])
    
              + elasticsearch.withHide(false)
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('rate')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('6')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              +elasticsearch.withQuery("test_description.runtime='kata'")
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp')
            ])



          ]),















        //////////////////////////////////////////////////////


        g.panel.row.new("BootStorm")
        + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(20)

        + g.panel.row.withId(176)

          + g.panel.row.withPanels([
            g.panel.stateTimeline.new('300 Fedora37 VMs(Sec)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-bootstorm-results')
            + g.panel.stateTimeline.withDescription('Time till VM Login - Lower is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(77)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withDecimals(1)
            + stateTimeline.fieldConfig.defaults.withMappings([
              stateTimeline.valueMapping.ValueMap.withOptions(
                {	
                  "0": {	
                  "color": "transparent",	
                  "index": 0,	
                  "text": "."	
                  }     	
                }
              )
              + stateTimeline.valueMapping.ValueMap.withType('value')

            ])
            + stateTimeline.standardOptions.withMax(-1)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-blue'),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(1),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(10),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(20),

              stateTimeline.thresholdStep.withColor('dark-red')
              + stateTimeline.thresholdStep.withValue(50)

            ])
            + stateTimeline.standardOptions.withUnit('none')
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(19)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(187)

            + stateTimeline.withId(178)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/regression-summary?orgId=1&from=now-45d&to=now&viewPanel=190')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('hidden')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('Min')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Min.withField('bootstorm_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Min.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Min.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Min.withType('min')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('Max')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('bootstorm_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('B')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withField('bootstorm_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.settings.withPercents(['25', '50', '75', '95', '99'])
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withType('percentiles')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('C')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('AVG. 100 vms {{term node.keyword}}')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('node.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('bootstorm_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('D')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('Memory(GB) [384GB]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('F')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('Memory Worker-0 (GB) [128GB]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-0_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('E')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('Memory Worker-1 (GB) [128GB]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-1_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('G')
              + elasticsearch.withTimeField('timestamp'),

              ////



              elasticsearch.withAlias('Memory Worker-2 (GB) [128GB]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-2_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('H')
              + elasticsearch.withTimeField('timestamp'),

              ////



              elasticsearch.withAlias('%CPU [240 cores]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('I')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('%CPU worker-0 [80 cores]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-0_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('J')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('%CPU worker-1 [80 cores]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-1_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('K')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('%CPU worker-2 [80 cores]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-2_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('L')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('VMs #')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.UniqueCount.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.UniqueCount.withType('count')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('M')
              + elasticsearch.withTimeField('timestamp')

              ////









            ]),
            
            ////////////////////////
            
            
            g.panel.stateTimeline.new('120 Windows Server 2019 VMs virtio (Sec)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-windows-results')
            + g.panel.stateTimeline.withDescription('Time till VM Login - Lower is better')

            + stateTimeline.standardOptions.color.withMode('thresholds')
            + stateTimeline.fieldConfig.defaults.custom.withFillOpacity(77)
            + stateTimeline.fieldConfig.defaults.custom.withLineWidth(0)

            + stateTimeline.fieldConfig.defaults.withDecimals(1)
            + stateTimeline.fieldConfig.defaults.withMappings([
              stateTimeline.valueMapping.ValueMap.withOptions(
                {	
                  "0": {	
                  "color": "transparent",	
                  "index": 0,	
                  "text": "."	
                  }     	
                }
              )
              + stateTimeline.valueMapping.ValueMap.withType('value')

            ])
            + stateTimeline.standardOptions.withMax(-1)
            + stateTimeline.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('dark-blue'),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(1),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(10),

              stateTimeline.thresholdStep.withColor('semi-dark-orange')
              + stateTimeline.thresholdStep.withValue(20),

              stateTimeline.thresholdStep.withColor('dark-red')
              + stateTimeline.thresholdStep.withValue(50)

            ])
            + stateTimeline.standardOptions.withUnit('none')
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(19)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(206)

            + stateTimeline.withId(193)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('https://grafana-perf-chmf5l4sh776bznl3b.ibm.rhperfscale.org/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=194')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('hidden')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('Min')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Min.withField('bootstorm_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Min.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Min.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Min.withType('min')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('Max')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('bootstorm_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('B')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])
              
              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withField('bootstorm_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.settings.withPercents(['25', '50', '75', '95', '99'])
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withType('percentiles')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('C')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('AVG. 40 vms {{term node.keyword}}')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('node.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('bootstorm_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('D')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('Memory(GB) [384GB]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000/2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('F')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('Memory Worker-0 (GB) [128GB]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-0_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000/2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:300 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('E')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('Memory Worker-1 (GB) [128GB]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-1_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000/2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('G')
              + elasticsearch.withTimeField('timestamp'),

              ////



              elasticsearch.withAlias('Memory Worker-2 (GB) [128GB]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-2_Memory')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000000000/2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('H')
              + elasticsearch.withTimeField('timestamp'),

              ////



              elasticsearch.withAlias('%CPU [240 cores]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('I')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('%CPU worker-0 [80 cores]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-0_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('J')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('%CPU worker-1 [80 cores]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-1_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('K')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('%CPU worker-2 [80 cores]')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('worker-2_CPU')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('L')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('VMs #')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
      
      
              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.UniqueCount.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.UniqueCount.withType('count')
         
              ])

              + elasticsearch.withQuery('scale:120 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('M')
              + elasticsearch.withTimeField('timestamp')

              ////









            ])



          ]),

        g.panel.row.new("Artifacts")
        + g.panel.row.withCollapsed(value=true)

        + g.panel.row.gridPos.withH(1)
        + g.panel.row.gridPos.withW(24)
        + g.panel.row.gridPos.withX(0)
        + g.panel.row.gridPos.withY(21)

        + g.panel.row.withId(125)

        + g.panel.row.withPanels([
          g.panel.table.new("HammerDB artifacts")
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-hammerdb-results')
          + g.panel.table.fieldConfig.defaults.thresholds.withMode('thresholds')

          + g.panel.table.panelOptions.withLinks([
              g.panel.table.link.withTargetBlank(true)
              + g.panel.table.link.withTitle('link')
              + g.panel.table.link.withUrl('${__data.fields[\'run_artifacts_url.keyword\']}')

          ])

          + g.panel.table.fieldConfig.defaults.withMappings([])
            + g.panel.table.standardOptions.withMin(0)
            + g.panel.table.fieldConfig.defaults.thresholds.withMode('percentage')
            + g.panel.table.fieldConfig.defaults.thresholds.withSteps([
              g.panel.table.thresholdStep.withColor('semi-dark-red'),

              g.panel.table.thresholdStep.withColor('light-orange')
              + g.panel.table.thresholdStep.withValue(50),

              g.panel.table.thresholdStep.withColor('super-light-green')
              + g.panel.table.thresholdStep.withValue(80),

              g.panel.table.thresholdStep.withColor('dark-green')
              + g.panel.table.thresholdStep.withValue(90),

              g.panel.table.thresholdStep.withColor('dark-blue')
              + g.panel.table.thresholdStep.withValue(100)

            ])
            + g.panel.table.fieldConfig.withOverrides([
              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('ci_date.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(146),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Date')
              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('db_type.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(137),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Database')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('current_worker')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(134),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Thread')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('kind.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(159),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Kind')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(1068),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Artifacts Link')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('storage_type.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Storage')

              ])


            ])

            + g.panel.table.gridPos.withH(28)
            + g.panel.table.gridPos.withW(24)
            + g.panel.table.gridPos.withX(0)
            + g.panel.table.gridPos.withY(22)

            + g.panel.table.withId(128)
            + g.panel.table.queryOptions.withInterval('1d')
            + g.panel.table.options.footer.TableFooterOptions.withFields('')
            + g.panel.table.options.footer.TableFooterOptions.withReducer('sum')
            + g.panel.table.options.footer.TableFooterOptions.withShow(false)
            + g.panel.table.options.withShowHeader(true)
            + g.panel.table.options.withSortBy([])
            + g.panel.table.withPluginVersion('8.4.0-pre')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('ci_date.keyword')
                + elasticsearch.bucketAggs.Terms.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('db_type.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('current_worker')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('5')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
                elasticsearch.bucketAggs.DateHistogram.withField('storage_type.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('run_artifacts_url.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms')
      
      


      
              ])
    
              
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('tpm')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')


              ])
              + elasticsearch.withQuery('_exists_:tpm AND db_type:$db_type AND current_worker:$current_worker AND kind:$kind')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')
            ]),





            ////////////////




          g.panel.table.new("Uperf artifacts")
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-uperf-results')
          + g.panel.table.fieldConfig.defaults.thresholds.withMode('thresholds')
          + g.panel.table.standardOptions.withDecimals(1)

          + g.panel.table.panelOptions.withLinks([
              g.panel.table.link.withTargetBlank(true)
              + g.panel.table.link.withTitle('link')
              + g.panel.table.link.withUrl('${__data.fields[\'run_artifacts_url.keyword\']}')

          ])

          + g.panel.table.fieldConfig.defaults.withMappings([])
            + g.panel.table.standardOptions.withMin(0)
            + g.panel.table.fieldConfig.defaults.thresholds.withMode('percentage')
            + g.panel.table.fieldConfig.defaults.thresholds.withSteps([
              g.panel.table.thresholdStep.withColor('semi-dark-red'),

              g.panel.table.thresholdStep.withColor('light-orange')
              + g.panel.table.thresholdStep.withValue(50),

              g.panel.table.thresholdStep.withColor('super-light-green')
              + g.panel.table.thresholdStep.withValue(80),

              g.panel.table.thresholdStep.withColor('dark-green')
              + g.panel.table.thresholdStep.withValue(90),

              g.panel.table.thresholdStep.withColor('dark-blue')
              + g.panel.table.thresholdStep.withValue(100)

            ])
            + g.panel.table.fieldConfig.withOverrides([
              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('ci_date.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(169),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Date')
              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('read_message_size')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(167),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Read Message Size')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('num_threads')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(125),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Thread')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('kind.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(114),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Kind')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(1068),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Artifacts Link')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Average')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Average Gbits')

              ])


            ])

            + g.panel.table.gridPos.withH(15)
            + g.panel.table.gridPos.withW(24)
            + g.panel.table.gridPos.withX(0)
            + g.panel.table.gridPos.withY(50)

            + g.panel.table.withId(129)
            + g.panel.table.queryOptions.withInterval('1d')
            + g.panel.table.options.footer.TableFooterOptions.withFields('')
            + g.panel.table.options.footer.TableFooterOptions.withReducer('sum')
            + g.panel.table.options.footer.TableFooterOptions.withShow(false)
            + g.panel.table.options.withShowHeader(true)
            + g.panel.table.options.withSortBy([])
            + g.panel.table.withPluginVersion('8.4.0-pre')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('ci_date.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('5')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('read_message_size')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('num_threads')
                + elasticsearch.bucketAggs.Terms.withId('5')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('asc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('run_artifacts_url.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms')
      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('norm_byte')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value*8/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])
              + elasticsearch.withQuery('_exists_:norm_ops AND read_message_size:(64 OR 1024 OR 8192) AND num_threads:(1 OR 8) AND test_type:stream')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('uperf_ts')
            ]),

          


          //////////////////////

          g.panel.table.new("vdbench artifacts")
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-vdbench-results')
          + g.panel.table.fieldConfig.defaults.thresholds.withMode('thresholds')
          + g.panel.table.standardOptions.withDecimals(1)

          + g.panel.table.panelOptions.withLinks([
              g.panel.table.link.withTargetBlank(true)
              + g.panel.table.link.withTitle('link')
              + g.panel.table.link.withUrl('${__data.fields[\'run_artifacts_url.keyword\']}')

          ])

          + g.panel.table.fieldConfig.defaults.withMappings([])
            + g.panel.table.standardOptions.withMin(0)
            + g.panel.table.fieldConfig.defaults.thresholds.withMode('percentage')
            + g.panel.table.fieldConfig.defaults.thresholds.withSteps([
              g.panel.table.thresholdStep.withColor('semi-dark-red'),

              g.panel.table.thresholdStep.withColor('light-orange')
              + g.panel.table.thresholdStep.withValue(50),

              g.panel.table.thresholdStep.withColor('super-light-green')
              + g.panel.table.thresholdStep.withValue(80),

              g.panel.table.thresholdStep.withColor('dark-green')
              + g.panel.table.thresholdStep.withValue(90),

              g.panel.table.thresholdStep.withColor('dark-blue')
              + g.panel.table.thresholdStep.withValue(100)

            ])
            + g.panel.table.fieldConfig.withOverrides([
              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('ci_date.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(227),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Date')
              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('kind.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(100),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Kind')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(1000),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Artifacts Link')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Average')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Average Rate')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Run.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(140),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Run')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Threads')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(100),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Thread')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Artifacts Link')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(1521)

              ])


            ])

            + g.panel.table.gridPos.withH(10)
            + g.panel.table.gridPos.withW(24)
            + g.panel.table.gridPos.withX(0)
            + g.panel.table.gridPos.withY(65)

            + g.panel.table.withId(133)
            + g.panel.table.queryOptions.withInterval('1d')
            + g.panel.table.options.footer.TableFooterOptions.withFields('')
            + g.panel.table.options.footer.TableFooterOptions.withReducer('sum')
            + g.panel.table.options.footer.TableFooterOptions.withShow(false)
            + g.panel.table.options.withShowHeader(true)
            + g.panel.table.options.withSortBy([])
            + g.panel.table.withPluginVersion('8.4.0-pre')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('ci_date.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('5')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('7')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('run_artifacts_url.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms')
      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('Rate')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])
              + elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup'")
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')
            ])

            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "Average": true
                },
                "indexByName": {},
                "renameByName": {}
              })

          
            ]),

          //////////////////

          g.panel.table.new("vdbench scale artifacts")
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-vdbench-results')
          + g.panel.table.fieldConfig.defaults.thresholds.withMode('thresholds')
          + g.panel.table.standardOptions.withDecimals(1)

          + g.panel.table.panelOptions.withLinks([
              g.panel.table.link.withTargetBlank(true)
              + g.panel.table.link.withTitle('link')
              + g.panel.table.link.withUrl('${__data.fields[\"run_artifacts_url.keyword\"]}')

          ])

          + g.panel.table.fieldConfig.defaults.withMappings([])
            + g.panel.table.standardOptions.withMin(0)
            + g.panel.table.fieldConfig.defaults.thresholds.withMode('percentage')
            + g.panel.table.fieldConfig.defaults.thresholds.withSteps([
              g.panel.table.thresholdStep.withColor('semi-dark-red'),

              g.panel.table.thresholdStep.withColor('light-orange')
              + g.panel.table.thresholdStep.withValue(50),

              g.panel.table.thresholdStep.withColor('super-light-green')
              + g.panel.table.thresholdStep.withValue(80),

              g.panel.table.thresholdStep.withColor('dark-green')
              + g.panel.table.thresholdStep.withValue(90),

              g.panel.table.thresholdStep.withColor('dark-blue')
              + g.panel.table.thresholdStep.withValue(100)

            ])
            + g.panel.table.fieldConfig.withOverrides([
              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('ci_date.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(227),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Date')
              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('kind.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(100),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Kind')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(1000),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Artifacts Link')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Average')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Average Rate')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Run.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(140),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Run')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Threads')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(100),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Thread')

              ])


            ])

            + g.panel.table.gridPos.withH(10)
            + g.panel.table.gridPos.withW(24)
            + g.panel.table.gridPos.withX(0)
            + g.panel.table.gridPos.withY(75)

            + g.panel.table.withId(195)
            + g.panel.table.queryOptions.withInterval('1d')
            + g.panel.table.options.footer.TableFooterOptions.withFields('')
            + g.panel.table.options.footer.TableFooterOptions.withReducer('sum')
            + g.panel.table.options.footer.TableFooterOptions.withShow(false)
            + g.panel.table.options.withShowHeader(true)
            + g.panel.table.options.sortBy.withDesc(true)
            + g.panel.table.options.sortBy.withDesc('ci_date.keyword')

            + g.panel.table.withPluginVersion('8.4.0-pre')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('ci_date.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('5')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('Run.keyword')
                + elasticsearch.bucketAggs.Terms.withId('5')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('Threads')
                + elasticsearch.bucketAggs.DateHistogram.withId('6')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('kind.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('7')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('scale')
                + elasticsearch.bucketAggs.DateHistogram.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('run_artifacts_url.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('9')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
              ])
              + elasticsearch.withHide(false)
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('Rate')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])
              + elasticsearch.withQuery("!Run.keyword='fillup'")
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')
            ]),


          //////////////////

          g.panel.table.new("clusterbuster artifacts")
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-clusterbuster-results')
          + g.panel.table.fieldConfig.defaults.thresholds.withMode('thresholds')
          + g.panel.table.standardOptions.withDecimals(1)

          + g.panel.table.panelOptions.withLinks([
              g.panel.table.link.withTargetBlank(true)
              + g.panel.table.link.withTitle('link')
              + g.panel.table.link.withUrl('${__data.fields[\"run_artifacts_url.keyword\"]}')

          ])

          + g.panel.table.fieldConfig.defaults.withMappings([])
            + g.panel.table.standardOptions.withMin(0)
            + g.panel.table.fieldConfig.defaults.thresholds.withMode('percentage')
            + g.panel.table.fieldConfig.defaults.thresholds.withSteps([
              g.panel.table.thresholdStep.withColor('green'),

              g.panel.table.thresholdStep.withColor('red')
              + g.panel.table.thresholdStep.withValue(80)

            ])
            + g.panel.table.fieldConfig.withOverrides([
              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('run_artifacts_url')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(1600)
              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Date')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(227)
              ])

            ])

            + g.panel.table.gridPos.withH(6)
            + g.panel.table.gridPos.withW(24)
            + g.panel.table.gridPos.withX(0)
            + g.panel.table.gridPos.withY(85)

            + g.panel.table.withId(150)
            + g.panel.table.queryOptions.withInterval('1d')
            + g.panel.table.options.footer.TableFooterOptions.withFields('')
            + g.panel.table.options.footer.TableFooterOptions.withReducer('sum')
            + g.panel.table.options.footer.TableFooterOptions.withShow(false)
            + g.panel.table.options.withShowHeader(true)

            + g.panel.table.withPluginVersion('8.4.0-pre')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('ci_date.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('5')
                + elasticsearch.bucketAggs.Terms.withType('terms'),


                elasticsearch.bucketAggs.Terms.withField('timestamp')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('run_artifacts_url.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('job_runtime')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withHide(false)
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])
              + elasticsearch.withQuery("")
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')
            ])
            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "Average": true,
                  "_id": true,
                  "_index": true,
                  "_type": true,
                  "highlight": true,
                  "job_end": true,
                  "job_runtime": true,
                  "job_start": true,
                  "kata_version": true,
                  "openshift_version": true,
                  "result": true,
                  "run_host": true,
                  "sort": true,
                  "uuid": true
                },
                "indexByName": {
                  "_id": 6,
                  "_index": 7,
                  "_type": 8,
                  "highlight": 9,
                  "job_end": 12,
                  "job_runtime": 10,
                  "job_start": 11,
                  "kata_version": 4,
                  "openshift_version": 3,
                  "result": 2,
                  "run_artifacts_url": 1,
                  "run_host": 5,
                  "sort": 13,
                  "timestamp": 0,
                  "uuid": 14
                },
                "renameByName": {
                  "Average": "Run time",
                  "run_artifacts_url": "Artifacts Link",
                  "run_artifacts_url.keyword": "Artifacts Link",
                  "timestamp": "Date"
                }
              }),
              





          
            ]),

          //////////////////

          g.panel.table.new("clusterbuster release artifacts")
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-clusterbuster-release-results')
          + g.panel.table.fieldConfig.defaults.thresholds.withMode('thresholds')
          + g.panel.table.standardOptions.withDecimals(1)

          + g.panel.table.panelOptions.withLinks([
              g.panel.table.link.withTargetBlank(true)
              + g.panel.table.link.withTitle('link')
              + g.panel.table.link.withUrl('${__data.fields[\"run_artifacts_url.keyword\"]}')

          ])

          + g.panel.table.fieldConfig.defaults.withMappings([])
            + g.panel.table.standardOptions.withMin(0)
            + g.panel.table.fieldConfig.defaults.thresholds.withMode('percentage')
            + g.panel.table.fieldConfig.defaults.thresholds.withSteps([
              g.panel.table.thresholdStep.withColor('green'),

              g.panel.table.thresholdStep.withColor('red')
              + g.panel.table.thresholdStep.withValue(80)

            ])
            + g.panel.table.fieldConfig.withOverrides([
              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('run_artifacts_url')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(1600)
              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Date')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(227)
              ])

            ])

            + g.panel.table.gridPos.withH(6)
            + g.panel.table.gridPos.withW(24)
            + g.panel.table.gridPos.withX(0)
            + g.panel.table.gridPos.withY(91)

            + g.panel.table.withId(166)
            + g.panel.table.options.footer.TableFooterOptions.withFields('')
            + g.panel.table.options.footer.TableFooterOptions.withReducer('sum')
            + g.panel.table.options.footer.TableFooterOptions.withShow(false)
            + g.panel.table.options.withShowHeader(true)

            + g.panel.table.withPluginVersion('8.4.0-pre')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([

                elasticsearch.bucketAggs.Terms.withField('timestamp')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('run_artifacts_url.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('3')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('job_runtime')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withHide(false)
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])
              + elasticsearch.withQuery("")
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')
            ])
            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "Average": true,
                  "_id": true,
                  "_index": true,
                  "_type": true,
                  "highlight": true,
                  "job_end": true,
                  "job_runtime": true,
                  "job_start": true,
                  "kata_version": true,
                  "openshift_version": true,
                  "result": true,
                  "run_host": true,
                  "sort": true,
                  "uuid": true
                },
                "indexByName": {
                  "_id": 6,
                  "_index": 7,
                  "_type": 8,
                  "highlight": 9,
                  "job_end": 12,
                  "job_runtime": 10,
                  "job_start": 11,
                  "kata_version": 4,
                  "openshift_version": 3,
                  "result": 2,
                  "run_artifacts_url": 1,
                  "run_host": 5,
                  "sort": 13,
                  "timestamp": 0,
                  "uuid": 14
                },
                "renameByName": {
                  "Average": "Run time",
                  "run_artifacts_url": "Artifacts Link",
                  "run_artifacts_url.keyword": "Artifacts Link",
                  "timestamp": "Date"
                }
              }),
              





          
            ]),

          //////////////////

          g.panel.table.new("bootstorm artifacts")
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-bootstorm-results')
          + g.panel.table.fieldConfig.defaults.thresholds.withMode('thresholds')
          + g.panel.table.standardOptions.withDecimals(1)

          + g.panel.table.panelOptions.withLinks([
              g.panel.table.link.withTargetBlank(true)
              + g.panel.table.link.withTitle('link')
              + g.panel.table.link.withUrl('${__data.fields[\"run_artifacts_url.keyword\"]}')

          ])

          + g.panel.table.fieldConfig.defaults.withMappings([])
            + g.panel.table.standardOptions.withMin(0)
            + g.panel.table.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('semi-dark-red'),

              stateTimeline.thresholdStep.withColor('light-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + g.panel.table.fieldConfig.withOverrides([
              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('ci_date.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(227),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Date')
              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('kind.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(100),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Kind')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(1000),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Artifacts Link')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Average')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Average Rate')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Run.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(140),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Run')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Threads')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(100),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Thread')

              ]),

            ])

            + g.panel.table.gridPos.withH(5)
            + g.panel.table.gridPos.withW(24)
            + g.panel.table.gridPos.withX(0)
            + g.panel.table.gridPos.withY(97)

            + g.panel.table.withId(190)
            + g.panel.table.options.footer.TableFooterOptions.withFields('')
            + g.panel.table.options.footer.TableFooterOptions.withReducer('sum')
            + g.panel.table.options.footer.TableFooterOptions.withShow(false)
            + g.panel.table.options.withShowHeader(true)
            + g.panel.table.options.sortBy.withDesc(true)
            + g.panel.table.options.sortBy.withDesc('ci_date.keyword')

            + g.panel.table.withPluginVersion('8.4.0-pre')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([

                elasticsearch.bucketAggs.Terms.withField('ci_date.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('9')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('100')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('run_artifacts_url.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('11')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('Rate')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])
              + elasticsearch.withQuery("scale:300")
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')
            ])
            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "Average": true
                },
                "indexByName": {},
                "renameByName": {}
              })
              





          
            ]),


          //////////////////

          g.panel.table.new("Windows artifacts")
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-windows-results')
          + g.panel.table.fieldConfig.defaults.thresholds.withMode('thresholds')
          + g.panel.table.standardOptions.withDecimals(1)

          + g.panel.table.panelOptions.withLinks([
              g.panel.table.link.withTargetBlank(true)
              + g.panel.table.link.withTitle('link')
              + g.panel.table.link.withUrl('${__data.fields[\"run_artifacts_url.keyword\"]}')

          ])

          + g.panel.table.fieldConfig.defaults.withMappings([])
            + g.panel.table.standardOptions.withMin(0)
            + g.panel.table.fieldConfig.defaults.thresholds.withMode('percentage')
            + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
              stateTimeline.thresholdStep.withColor('semi-dark-red'),

              stateTimeline.thresholdStep.withColor('light-orange')
              + stateTimeline.thresholdStep.withValue(50),

              stateTimeline.thresholdStep.withColor('super-light-green')
              + stateTimeline.thresholdStep.withValue(80),

              stateTimeline.thresholdStep.withColor('dark-green')
              + stateTimeline.thresholdStep.withValue(90),

              stateTimeline.thresholdStep.withColor('dark-blue')
              + stateTimeline.thresholdStep.withValue(100)

            ])
            + g.panel.table.fieldConfig.withOverrides([
              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('ci_date.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(227),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Date')
              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('kind.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(100),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Kind')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(1000),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Artifacts Link')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Average')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Average Rate')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Run.keyword')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(140),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Run')

              ]),

              g.panel.table.fieldOverride.matcher.withId('byName')
              + g.panel.table.fieldOverride.matcher.withOptions('Threads')
              + g.panel.table.fieldOverride.withProperties([
                g.panel.table.fieldOverride.properties.withId('custom.width')
                + g.panel.table.fieldOverride.properties.withValue(100),
                g.panel.table.fieldOverride.properties.withId('displayName')
                + g.panel.table.fieldOverride.properties.withValue('Thread')

              ]),

            ])

            + g.panel.table.gridPos.withH(5)
            + g.panel.table.gridPos.withW(24)
            + g.panel.table.gridPos.withX(0)
            + g.panel.table.gridPos.withY(102)

            + g.panel.table.withId(194)
            + g.panel.table.withInterval('1d')

            + g.panel.table.options.footer.TableFooterOptions.withFields('')
            + g.panel.table.options.footer.TableFooterOptions.withReducer('sum')
            + g.panel.table.options.footer.TableFooterOptions.withShow(false)
            + g.panel.table.options.withShowHeader(true)
            + g.panel.table.options.sortBy.withDesc(true)
            + g.panel.table.options.sortBy.withDesc('ci_date.keyword')

            + g.panel.table.withPluginVersion('8.4.0-pre')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('')
    
              + elasticsearch.withBucketAggs([

                elasticsearch.bucketAggs.Terms.withField('ci_date.keyword')
                + elasticsearch.bucketAggs.Terms.withId('8')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('9')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('10')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('run_artifacts_url.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('11')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),
      
              ])
    
              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('Rate')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')


              ])
              + elasticsearch.withQuery("scale:120")
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')
            ])
            + stateTimeline.withTransformations([
              stateTimeline.transformation.withId('organize')
                + stateTimeline.transformation.withOptions({
                "excludeByName": {
                  "Average": true
                },
                "indexByName": {},
                "renameByName": {}
              })
              





          
            ]),

          /////////////

          g.panel.text.new('')

          + g.panel.text.gridPos.withH(4)
          + g.panel.text.gridPos.withW(5)
          + g.panel.text.gridPos.withX(19)
          + g.panel.text.gridPos.withY(107)

          + g.panel.text.withId('189')
          + g.panel.text.withDatasource('Elasticsearch-ci-status')

          + g.panel.text.panelOptions.withLinks([
              g.panel.text.link.withTargetBlank(true)
              + g.panel.text.link.withTitle('PerfCI')
              + g.panel.text.link.withUrl('https://github.com/redhat-performance/benchmark-runner/actions')

          ])

          + g.panel.text.options.withContent('![Cloud Governance](https://github.com/redhat-performance/benchmark-runner/blob/main/media/benchmark_runner.png?raw=true \"Tooltip Text\")\n')
          + g.panel.text.options.withMode("markdown")

          + g.panel.text.withPluginVersion('8.4.0-pre')

          + g.panel.text.withTargets([
            elasticsearch.withAlias('')

            + elasticsearch.withBucketAggs([
            elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
            + elasticsearch.bucketAggs.DateHistogram.withId('2')
            + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
            + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
            ])
       

            + elasticsearch.withMetrics([
              elasticsearch.metrics.Count.withId('1')
              + elasticsearch.metrics.Count.withType('count')
         
            ])

            + elasticsearch.withQuery('')
            + elasticsearch.withRefId('A')
            + elasticsearch.withTimeField('timestamp')


          ]),

    ////////////////////////////////////////////
                  
  




        ])

          





])

