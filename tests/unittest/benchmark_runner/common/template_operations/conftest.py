
import tempfile
from benchmark_runner.main.environment_variables import environment_variables

environment_variables.environment_variables_dict['run_artifacts_path'] = tempfile.mkdtemp()
