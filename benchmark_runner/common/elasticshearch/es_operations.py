
import time
from typeguard import typechecked
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from datetime import datetime

from benchmark_runner.common.elasticshearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger


class ESOperations:
    """
    This class contains elastic search operations
    """

    def __init__(self, es_host: str, es_port: str, es_fetch_last_x_minutes: int = 15):
        self.__es_fetch_last_x_minutes = es_fetch_last_x_minutes  # MUST BE 15 MIN AT LEAST
        self.__es_host = es_host
        self.__es_port = es_port
        self.__es = Elasticsearch([{'host': self.__es_host, 'port': self.__es_port}])
        self._hits = 0

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

    def __es_get_index_hits(self, index: str, uuid: str = '', workload: str = '',
                            max_search_results: int = 1000):
        """
        This method search for data per index in last 2 minutes and return the number of docs or zero
        :param index:
        :param workload: need only if there is different timestamp parameter in Elasticsearch
        :param max_search_results:
        :return:
        """
        """
        :return:
        """
        # https://github.com/elastic/elasticsearch-dsl-py/issues/49
        self.__es.indices.refresh(index=index)
        # timestamp name in Elasticsearch is different
        if 'uperf' in workload:
            search = Search(using=self.__es, index=index).filter('range', uperf_ts={
                'gte': f'now-{self.__es_fetch_last_x_minutes}m', 'lt': 'now'})
        else:
            search = Search(using=self.__es, index=index).filter('range', timestamp={
                'gte': f'now-{self.__es_fetch_last_x_minutes}m', 'lt': 'now'})
        search = search[0:max_search_results]
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
                        count_hits += 1
                return count_hits
            else:
                return len(search_response.hits)
        else:
            return 0

    @typechecked()
    @logger_time_stamp
    def verify_es_data_uploaded(self, index: str, uuid: str = '', workload: str = '', timeout: int = 1800,
                                sleep_time: int = 30):
        """
        The method wait till data upload to elastic search and wait if there is new data, search in last 15 minutes
        :param uuid: the current workload uuid
        :param workload: workload name only if there is a different timestamp parameter name in elasticsearch
        :param index:
        :param timeout:
        :param sleep_time:
        :return:
        """
        current_wait_time = 0
        current_hits = self._hits
        # waiting for any hits
        while current_wait_time <= timeout:
            # waiting for new hits
            new_hits = self.__es_get_index_hits(index=index, uuid=uuid, workload=workload)
            if current_hits < new_hits:
                logger.info(f'Data with index: {index} and uuid={uuid} was uploaded to ElasticSearch successfully')
                return True

            # sleep for x seconds
            time.sleep(sleep_time)
            current_wait_time += sleep_time
        raise ElasticSearchDataNotUploaded

    def upload_to_es(self, data: dict, index: str, doc_type: str = '_doc', es_add_items: dict = None):
        """
        This method is upload json data into elasticsearch
        :param data: data must me in dictionary i.e. {'key': 'value'}
        :param index: index name to be stored in elasticsearch
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
