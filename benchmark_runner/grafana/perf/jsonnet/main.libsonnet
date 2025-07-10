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

    + g.panel.text.withPluginVersion()

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

      + g.panel.text.options.withContent('![PerfCi](https://www.cielhr.com/wp-content/uploads/2019/10/PerformancewSpace-1080x675.png \"Tooltip Text\")\n')
      + g.panel.text.options.withMode("markdown")

      + g.panel.text.withPluginVersion()


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
        //START_VALUE_MAPPING_227
				 {"0": {"index": 0, "text": "fail"}, "1": {"index": 1, "text": "pass"}, "102": {"index": 13, "text": "1.0.2"}, "110": {"index": 14, "text": "1.1.0"}, "120": {"index": 15, "text": "1.2.0"}, "121": {"index": 16, "text": "1.2.1"}, "130": {"index": 45, "text": "1.3.0"}, "131": {"index": 117, "text": "1.3.1"}, "132": {"index": 76, "text": "1.3.2"}, "133": {"index": 77, "text": "1.3.3"}, "140": {"index": 118, "text": "1.4.0"}, "483": {"index": 0, "text": "4.8.3"}, "484": {"index": 1, "text": "4.8.4"}, "485": {"index": 2, "text": "4.8.5"}, "486": {"index": 3, "text": "4.8.6"}, "487": {"index": 4, "text": "4.8.7"}, "488": {"index": 5, "text": "4.8.8"}, "3025": {"index": 86, "text": "3.0.2-5"}, "3026": {"index": 119, "text": "3.0.2-6"}, "4102": {"index": 33, "text": "4.10.2"}, "4104": {"index": 34, "text": "4.10.4"}, "4105": {"index": 35, "text": "4.10.5"}, "4106": {"index": 36, "text": "4.10.6"}, "4108": {"index": 37, "text": "4.10.8"}, "4109": {"index": 38, "text": "4.10.9"}, "4114": {"index": 54, "text": "4.11.4"}, "4115": {"index": 55, "text": "4.11.5"}, "4116": {"index": 56, "text": "4.11.6"}, "4117": {"index": 57, "text": "4.11.7"}, "4118": {"index": 58, "text": "4.11.8"}, "4119": {"index": 59, "text": "4.11.9"}, "4120": {"index": 68, "text": "4.12.0"}, "4121": {"index": 69, "text": "4.12.1"}, "4122": {"index": 70, "text": "4.12.2"}, "4124": {"index": 80, "text": "4.12.4"}, "4130": {"index": 106, "text": "4.13.0"}, "4131": {"index": 109, "text": "4.13.1"}, "4132": {"index": 110, "text": "4.13.2"}, "4133": {"index": 111, "text": "4.13.3"}, "4814": {"index": 6, "text": "4.8.14"}, "4932": {"index": 8, "text": "4.9.3-2"}, "4947": {"index": 9, "text": "4.9.4-7"}, "4955": {"index": 10, "text": "4.9.5-5"}, "4961": {"index": 11, "text": "4.9.6-1"}, "4972": {"index": 12, "text": "4.9.7-2"}, "410012": {"index": 30, "text": "4.10.0-rc.2"}, "410013": {"index": 31, "text": "4.10.0-rc.3"}, "410017": {"index": 32, "text": "4.10.0-rc.7"}, "41010": {"index": 39, "text": "4.10.10"}, "41011": {"index": 40, "text": "4.10.11"}, "41012": {"index": 41, "text": "4.10.12"}, "41013": {"index": 42, "text": "4.10.13"}, "41014": {"index": 43, "text": "4.10.14"}, "41015": {"index": 44, "text": "4.10.15"}, "41016": {"index": 21, "text": "4.10.1-6"}, "41021": {"index": 28, "text": "4.10.2-1"}, "41023": {"index": 29, "text": "4.10.2-3"}, "41054": {"index": 49, "text": "4.10.5-4"}, "41066": {"index": 48, "text": "4.10.6-6"}, "41110": {"index": 60, "text": "4.11.10"}, "41111": {"index": 61, "text": "4.11.11"}, "41112": {"index": 62, "text": "4.11.12"}, "41113": {"index": 63, "text": "4.11.13"}, "41114": {"index": 64, "text": "4.11.14"}, "41144": {"index": 78, "text": "4.11.4-4"}, "41159": {"index": 79, "text": "4.11.5-9"}, "41206": {"index": 65, "text": "4.12.0.6"}, "41207": {"index": 66, "text": "4.12.0.7"}, "41208": {"index": 67, "text": "4.12.0.8"}, "41218": {"index": 73, "text": "4.12.1-8"}, "41224": {"index": 85, "text": "4.12.2-4"}, "413014": {"index": 102, "text": "4.13.0-rc.4"}, "413015": {"index": 103, "text": "4.13.0-rc.5"}, "413017": {"index": 104, "text": "4.13.0-rc.7"}, "413018": {"index": 105, "text": "4.13.0-rc.8"}, "49211": {"index": 7, "text": "4.9.2-11"}, "410129": {"index": 22, "text": "4.10.1-29"}, "410136": {"index": 23, "text": "4.10.1-36"}, "410160": {"index": 24, "text": "4.10.1-60"}, "410170": {"index": 25, "text": "4.10.1-70"}, "410197": {"index": 26, "text": "4.10.1-97"}, "411115": {"index": 52, "text": "4.11.1-15"}, "411121": {"index": 51, "text": "4.11.1-21"}, "411135": {"index": 46, "text": "4.11.1-35"}, "411142": {"index": 47, "text": "4.11.1-42"}, "411605": {"index": 53, "text": "4.11.6-5"}, "412116": {"index": 74, "text": "4.12.1-16"}, "412119": {"index": 84, "text": "4.12.1-19"}, "412122": {"index": 75, "text": "4.12.1-22"}, "412139": {"index": 82, "text": "4.12.1-39"}, "412140": {"index": 81, "text": "4.12.1-40"}, "412317": {"index": 121, "text": "4.12.3-17"}, "413004": {"index": 101, "text": "4.13.0-ec.4"}, "413118": {"index": 113, "text": "4.13.1-18"}, "413140": {"index": 114, "text": "4.13.1-40"}, "4100683": {"index": 17, "text": "4.10.0-683"}, "4100688": {"index": 18, "text": "4.10.0-688"}, "4100700": {"index": 19, "text": "4.10.0-700"}, "4100729": {"index": 20, "text": "4.10.0-729"}, "4101101": {"index": 27, "text": "4.10.1-101"}, "4110137": {"index": 50, "text": "4.11.0-137"}, "4120173": {"index": 83, "text": "4.12.0-173"}, "4120777": {"index": 71, "text": "4.12.0-777"}, "4120781": {"index": 72, "text": "4.12.0-781"}, "4131154": {"index": 115, "text": "4.13.1-154"}, "41301586": {"index": 88, "text": "4.13.0-1586"}, "41301649": {"index": 89, "text": "4.13.0-1649"}, "41301666": {"index": 91, "text": "4.13.0-1666"}, "41301689": {"index": 90, "text": "4.13.0-1689"}, "41301782": {"index": 92, "text": "4.13.0-1782"}, "41301856": {"index": 93, "text": "4.13.0-1856"}, "41301938": {"index": 94, "text": "4.13.0-1938"}, "41301943": {"index": 95, "text": "4.13.0-1943"}, "41302115": {"index": 96, "text": "4.13.0-2115"}, "41302176": {"index": 97, "text": "4.13.0-2176"}, "41302229": {"index": 98, "text": "4.13.0-2229"}, "41302251": {"index": 99, "text": "4.13.0-2251"}, "41302269": {"index": 100, "text": "4.13.0-2269"}, "413003": {"index": 87, "text": "4.13.0-ec.3"}, "CNV": {"index": 112, "text": "CNV"}, "KATA": {"index": 116, "text": "KATA"}, "OCP": {"index": 108, "text": "OCP"}, "ODF": {"index": 120, "text": "ODF"}, "Product Versions": {"index": 107, "text": "Product Versions"}, "4136": {"index": 122, "text": "4.13.6"}, "413360": {"index": 123, "text": "4.13.3-60"}, "41244": {"index": 126, "text": "4.12.4-4"}, "4134": {"index": 130, "text": "4.13.4"}, "4131206": {"index": 131, "text": "4.13.1-206"}, "4131214": {"index": 132, "text": "4.13.1-214"}, "41323": {"index": 133, "text": "4.13.2-3"}, "413273": {"index": 134, "text": "4.13.2-73"}, "41338": {"index": 135, "text": "4.13.3-8"}, "413267": {"index": 136, "text": "4.13.2-67"}, "4137": {"index": 137, "text": "4.13.7"}, "4133166": {"index": 138, "text": "4.13.3-166"}, "141": {"index": 139, "text": "1.4.1"}, "41252": {"index": 140, "text": "4.12.5-2"}, "4138": {"index": 141, "text": "4.13.8"}, "4133203": {"index": 142, "text": "4.13.3-203"}, "4139": {"index": 143, "text": "4.13.9"}, "413426": {"index": 145, "text": "4.13.4-26"}, "4133266": {"index": 146, "text": "4.13.3-266"}, "41310": {"index": 147, "text": "4.13.10"}, "413482": {"index": 148, "text": "4.13.4-82"}, "41263": {"index": 149, "text": "4.12.6-3"}, "41311": {"index": 150, "text": "4.13.11"}, "4134140": {"index": 151, "text": "4.13.4-140"}, "41272": {"index": 152, "text": "4.12.7-2"}, "41312": {"index": 153, "text": "4.13.12"}, "4134192": {"index": 154, "text": "4.13.4-192"}, "41313": {"index": 155, "text": "4.13.13"}, "4134237": {"index": 156, "text": "4.13.4-237"}, "414011": {"index": 157, "text": "4.14.0-rc.1"}, "41401991": {"index": 158, "text": "4.14.0-1991"}, "3132": {"index": 159, "text": "3.1.3-2"}, "41402040": {"index": 160, "text": "4.14.0-2040"}, "414012": {"index": 161, "text": "4.14.0-rc.2"}, "41402084": {"index": 162, "text": "4.14.0-2084"}, "41402117": {"index": 163, "text": "4.14.0-2117"}, "41336": {"index": 164, "text": "4.13.3-6"}, "414014": {"index": 165, "text": "4.14.0-rc.4"}, "41402178": {"index": 166, "text": "4.14.0-2178"}, "41402197": {"index": 167, "text": "4.14.0-2197"}, "414016": {"index": 168, "text": "4.14.0-rc.6"}, "41402245": {"index": 169, "text": "4.14.0-2245"}, "3134": {"index": 170, "text": "3.1.3-4"}, "41402256": {"index": 171, "text": "4.14.0-2256"}, "41402257": {"index": 172, "text": "4.14.0-2257"}, "41402258": {"index": 173, "text": "4.14.0-2258"}, "414017": {"index": 174, "text": "4.14.0-rc.7"}, "41402337": {"index": 175, "text": "4.14.0-2337"}, "41348": {"index": 176, "text": "4.13.4-8"}, "4141": {"index": 177, "text": "4.14.1"}, "41402356": {"index": 178, "text": "4.14.0-2356"}, "41402391": {"index": 179, "text": "4.14.0-2391"}, "41402399": {"index": 180, "text": "4.14.0-2399"}, "41402401": {"index": 181, "text": "4.14.0-2401"}, "41402419": {"index": 182, "text": "4.14.0-2419"}, "41402424": {"index": 183, "text": "4.14.0-2424"}, "4142": {"index": 184, "text": "4.14.2"}, "41402432": {"index": 185, "text": "4.14.0-2432"}, "4140161": {"index": 186, "text": "4.14.0-161"}, "414112": {"index": 187, "text": "4.14.1-12"}, "4143": {"index": 188, "text": "4.14.3"}, "414157": {"index": 189, "text": "4.14.1-57"}, "4144": {"index": 190, "text": "4.14.4"}, "414183": {"index": 191, "text": "4.14.1-83"}, "4141118": {"index": 192, "text": "4.14.1-118"}, "150": {"index": 193, "text": "1.5.0"}, "4145": {"index": 194, "text": "4.14.5"}, "4141136": {"index": 195, "text": "4.14.1-136"}, "4146": {"index": 196, "text": "4.14.6"}, "414162": {"index": 197, "text": "4.14.1-62"}, "414216": {"index": 198, "text": "4.14.2-16"}, "413511": {"index": 199, "text": "4.13.5-11"}, "4147": {"index": 200, "text": "4.14.7"}, "414294": {"index": 201, "text": "4.14.2-94"}, "41361": {"index": 202, "text": "4.13.6-1"}, "4142127": {"index": 203, "text": "4.14.2-127"}, "4142148": {"index": 204, "text": "4.14.2-148"}, "4148": {"index": 205, "text": "4.14.8"}, "4142199": {"index": 206, "text": "4.14.2-199"}, "414356": {"index": 207, "text": "4.14.3-56"}, "151": {"index": 208, "text": "1.5.1"}, "41329": {"index": 209, "text": "4.13.29"}, "4137315": {"index": 210, "text": "4.13.7-315"}, "412102": {"index": 211, "text": "4.12.10-2"}, "41410": {"index": 212, "text": "4.14.10"}, "4143123": {"index": 213, "text": "4.14.3-123"}, "4143168": {"index": 214, "text": "4.14.3-168"}, "4143196": {"index": 215, "text": "4.14.3-196"}, "41371": {"index": 216, "text": "4.13.7-1"}, "41412": {"index": 217, "text": "4.14.12"}, "414413": {"index": 218, "text": "4.14.4-13"}, "41413": {"index": 219, "text": "4.14.13"}, "152": {"index": 220, "text": "1.5.2"}, "414496": {"index": 221, "text": "4.14.4-96"}, "41414": {"index": 222, "text": "4.14.14"}, "4144142": {"index": 223, "text": "4.14.4-142"}, "41415": {"index": 224, "text": "4.14.15"}, "4144196": {"index": 225, "text": "4.14.4-196"}, "4144200": {"index": 226, "text": "4.14.4-200"}, "4152": {"index": 227, "text": "4.15.2"}, "415178": {"index": 228, "text": "4.15.1-78"}, "41459": {"index": 229, "text": "4.14.5-9"}, "4144204": {"index": 230, "text": "4.14.4-204"}, "": {"index": 231, "text": ""}, "4144237": {"index": 232, "text": "4.14.4-237"}, "4144248": {"index": 233, "text": "4.14.4-248"}, "4144265": {"index": 234, "text": "4.14.4-265"}, "4153": {"index": 235, "text": "4.15.3"}, "4151117": {"index": 236, "text": "4.15.1-117"}, "3204": {"index": 237, "text": "3.2.0-4"}, "4151140": {"index": 238, "text": "4.15.1-140"}, "4154": {"index": 239, "text": "4.15.4"}, "4151174": {"index": 240, "text": "4.15.1-174"}, "4144310": {"index": 241, "text": "4.14.4-310"}, "4144320": {"index": 242, "text": "4.14.4-320"}, "4144334": {"index": 243, "text": "4.14.4-334"}, "414580": {"index": 244, "text": "4.14.5-80"}, "414588": {"index": 245, "text": "4.14.5-88"}, "41420": {"index": 246, "text": "4.14.20"}, "4145146": {"index": 247, "text": "4.14.5-146"}, "41381": {"index": 248, "text": "4.13.8-1"}, "4159": {"index": 249, "text": "4.15.9"}, "415287": {"index": 250, "text": "4.15.2-87"}, "41461": {"index": 251, "text": "4.14.6-1"}, "41510": {"index": 252, "text": "4.15.10"}, "4152143": {"index": 253, "text": "4.15.2-143"}, "4152187": {"index": 254, "text": "4.15.2-187"}, "41512": {"index": 255, "text": "4.15.12"}, "4152249": {"index": 256, "text": "4.15.2-249"}, "41513": {"index": 257, "text": "4.15.13"}, "4152335": {"index": 258, "text": "4.15.2-335"}, "416011": {"index": 259, "text": "4.16.0-rc.1"}, "41602528": {"index": 260, "text": "4.16.0-2528"}, "41521": {"index": 261, "text": "4.15.2-1"}, "416012": {"index": 262, "text": "4.16.0-rc.2"}, "41602581": {"index": 263, "text": "4.16.0-2581"}, "41602591": {"index": 264, "text": "4.16.0-2591"}, "41602588": {"index": 265, "text": "4.16.0-2588"}, "416013": {"index": 266, "text": "4.16.0-rc.3"}, "41602624": {"index": 267, "text": "4.16.0-2624"}, "416014": {"index": 268, "text": "4.16.0-rc.4"}, "41602656": {"index": 269, "text": "4.16.0-2656"}, "41602666": {"index": 270, "text": "4.16.0-2666"}, "41539": {"index": 271, "text": "4.15.3-9"}, "416016": {"index": 272, "text": "4.16.0-rc.6"}, "41602693": {"index": 273, "text": "4.16.0-2693"}, "41602694": {"index": 274, "text": "4.16.0-2694"}, "41602702": {"index": 275, "text": "4.16.0-2702"}, "4160": {"index": 276, "text": "4.16.0"}, "41602730": {"index": 277, "text": "4.16.0-2730"}, "416018": {"index": 278, "text": "4.16.0-rc.8"}, "41602718": {"index": 279, "text": "4.16.0-2718"}, "4161": {"index": 280, "text": "4.16.1"}, "41602733": {"index": 281, "text": "4.16.0-2733"}, "41602732": {"index": 282, "text": "4.16.0-2732"}, "41602746": {"index": 283, "text": "4.16.0-2746"}, "4162": {"index": 284, "text": "4.16.2"}, "41602756": {"index": 285, "text": "4.16.0-2756"}, "41541": {"index": 286, "text": "4.15.4-1"}, "41602769": {"index": 287, "text": "4.16.0-2769"}, "4163": {"index": 288, "text": "4.16.3"}, "41555": {"index": 289, "text": "4.15.5-5"}, "4164": {"index": 290, "text": "4.16.4"}, "416170": {"index": 291, "text": "4.16.1-70"}, "4165": {"index": 292, "text": "4.16.5"}, "4161142": {"index": 293, "text": "4.16.1-142"}, "4166": {"index": 294, "text": "4.16.6"}, "4161160": {"index": 295, "text": "4.16.1-160"}, "416221": {"index": 296, "text": "4.16.2-21"}, "4167": {"index": 297, "text": "4.16.7"}, "416225": {"index": 298, "text": "4.16.2-25"}, "416224": {"index": 299, "text": "4.16.2-24"}, "416245": {"index": 300, "text": "4.16.2-45"}, "4168": {"index": 301, "text": "4.16.8"}, "416297": {"index": 302, "text": "4.16.2-97"}, "4169": {"index": 303, "text": "4.16.9"}, "4162113": {"index": 304, "text": "4.16.2-113"}, "4162124": {"index": 305, "text": "4.16.2-124"}, "41610": {"index": 306, "text": "4.16.10"}, "4162136": {"index": 307, "text": "4.16.2-136"}, "4162150": {"index": 308, "text": "4.16.2-150"}, "41611": {"index": 309, "text": "4.16.11"}, "41563": {"index": 310, "text": "4.15.6-3"}, "416333": {"index": 311, "text": "4.16.3-33"}, "41612": {"index": 312, "text": "4.16.12"}, "416350": {"index": 313, "text": "4.16.3-50"}, "41613": {"index": 314, "text": "4.16.13"}, "416397": {"index": 315, "text": "4.16.3-97"}, "41614": {"index": 316, "text": "4.16.14"}, "416399": {"index": 317, "text": "4.16.3-99"}, "41615": {"index": 318, "text": "4.16.15"}, "41649": {"index": 319, "text": "4.16.4-9"}, "416424": {"index": 320, "text": "4.16.4-24"}, "416427": {"index": 321, "text": "4.16.4-27"}, "41645": {"index": 322, "text": "4.16.4-5"}, "416430": {"index": 323, "text": "4.16.4-30"}, "416447": {"index": 324, "text": "4.16.4-47"}, "41616": {"index": 325, "text": "4.16.16"}, "416449": {"index": 326, "text": "4.16.4-49"}, "41572": {"index": 327, "text": "4.15.7-2"}, "416476": {"index": 328, "text": "4.16.4-76"}, "41617": {"index": 329, "text": "4.16.17"}, "416479": {"index": 330, "text": "4.16.4-79"}, "4164130": {"index": 331, "text": "4.16.4-130"}, "41618": {"index": 332, "text": "4.16.18"}, "4164132": {"index": 333, "text": "4.16.4-132"}, "4164171": {"index": 334, "text": "4.16.4-171"}, "41619": {"index": 335, "text": "4.16.19"}, "4164224": {"index": 336, "text": "4.16.4-224"}, "41620": {"index": 337, "text": "4.16.20"}, "4164226": {"index": 338, "text": "4.16.4-226"}, "4164253": {"index": 339, "text": "4.16.4-253"}, "41621": {"index": 340, "text": "4.16.21"}, "4164261": {"index": 341, "text": "4.16.4-261"}, "4164271": {"index": 342, "text": "4.16.4-271"}, "41623": {"index": 343, "text": "4.16.23"}, "4164287": {"index": 344, "text": "4.16.4-287"}, "4164302": {"index": 345, "text": "4.16.4-302"}, "416517": {"index": 346, "text": "4.16.5-17"}, "41586": {"index": 347, "text": "4.15.8-6"}, "41624": {"index": 348, "text": "4.16.24"}, "416562": {"index": 349, "text": "4.16.5-62"}, "41625": {"index": 350, "text": "4.16.25"}, "416571": {"index": 351, "text": "4.16.5-71"}, "416578": {"index": 352, "text": "4.16.5-78"}, "41626": {"index": 353, "text": "4.16.26"}, "4165104": {"index": 354, "text": "4.16.5-104"}, "4165118": {"index": 355, "text": "4.16.5-118"}, "41627": {"index": 356, "text": "4.16.27"}, "4165122": {"index": 357, "text": "4.16.5-122"}, "4165142": {"index": 358, "text": "4.16.5-142"}, "41423": {"index": 359, "text": "4.14.23"}, "414125": {"index": 360, "text": "4.14.12-5"}, "41628": {"index": 361, "text": "4.16.28"}, "41661": {"index": 362, "text": "4.16.6-1"}, "416666": {"index": 363, "text": "4.16.6-66"}, "41629": {"index": 364, "text": "4.16.29"}, "416692": {"index": 365, "text": "4.16.6-92"}, "41711": {"index": 366, "text": "4.17.11"}, "4173111": {"index": 367, "text": "4.17.3-111"}, "41712": {"index": 368, "text": "4.17.12"}, "417414": {"index": 369, "text": "4.17.4-14"}, "4172": {"index": 370, "text": "4.17.2"}, "417422": {"index": 371, "text": "4.17.4-22"}, "418013": {"index": 372, "text": "4.18.0-rc.3"}, "4180739": {"index": 373, "text": "4.18.0-739"}, "41713": {"index": 374, "text": "4.17.13"}, "417456": {"index": 375, "text": "4.17.4-56"}, "418015": {"index": 376, "text": "4.18.0-rc.5"}, "4180744": {"index": 377, "text": "4.18.0-744"}, "41714": {"index": 378, "text": "4.17.14"}, "417473": {"index": 379, "text": "4.17.4-73"}, "417481": {"index": 380, "text": "4.17.4-81"}, "418016": {"index": 381, "text": "4.18.0-rc.6"}, "4180804": {"index": 382, "text": "4.18.0-804"}, "4173": {"index": 383, "text": "4.17.3"}, "41715": {"index": 384, "text": "4.17.15"}, "417489": {"index": 385, "text": "4.17.4-89"}, "41716": {"index": 386, "text": "4.17.16"}, "41756": {"index": 387, "text": "4.17.5-6"}, "418018": {"index": 388, "text": "4.18.0-rc.8"}, "4180825": {"index": 389, "text": "4.18.0-825"}, "4174": {"index": 390, "text": "4.17.4"}, "41717": {"index": 391, "text": "4.17.17"}, "417515": {"index": 392, "text": "4.17.5-15"}, "4180110": {"index": 393, "text": "4.18.0-rc.10"}, "4180836": {"index": 394, "text": "4.18.0-836"}, "4181": {"index": 395, "text": "4.18.1"}, "4180848": {"index": 396, "text": "4.18.0-848"}, "4180847": {"index": 397, "text": "4.18.0-847"}, "4175": {"index": 398, "text": "4.17.5"}, "4182": {"index": 399, "text": "4.18.2"}, "4183": {"index": 400, "text": "4.18.3"}, "418110": {"index": 401, "text": "4.18.1-10"}, "418112": {"index": 402, "text": "4.18.1-12"}, "4184": {"index": 403, "text": "4.18.4"}, "418115": {"index": 404, "text": "4.18.1-15"}, "418117": {"index": 405, "text": "4.18.1-17"}, "418122": {"index": 406, "text": "4.18.1-22"}, "4185": {"index": 407, "text": "4.18.5"}, "418124": {"index": 408, "text": "4.18.1-24"}, "418131": {"index": 409, "text": "4.18.1-31"}, "4186": {"index": 410, "text": "4.18.6"}, "418139": {"index": 411, "text": "4.18.1-39"}, "418135": {"index": 412, "text": "4.18.1-35"}, "419003": {"index": 413, "text": "4.19.0-ec.3"}, "419075": {"index": 414, "text": "4.19.0-75"}, "419088": {"index": 415, "text": "4.19.0-88"}, "4187": {"index": 416, "text": "4.18.7"}, "418211": {"index": 417, "text": "4.18.2-11"}, "419004": {"index": 418, "text": "4.19.0-ec.4"}, "419099": {"index": 419, "text": "4.19.0-99"}, "4177": {"index": 420, "text": "4.17.7"}, "4176": {"index": 421, "text": "4.17.6"}, "4188": {"index": 422, "text": "4.18.8"}, "418213": {"index": 423, "text": "4.18.2-13"}, "4190100": {"index": 424, "text": "4.19.0-100"}, "4189": {"index": 425, "text": "4.18.9"}, "418225": {"index": 426, "text": "4.18.2-25"}, "41810": {"index": 427, "text": "4.18.10"}, "41831": {"index": 428, "text": "4.18.3-1"}, "4190117": {"index": 429, "text": "4.19.0-117"}, "419005": {"index": 443, "text": "4.19.0-ec.5"}, "4190124": {"index": 431, "text": "4.19.0-124"}, "41812": {"index": 432, "text": "4.18.12"}, "418312": {"index": 433, "text": "4.18.3-12"}, "41813": {"index": 434, "text": "4.18.13"}, "41847": {"index": 435, "text": "4.18.4-7"}, "4190145": {"index": 436, "text": "4.19.0-145"}, "4190154": {"index": 437, "text": "4.19.0-154"}, "419012": {"index": 438, "text": "4.19.0-rc.2"}, "4190160": {"index": 439, "text": "4.19.0-160"}, "4190170": {"index": 440, "text": "4.19.0-170"}, "4190164": {"index": 441, "text": "4.19.0-164"}, "4190174": {"index": 442, "text": "4.19.0-174"}, "419013": {"index": 443, "text": "4.19.0-rc.3"}, "419014": {"index": 444, "text": "4.19.0-rc.4"}, "419015": {"index": 445, "text": "4.19.0-rc.5"}, "4190188": {"index": 446, "text": "4.19.0-188"}, "41905": {"index": 447, "text": "4.19.0-rc.5"}, "4190187": {"index": 448, "text": "4.19.0-187"}, "41903": {"index": 449, "text": "4.19.0-rc.3"}, "41904": {"index": 450, "text": "4.19.0-rc.4"}, "4190192": {"index": 451, "text": "4.19.0-192"}, "41912": {"index": 452, "text": "4.19.1-2"}, "4191": {"index": 453, "text": "4.19.1"}, "41915": {"index": 454, "text": "4.19.1-5"}, "41913": {"index": 455, "text": "4.19.1-3"}, "419115": {"index": 456, "text": "4.19.1-15"}, "419116": {"index": 457, "text": "4.19.1-16"}, "4192": {"index": 458, "text": "4.19.2"}, "419120": {"index": 459, "text": "4.19.1-20"}, "419124": {"index": 460, "text": "4.19.1-24"}, "4193": {"index": 461, "text": "4.19.3"}, "419128": {"index": 462, "text": "4.19.1-28"}, "419130": {"index": 463, "text": "4.19.1-30"}, "419133": {"index": 464, "text": "4.19.1-33"}} 
 		    //END_VALUE_MAPPING_227
 		)
        + stateTimeline.valueMapping.RegexMap.withType('value')


      ])

      + stateTimeline.fieldConfig.defaults.thresholds.withMode('absolute')
      + stateTimeline.fieldConfig.defaults.thresholds.withSteps([
        g.panel.alertGroups.thresholdStep.withColor('green')
        + g.panel.alertGroups.thresholdStep.withValue(null)

      ])

      + stateTimeline.fieldConfig.withOverrides([
        stateTimeline.fieldOverride.byName.new('Ci Status')
              + g.panel.table.fieldOverride.byName.withProperty('color', {"mode": "continuous-GrYlRd"})
      ])

      + stateTimeline.gridPos.withH(6)
      + stateTimeline.gridPos.withW(24)
      + stateTimeline.gridPos.withX(0)
      + stateTimeline.gridPos.withY(6)

      + stateTimeline.withId(171)
      + stateTimeline.queryOptions.withInterval("1d")

      + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('CI Status')
              + stateTimeline.link.withUrl('http://jenkins.perf.lab.eng.bos.redhat.com/view/PerfCI/job/PerfCI-Workloads-Deployment')

      ])

      + stateTimeline.options.withAlignValue("right")
      + stateTimeline.options.legend.withDisplayMode("hidden")
      + stateTimeline.options.legend.withPlacement("bottom")
      + stateTimeline.options.withMergeValues(true)
      + stateTimeline.options.withRowHeight(0.85)
      + stateTimeline.options.withShowValue("always")
      + stateTimeline.options.tooltip.withMode("single")

      + stateTimeline.withPluginVersion()

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
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('Integer.parseInt(\"0\"+doc["ocp_version.keyword"].value.replace(\".\",\"\").replace(\"r\",\"1\").replace(\"e\",\"0\").replace(\"c\",\"\").replace(\"f\",\"\").replace(\"-\",\"\"))')
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
          + elasticsearch.withRefId('B')
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
          + elasticsearch.withRefId('C')
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
          + elasticsearch.withRefId('D')
          + elasticsearch.withTimeField('timestamp'),
        ////
        elasticsearch.withAlias('Ci Status')
          + elasticsearch.withBucketAggs([
            elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
            + elasticsearch.bucketAggs.DateHistogram.withId('2')
            + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
            + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')
          ])

          + elasticsearch.withHide(false)

          + elasticsearch.withMetrics([
            elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('status#')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withSettings({})
            + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

          ])

          + elasticsearch.withQuery('ocp_version:$ocp_version')
          + elasticsearch.withRefId('E')
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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=39')
            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + stateTimeline.withPluginVersion()


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
            ]),
          ////
          g.panel.stateTimeline.new('HammerDB VM Memory')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-hammerdb-results')
            + stateTimeline.withDescription("MariaDB: innodb_buffer_pool_size = 8GB \n\nPostgreSQL: shared_buffers = 4GB")

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

            + stateTimeline.gridPos.withH(13)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(51)

            + stateTimeline.withId(120)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=39')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + stateTimeline.withPluginVersion()


            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('{{term db_type.keyword}}  : {{field}} [GB]: {{term storage_type.keyword}}')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('db_type.keyword')
                + elasticsearch.bucketAggs.Terms.withId('3')
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

                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')





              ])



              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher Cache')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher working set bytes')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),


              ])
              + elasticsearch.withQuery('_exists_:tpm AND db_type:$db_type AND kind:vm AND ocp_version:$ocp_version')
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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=40')

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

              +elasticsearch.withQuery('_exists_:norm_ltcy AND read_message_size:(64 OR 1024 OR 8192) AND num_threads:(1 OR 8) AND test_type:rr AND norm_ltcy:<1000 AND kind:$kind AND ocp_version:$ocp_version')
              +elasticsearch.withRefId('A')
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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=40')

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

              +elasticsearch.withQuery('_exists_:norm_ops AND read_message_size:(64 OR 1024 OR 8192) AND num_threads:(1 OR 8) AND test_type:stream AND kind:$kind AND ocp_version:$ocp_version')
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp')

            ]),

          g.panel.stateTimeline.new('Uperf VM Memory')
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

            + stateTimeline.gridPos.withH(6)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(67)

            + stateTimeline.withId(115)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=40')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              elasticsearch.withAlias('{{field}} [GB]')

              + elasticsearch.withBucketAggs([


                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')





              ])


              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher Cache')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher working set bytes')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),


              ])

              +elasticsearch.withQuery('_exists_:norm_ops AND kind:vm AND ocp_version:$ocp_version')
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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=41'),

              stateTimeline.link.withTitle('scale artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=42')

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

              elasticsearch.withAlias('Total %CPU [240 cores]: 1 {{term kind.keyword}}')

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
              +elasticsearch.withRefId('B')
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

              +elasticsearch.withQuery("SCALE AND !Run.keyword='fillup' AND kind:$kind AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('C')
              +elasticsearch.withTimeField('timestamp'),


              ////

              elasticsearch.withAlias('Total %CPU [240 cores]: {{term scale}} {{term kind.keyword}}')

              + elasticsearch.withBucketAggs([

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('scale')
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
              +elasticsearch.withRefId('D')
              +elasticsearch.withTimeField('timestamp'),

            ////


            ]),

            ////

            g.panel.stateTimeline.new('vdbench Latency (sec)')
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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=41'),

              stateTimeline.link.withTitle('scale artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=42')

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

            elasticsearch.withAlias('Total %CPU [240 cores]: 1 {{term kind.keyword}}')
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
              +elasticsearch.withRefId('B')
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

             elasticsearch.withAlias('Total %CPU [240 cores]: {{term scale}} {{term kind.keyword}}')

              + elasticsearch.withBucketAggs([

                elasticsearch.bucketAggs.Terms.withField('kind.keyword')
                + elasticsearch.bucketAggs.Terms.withId('2')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.Terms.withField('scale')
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
              +elasticsearch.withRefId('D')
              +elasticsearch.withTimeField('timestamp'),

              ////


            ]),
            ////

            g.panel.stateTimeline.new('vdbench VM memory')
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

            + stateTimeline.gridPos.withH(10)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(131)

            + stateTimeline.withId(134)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=41'),

              stateTimeline.link.withTitle('scale artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=42')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('list')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([

             elasticsearch.withAlias('{{field}} [GB]: 1 vm')

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
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher Cache')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher working set bytes')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),


              ])

              +elasticsearch.withQuery("!SCALE AND !Run.keyword='fillup' AND kind:'vm' AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('A')
              +elasticsearch.withTimeField('timestamp'),

              ////


             elasticsearch.withAlias('{{field}} [GB]: {{term scale}} {{kind.keyword}}s')

              + elasticsearch.withBucketAggs([

                elasticsearch.bucketAggs.Terms.withField('scale')
                + elasticsearch.bucketAggs.Terms.withId('7')
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
                + elasticsearch.bucketAggs.DateHistogram.withId('5')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.settings.withMinDocCount('0')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTimeZone('utc')
                + elasticsearch.bucketAggs.DateHistogram.settings.withTrimEdges('0')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')


              ])


              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher Cache')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher working set bytes')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),


              ])

              +elasticsearch.withQuery("SCALE AND !Run.keyword='fillup' AND kind:'vm' AND Run:$vdbench_type AND ocp_version:$ocp_version")
              +elasticsearch.withRefId('B')
              +elasticsearch.withTimeField('timestamp'),

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=43')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=43')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=43')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=43')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=43')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=43')

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
                elasticsearch.metrics.MetricAggregationWithSettings.Average.withField('avg_time_op')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value*1000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.withType('avg')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=43')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=44')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=44')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=44')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=44')

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
            g.panel.stateTimeline.new('240 Fedora37 VMs(Sec)')
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

            + stateTimeline.gridPos.withH(10)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(187)

            + stateTimeline.withId(178)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=45')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('hidden')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              ////
              elasticsearch.withAlias('Min')

              + elasticsearch.withBucketAggs([
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

              + elasticsearch.withQuery('scale:240 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')


              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withField('bootstorm_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.settings.withPercents(['50', '90'])
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withType('percentiles')

              ])

              + elasticsearch.withQuery('scale:240 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('B')
              + elasticsearch.withTimeField('timestamp'),

              ///

              elasticsearch.withAlias('Max')

              + elasticsearch.withBucketAggs([
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

              + elasticsearch.withQuery('scale:240 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('C')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('{{field}} (min.)')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')


              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_run_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000/60')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              + elasticsearch.withQuery('scale:240 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('D')
              + elasticsearch.withTimeField('timestamp'),

              ////

            ]),
            ////////////////////////

            g.panel.stateTimeline.new('')
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
            + stateTimeline.standardOptions.withUnit('none')
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(3)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(187)

            + stateTimeline.withId(178)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=45')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('hidden')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              ////
              elasticsearch.withAlias('VMs #: Fedora')

              + elasticsearch.withBucketAggs([
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

              + elasticsearch.withQuery('scale:240 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')

              ////


            ]),

            ////////////////////////

            g.panel.stateTimeline.new('240 Fedora37 VM Memory')
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

            + stateTimeline.gridPos.withH(5)
            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(187)

            + stateTimeline.withId(178)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=45')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('hidden')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([

              elasticsearch.withAlias('{{field}} [GB]')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.DateHistogram.withField('timestamp')
                + elasticsearch.bucketAggs.DateHistogram.withId('2')
                + elasticsearch.bucketAggs.DateHistogram.settings.withInterval('auto')
                + elasticsearch.bucketAggs.DateHistogram.withType('date_histogram')

              ])

              + elasticsearch.withHide(false)

              + elasticsearch.withMetrics([
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher Cache')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher working set bytes')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),


              ])

              + elasticsearch.withQuery('scale:240 AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')

              ////

            ]),
            ////////////////////////


            g.panel.stateTimeline.new('111 Windows VMs virtio (Sec)')
            + stateTimeline.queryOptions.withDatasource('Elasticsearch-windows-results')
            + g.panel.stateTimeline.withDescription('Time till VM Login - Lower is better [changed to 111 vms in 01/07/2024]')

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
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=46')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('hidden')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([
              ////
              elasticsearch.withAlias('Min: {{term vm_os_version.keyword}}')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('vm_os_version.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
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

              + elasticsearch.withQuery('scale:(111 OR 120) AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('vm_os_version.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
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
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.settings.withPercents(['50', '90'])
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.settings.withScript('_value/1000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Percentiles.withType('percentiles')

              ])

              + elasticsearch.withQuery('scale:(111 OR 120) AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('B')
              + elasticsearch.withTimeField('timestamp'),

              ////

              elasticsearch.withAlias('Max: {{term vm_os_version.keyword}}')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('vm_os_version.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
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

              + elasticsearch.withQuery('scale:(111 OR 120) AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('C')
              + elasticsearch.withTimeField('timestamp'),

              ////


              elasticsearch.withAlias('{{field}} {{term vm_os_version.keyword}} (min.)')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('vm_os_version.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
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
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('total_run_time')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.settings.withScript('_value/1000/60')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max')

              ])

              + elasticsearch.withQuery('scale:(111 OR 120) AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('C')
              + elasticsearch.withTimeField('timestamp'),

              ////


            ]),
            ////////////////////////

            g.panel.stateTimeline.new('')
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
            + stateTimeline.standardOptions.withUnit('none')
            + stateTimeline.fieldConfig.withOverrides([])

            + stateTimeline.gridPos.withH(5)

            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(206)

            + stateTimeline.withId(193)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=46')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('hidden')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([

              elasticsearch.withAlias('VMs #: {{term vm_os_version.keyword}}')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('vm_os_version.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
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

              + elasticsearch.withQuery('scale:(111 OR 120) AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp')

              ////


            ]),
            ////////////////////////

            g.panel.stateTimeline.new('111 Windows VM Memory')
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

            + stateTimeline.gridPos.withH(9)

            + stateTimeline.gridPos.withW(24)
            + stateTimeline.gridPos.withX(0)
            + stateTimeline.gridPos.withY(206)

            + stateTimeline.withId(193)
            + stateTimeline.withInterval('1d')

            + stateTimeline.panelOptions.withLinks([
              stateTimeline.link.withTargetBlank(true)
              + stateTimeline.link.withTitle('artifacts link')
              + stateTimeline.link.withUrl('http://cnv-intel-15.perf.eng.bos2.dc.redhat.com:3000/d/T4775LKnzzmichey/perfci-regression-summary?orgId=1&from=now-45d&to=now&viewPanel=46')

            ])

            + stateTimeline.options.withAlignValue('center')
            + stateTimeline.options.legend.withDisplayMode('hidden')
            + stateTimeline.options.legend.withPlacement('bottom')
            + stateTimeline.options.withMergeValues(value = false)
            + stateTimeline.options.withRowHeight(value = 0.9)
            + stateTimeline.options.withShowValue('always')
            + stateTimeline.options.tooltip.withMode('single')

            + g.panel.stateTimeline.withTargets([

              ////

              elasticsearch.withAlias('{{field}} [GB]: {{term vm_os_version.keyword}}')

              + elasticsearch.withBucketAggs([
                elasticsearch.bucketAggs.Terms.withField('vm_os_version.keyword')
                + elasticsearch.bucketAggs.Terms.withId('4')
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
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher Cache')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('1')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),
                elasticsearch.metrics.MetricAggregationWithSettings.Max.withField('virt launcher working set bytes')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withId('2')
                + elasticsearch.metrics.MetricAggregationWithSettings.Average.settings.withScript('_value/1000000000')
                + elasticsearch.metrics.MetricAggregationWithSettings.Max.withType('max'),


              ])

              + elasticsearch.withQuery('scale:(111 OR 120) AND ocp_version:$ocp_version')
              + elasticsearch.withRefId('A')
              + elasticsearch.withTimeField('timestamp'),

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
              g.panel.table.fieldOverride.byName.new('ci_date.keyword')
             + g.panel.table.fieldOverride.byName.withProperty('custom.width',169)
             + g.panel.table.fieldOverride.byName.withProperty('displayName','Date'),

             g.panel.table.fieldOverride.byName.new('db_type.keyword')
             + g.panel.table.fieldOverride.byName.withProperty('custom.width',137)
             + g.panel.table.fieldOverride.byName.withProperty('displayName','Database'),

             g.panel.table.fieldOverride.byName.new('current_worker')
             + g.panel.table.fieldOverride.byName.withProperty('custom.width',134)
             + g.panel.table.fieldOverride.byName.withProperty('displayName','Thread'),

             g.panel.table.fieldOverride.byName.new('kind.keyword')
             + g.panel.table.fieldOverride.byName.withProperty('custom.width',159)
             + g.panel.table.fieldOverride.byName.withProperty('displayName','Kind'),

             g.panel.table.fieldOverride.byName.new('run_artifacts_url.keyword')
             + g.panel.table.fieldOverride.byName.withProperty('custom.width',1068)
             + g.panel.table.fieldOverride.byName.withProperty('displayName','Artifacts Link'),

             g.panel.table.fieldOverride.byName.new('storage_type.keyword')
             + g.panel.table.fieldOverride.byName.withProperty('displayName','Storage'),




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
            + g.panel.table.withPluginVersion()

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
              g.panel.table.fieldOverride.byName.new('ci_date.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',169)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Date'),

              g.panel.table.fieldOverride.byName.new('read_message_size')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',167)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Read Message Size'),

              g.panel.table.fieldOverride.byName.new('num_threads')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',125)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Thread'),

              g.panel.table.fieldOverride.byName.new('kind.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',114)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Kind'),

              g.panel.table.fieldOverride.byName.new('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',1068)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Artifacts Link'),

              g.panel.table.fieldOverride.byName.new('Average')
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Average Gbits')


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
            + g.panel.table.withPluginVersion()

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

              g.panel.table.fieldOverride.byName.new('ci_date.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',227)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Date'),

              g.panel.table.fieldOverride.byName.new('kind.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',100)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Kind'),

              g.panel.table.fieldOverride.byName.new('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',1000)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Artifacts Link'),

              g.panel.table.fieldOverride.byName.new('Average')
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Average Rate'),

              g.panel.table.fieldOverride.byName.new('Run.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',140)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Run'),

              g.panel.table.fieldOverride.byName.new('Threads')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',100)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Thread'),

              g.panel.table.fieldOverride.byName.new('Artifacts Link')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',1521)


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
            + g.panel.table.withPluginVersion()

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

              g.panel.table.fieldOverride.byName.new('ci_date.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',227)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Date'),

              g.panel.table.fieldOverride.byName.new('kind.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',100)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Kind'),

              g.panel.table.fieldOverride.byName.new('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',1000)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Artifacts Link'),

              g.panel.table.fieldOverride.byName.new('Average')
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Average Rate'),

              g.panel.table.fieldOverride.byName.new('Run.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',140)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Run'),

              g.panel.table.fieldOverride.byName.new('Threads')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',100)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Thread')


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

            + g.panel.table.withPluginVersion()

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
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-clusterbuster-metadata-results')
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

              g.panel.table.fieldOverride.byName.new('Artifacts Link')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',1600),

              g.panel.table.fieldOverride.byName.new('Date')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',227)

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

            + g.panel.table.withPluginVersion()

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

          g.panel.table.new("clusterbuster release artifacts")
          + g.panel.table.queryOptions.withDatasource('Elasticsearch-clusterbuster-metadata-release-results')
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

              g.panel.table.fieldOverride.byName.new('Artifacts Link')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',1600),

              g.panel.table.fieldOverride.byName.new('Date')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',227)


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

            + g.panel.table.withPluginVersion()

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

              g.panel.table.fieldOverride.byName.new('ci_date.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',227)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Date'),

              g.panel.table.fieldOverride.byName.new('kind.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',100)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Kind'),

              g.panel.table.fieldOverride.byName.new('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',1000)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Artifacts Link'),


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

            + g.panel.table.withPluginVersion()

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
              + elasticsearch.withQuery("scale:240")
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

              g.panel.table.fieldOverride.byName.new('ci_date.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',227)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Date'),

              g.panel.table.fieldOverride.byName.new('kind.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',100)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Kind'),

              g.panel.table.fieldOverride.byName.new('scale')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',100)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Scale'),

              g.panel.table.fieldOverride.byName.new('vm_os_version.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',200)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','OS Version'),

              g.panel.table.fieldOverride.byName.new('run_artifacts_url.keyword')
              + g.panel.table.fieldOverride.byName.withProperty('custom.width',1000)
              + g.panel.table.fieldOverride.byName.withProperty('displayName','Artifacts Link'),

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

            + g.panel.table.withPluginVersion()

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

                elasticsearch.bucketAggs.Terms.withField('vm_os_version.keyword')
                + elasticsearch.bucketAggs.Terms.withId('11')
                + elasticsearch.bucketAggs.Terms.settings.withMinDocCount('1')
                + elasticsearch.bucketAggs.Terms.settings.withOrder('desc')
                + elasticsearch.bucketAggs.Terms.settings.withOrderBy('_term')
                + elasticsearch.bucketAggs.Terms.settings.withSize('10')
                + elasticsearch.bucketAggs.Terms.withType('terms'),

                elasticsearch.bucketAggs.DateHistogram.withField('run_artifacts_url.keyword')
                + elasticsearch.bucketAggs.DateHistogram.withId('12')
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
              + elasticsearch.withQuery("scale:(111 OR 120)")
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

          + g.panel.text.withPluginVersion()

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
