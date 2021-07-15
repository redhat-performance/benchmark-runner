
class BenchmarkOperatorError(Exception):
    """ Base class for all benchmark operator error classes.
        All exceptions raised by the benchmark runner library should inherit from this class. """
    pass


class VMWorkloadNeedElasticSearch(BenchmarkOperatorError):
    """This exception return elastic search not uploaded error"""
    def __init__(self):
        self.message = f'Vm workload need elastic search for verify completed status'
        super(VMWorkloadNeedElasticSearch, self).__init__(self.message)

