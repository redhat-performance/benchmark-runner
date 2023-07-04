local g = import 'g.libsonnet';
local grafonnet = import 'github.com/grafana/grafonnet/gen/grafonnet-latest/main.libsonnet';
local elasticsearch = grafonnet.query.elasticsearch;
local stateTimeline = grafonnet.panel.stateTimeline;
local var = g.dashboard.variable;


g.dashboard.new('PerfCI-Regression-Summary')
+ g.dashboard.withTimepicker({},)
+ g.dashboard.withTimezone("")
+ g.dashboard.withUid('T4775LKnzzmichey')
+ g.dashboard.withVersion(409)
+ g.dashboard.withWeekStart("")


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

             + stateTimeline.fieldConfig.defaults.withMappings([
              stateTimeline.valueMapping.RegexMap.options.withPattern("41308")
              + stateTimeline.valueMapping.RegexMap.options.withResult("41308")
              + stateTimeline.valueMapping.RegexMap.options.result.withText('4.13.0-rc.8')
        

            ])
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
    g.panel.text.new('placeholder')
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
        stateTimeline.valueMapping.RangeMap.options.withFrom("41308")
        + stateTimeline.valueMapping.RangeMap.options.result.withIndex(1)
        + stateTimeline.valueMapping.RangeMap.options.result.withText('4.13.0-rc.8')
        

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

              +elasticsearch.withQuery('!SCALE AND !Run.keyword="fillup" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version')
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

              +elasticsearch.withQuery('!SCALE AND !Run.keyword="fillup" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version')
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

              +elasticsearch.withQuery('!SCALE AND !Run.keyword="fillup" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version')
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

              +elasticsearch.withQuery('SCALE AND !Run.keyword="fillup" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version')
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

              +elasticsearch.withQuery('SCALE AND !Run.keyword="fillup" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version')
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

              +elasticsearch.withQuery('SCALE AND !Run.keyword="fillup" AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version')
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
                + stateTimeline.transformation.withOptions()


          
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
              stateTimeline.valueMapping.SpecialValueMap.options.result.withColor('transparent')
              + stateTimeline.valueMapping.SpecialValueMap.options.result.withIndex(0)
              + stateTimeline.valueMapping.SpecialValueMap.options.result.withText('.')
              + stateTimeline.valueMapping.SpecialValueMap.withType('value')

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
              stateTimeline.valueMapping.SpecialValueMap.options.result.withColor('transparent')
              + stateTimeline.valueMapping.SpecialValueMap.options.result.withIndex(0)
              + stateTimeline.valueMapping.SpecialValueMap.options.result.withText('.')
              + stateTimeline.valueMapping.SpecialValueMap.withType('value')

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
          + g.panel.table.queryOptions.withTransformations([])
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
            ])

          














          

          









        ])

          































      











])

