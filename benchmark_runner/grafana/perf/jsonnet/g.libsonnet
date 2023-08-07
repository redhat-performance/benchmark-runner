// Cannot import 'g.libsonnet' inside 'main.libsonnet' as it causes a Terraform error. The 'g.libsonnet' file must be in a separate file. For more details, please refer to: https://github.com/grafana/grafonnet/tree/main/examples/terraform
import 'github.com/grafana/grafonnet/gen/grafonnet-latest/main.libsonnet'
