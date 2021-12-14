
import time
from typeguard import typechecked
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from datetime import datetime

from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger
from benchmark_runner.main.environment_variables import environment_variables


class ESOperations:
    """
    This class contains elastic search operations
    """

    # sleep time between checks is 10 sec
    SLEEP_TIME = 10
    # ElasticSearch fetch data of last 15 minutes
    ES_FETCH_MIN_TIME = 15
    # max search results
    MAX_SEARCH_RESULTS = 1000
    MIN_SEARCH_RESULTS = 100

    def __init__(self, es_host: str, es_port: str, es_fetch_last_x_minutes: int = ES_FETCH_MIN_TIME):
        self.__es_fetch_last_x_minutes = es_fetch_last_x_minutes  # MUST BE 15 MIN AT LEAST
        self.__es_host = es_host
        self.__es_port = es_port
        if self.__es_port:
            self.__es = Elasticsearch([{'host': self.__es_host, 'port': self.__es_port}])
        else:
            self.__es = Elasticsearch([{'host': self.__es_host}])
        self._hits = 0
        self.__environment_variables_dict = environment_variables.environment_variables_dict
        self.__timeout = int(environment_variables.environment_variables_dict['timeout'])

    @property
    def hits(self):
        """This method is getter of hits"""
        return self._hits

    @hits.setter
    def hits(self, value):
        """This method is setter of hits"""
        try:
            index, uuid, workload = value
        except ValueError:
            raise ValueError("Pass an iterable with two items")
        self._hits = self.__es_get_index_hits(index=index, uuid=uuid, workload=workload)

    def __es_get_index_hits(self, index: str, uuid: str = '', workload: str = '', fast_check: bool = False, id: bool = False):
        """
        This method search for data per index in last 2 minutes and return the number of docs or zero
        :param index:
        :param workload: need only if there is different timestamp parameter in Elasticsearch
        :param id: True to return the doc ids
        :param fast_check: return fast response
        :return:
        """
        """
        :return:
        """
        ids = []
        # https://github.com/elastic/elasticsearch-dsl-py/issues/49
        self.__es.indices.refresh(index=index)
        # timestamp name in Elasticsearch is different
        if 'uperf' in workload:
            search = Search(using=self.__es, index=index).filter('range', uperf_ts={
                'gte': f'now-{self.__es_fetch_last_x_minutes}m', 'lt': 'now'})
        else:
            search = Search(using=self.__es, index=index).filter('range', timestamp={
                'gte': f'now-{self.__es_fetch_last_x_minutes}m', 'lt': 'now'})
        # reduce the search result
        if fast_check:
            search = search[0:self.MIN_SEARCH_RESULTS]
        else:
            search = search[0:self.MAX_SEARCH_RESULTS]
        search_response = search.execute()
        if search_response.hits:
            if uuid:
                count_hits = 0
                for row in search_response:
                    if type(row['uuid']) == str:
                        # uperf return str
                        current_uuid = row['uuid']
                    else:
                        current_uuid = row['uuid'][0]
                    if current_uuid == uuid:
                        if fast_check:
                            return 1
                        ids.append(row.meta.id)
                        count_hits += 1
                if id:
                    return ids
                else:
                    return count_hits
            else:
                return len(search_response.hits)
        else:
            return 0

    @typechecked()
    @logger_time_stamp
    def verify_es_data_uploaded(self, index: str, uuid: str = '', workload: str = '', fast_check: bool = False):
        """
        The method wait till data upload to elastic search and wait if there is new data, search in last 15 minutes
        :param index:
        :param uuid: the current workload uuid
        :param workload: workload name only if there is a different timestamp parameter name in elasticsearch
        :param fast_check: return response on first doc

        :return:
        """
        current_wait_time = 0
        current_hits = 0
        # waiting for any hits
        while current_wait_time <= self.__timeout:
            # waiting for new hits
            new_hits = self.__es_get_index_hits(index=index, uuid=uuid, workload=workload, fast_check=fast_check)
            if current_hits < new_hits:
                logger.info(f'Data with index: {index} and uuid={uuid} was uploaded to ElasticSearch successfully')
                return self.__es_get_index_hits(index=index, uuid=uuid, workload=workload, id=True, fast_check=fast_check)
            # sleep for x seconds
            time.sleep(self.SLEEP_TIME)
            current_wait_time += self.SLEEP_TIME
        raise ElasticSearchDataNotUploaded

    @typechecked()
    @logger_time_stamp
    def upload_to_es(self, index: str, data: dict, doc_type: str = '_doc', es_add_items: dict = None):
        """
        This method is upload json data into elasticsearch
        :param index: index name to be stored in elasticsearch
        :param data: data must me in dictionary i.e. {'key': 'value'}
        :param doc_type:
        :param es_add_items:
        :return:
        """
        # read json to dict
        json_path = ""

        # Add items
        if es_add_items:
            for key, value in es_add_items.items():
                data[key] = value

        # utcnow - solve timestamp issue
        data['timestamp'] = datetime.utcnow()  # datetime.now()

        # Upload data to elastic search server
        try:
            if isinstance(data, dict):  # JSON Object
                self.__es.index(index=index, doc_type=doc_type, body=data)
            else:  # JSON Array
                for record in data:
                    self.__es.index(index=index, doc_type=doc_type, body=record)
            return True
        except Exception as err:
            raise err

    @typechecked()
    @logger_time_stamp
    def update_es_index(self, index: str, id: str, metadata: dict = ''):
        """
        This method update existing index
        :param index: index name
        :param id: The specific index id
        :param metadata: The metadata for enrich that existing index according to id
        :return:
        """
        self.__es.update(index=index, id=id, body={"doc": metadata})

    @typechecked()
    @logger_time_stamp
    def get_es_index_by_id(self, index: str, id: str):
        """
        This method return elastic search index data by id
        :param index: index name
        :param id: The specific index id
        :param doc_type:
        :param metadata: The metadata for enrich that existing index according to id
        :return:
        """
        return self.__es.get(index=index, id=id)
