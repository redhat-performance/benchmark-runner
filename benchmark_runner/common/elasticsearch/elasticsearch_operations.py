
import time
import ssl

from typeguard import typechecked
from elasticsearch import Elasticsearch
from elasticsearch.connection import create_ssl_context
from elasticsearch_dsl import Search
from datetime import datetime, timezone

from benchmark_runner.common.elasticsearch.elasticsearch_exceptions import ElasticSearchDataNotUploaded
from benchmark_runner.common.logger.logger_time_stamp import logger_time_stamp, logger


class ElasticSearchOperations:
    """
    This class contains elasticsearch operations
    """

    # sleep time between checks is 10 sec
    SLEEP_TIME = 10
    # ElasticSearch fetch data of last 15 minutes
    ES_FETCH_MIN_TIME = 15
    # max search results
    MAX_SEARCH_RESULTS = 1000
    MIN_SEARCH_RESULTS = 100

    def __init__(self, es_host: str, es_port: str, es_user: str = '', es_password: str = '', es_url_protocol: str = 'http', timeout: int = 2000):
        self.__es_host = es_host
        self.__es_port = es_port
        self.__es_user = es_user
        self.__es_password = es_password
        self.__es_url_protocol = es_url_protocol
        self.__timeout = timeout

        kwargs = {}
        if self.__es_url_protocol == 'https':
            ssl_context = create_ssl_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            kwargs["ssl_context"] = ssl_context

        if self.__es_password:
            self.__es_url = f"{self.__es_url_protocol}://{self.__es_user}:{self.__es_password}@{self.__es_host}:{self.__es_port}"

            host_arg = self.__es_url
        else:
            host_arg = dict(host=self.__es_host)
            if self.__es_port:
                host_arg['port'] = self.__es_port

        self.__es = Elasticsearch([host_arg], **kwargs)

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
        self._hits = self.__elasticsearch_get_index_hits(index=index, uuid=uuid, workload=workload)

    def __elasticsearch_get_index_hits(self, index: str, uuid: str = '', fast_check: bool = False, id: bool = False, es_fetch_min_time:int = None):
        """
        This method searches for data per index in last 2 minutes and return the number of docs or zero
        :param index:
        :param es_fetch_min_time
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
        if es_fetch_min_time:
            search = Search(using=self.__es, index=index).filter('range', timestamp={
                'gte': f'now-{es_fetch_min_time}m', 'lt': 'now'})
        else:
            search = Search(using=self.__es, index=index).filter('range', timestamp={
                'gte': f'now-{self.ES_FETCH_MIN_TIME}m', 'lt': 'now'})
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
    def verify_elasticsearch_data_uploaded(self, index: str, uuid: str = '', workload: str = '',
                                           fast_check: bool = False, timeout: int = None, es_fetch_min_time: int = None):
        """
        The method waits till data uploads to elasticsearch and waits if there is new data, search in last 15 minutes
        :param es_fetch_min_time:
        :param index:
        :param uuid: the current workload uuid
        :param workload: workload name only if there is a different timestamp parameter name in elasticsearch
        :param timeout:
        :param fast_check: return response on first doc

        :return:
        """
        current_wait_time = 0
        current_hits = 0
        self.__timeout = timeout if timeout else self.__timeout
        # waiting for any hits
        while self.__timeout <= 0 or current_wait_time <= self.__timeout:
            # waiting for new hits
            new_hits = self.__elasticsearch_get_index_hits(index=index, uuid=uuid, fast_check=fast_check, es_fetch_min_time=es_fetch_min_time)
            if current_hits < new_hits:
                logger.info(f'Data with index: {index} and uuid={uuid} was uploaded to ElasticSearch successfully')
                return self.__elasticsearch_get_index_hits(index=index, uuid=uuid, id=True, fast_check=fast_check, es_fetch_min_time=es_fetch_min_time)
            # sleep for x seconds
            time.sleep(self.SLEEP_TIME)
            current_wait_time += self.SLEEP_TIME
        # not raise error in case of timeout parameter
        if timeout:
            return False
        else:
            raise ElasticSearchDataNotUploaded

    @typechecked()
    def upload_to_elasticsearch(self, index: str, data: dict, doc_type: str = '_doc', es_add_items: dict = None, **kwargs):
        """
        This method uploads json data into elasticsearch
        :param index: index name to be stored in elasticsearch
        :param data: data must be in dictionary i.e. {'key': 'value'}
        :param doc_type:
        :param es_add_items:
        :return:
        """
        if index and data:
            # Add items
            if es_add_items:
                data.update(es_add_items)

            # utcnow - solve timestamp issue
            data['timestamp'] = datetime.now(timezone.utc)  # datetime.utcnow() or datetime.now()

            # Uploads data to elasticsearch server
            try:
                if isinstance(data, dict):  # JSON Object
                    self.__es.index(index=index, doc_type=doc_type, document=data, **kwargs)
                else:  # JSON Array
                    for record in data:
                        self.__es.index(index=index, doc_type=doc_type, document=record, **kwargs)
                return True
            except Exception as err:
                raise err
        else:
            raise Exception('Empty parameters: index/ data')

    @typechecked()
    @logger_time_stamp
    def update_elasticsearch_index(self, index: str, id: str, metadata: dict = ''):
        """
        This method updates existing index with specific id
        :param index: index name
        :param id: The specific id
        :param metadata: The metadata for enrich that existing index according to id
        :return:
        """
        if index and id and metadata:
            self.__es.update(index=index, id=id, body={"doc": metadata})
        else:
            raise Exception('Empty parameters: index/ id/ metadata')

    @typechecked()
    @logger_time_stamp
    def get_elasticsearch_index_by_id(self, index: str, id: str):
        """
        This method returns elasticsearch index data by id
        :param index: index name
        :param id: The specific index id
        :return:
        """
        if index and id:
            return self.__es.get(index=index, id=id)
        else:
            raise Exception('Empty parameters: index/ id')

    @typechecked()
    @logger_time_stamp
    def delete_elasticsearch_index_by_id(self, index: str, id: str):
        """
        This method deletes elasticsearch index data by id
        :param index: index name
        :param id: The specific index id
        :return:
        """
        if index and id:
            return self.__es.delete(index=index, id=id)
        else:
            raise Exception('Empty parameters: index/ id')

    @typechecked()
    @logger_time_stamp
    def get_query_data_between_dates(self, start_datetime: datetime, end_datetime: datetime):
        """
        This method returns the query for fetching data between dates
        @param start_datetime:
        @param end_datetime:
        @return:
        """
        if start_datetime and end_datetime:
            if end_datetime < start_datetime:
                start_datetime = end_datetime
            query = {
                    "bool": {
                        "filter": {
                            "range": {
                                "timestamp": {
                                    "format": "yyyy-MM-dd HH:mm:ss"
                                }
                            }
                        }
                    }
            }
            query['bool']['filter']['range']['timestamp']['lte'] = str(end_datetime.replace(microsecond=0))
            query['bool']['filter']['range']['timestamp']['gte'] = str(start_datetime.replace(microsecond=0))
            return query
        else:
            raise Exception('Empty parameters: start_datetime/ end_datetime')

    @typechecked()
    @logger_time_stamp
    def get_index_data_between_dates(self, index: str, start_datetime: datetime = None, end_datetime: datetime = None):
        """
        This method returns list of index data between dates
        @param index:
        @param start_datetime:
        @param end_datetime:
        @return: list of ids
        """
        number_of_documents = 100
        scroll_duration = '1h'
        if index and start_datetime and end_datetime:
            es_data = []
            query = self.get_query_data_between_dates(start_datetime, end_datetime)
            response = self.__es.search(index=index, query=query, size=number_of_documents, scroll=scroll_duration)
            scroll_id = response.get('_scroll_id')
            if response.get('hits').get('hits'):
                es_data.extend(response.get('hits').get('hits'))
            while scroll_id:
                response = self.__es.scroll(scroll_id=scroll_id, scroll="1h")
                if len(response.get('hits').get('hits')) > 0:
                    es_data.extend(response.get('hits').get('hits'))
                else:
                    break
            return es_data
        else:
            raise Exception('Empty parameters: index/ start_datetime/ end_datetime')

    @typechecked()
    @logger_time_stamp
    def get_index_ids_between_dates(self, index: str, start_datetime: datetime = None, end_datetime: datetime = None):
        """
        This method returns list of index ids between dates
        @param index:
        @param start_datetime:
        @param end_datetime:
        @return: list of ids
        """
        es_data = self.get_index_data_between_dates(index=index, start_datetime=start_datetime, end_datetime=end_datetime)
        ids = [hit["_id"] for hit in es_data]
        return ids

    @typechecked()
    @logger_time_stamp
    def delete_index_ids_between_dates(self, index: str, start_datetime: datetime = None,
                                       end_datetime: datetime = None):
        """
        This method deletes index ids between dates
        @param index:
        @param start_datetime:
        @param end_datetime:
        @return:
        """
        if index and start_datetime and end_datetime:
            ids = self.get_index_ids_between_dates(index=index, start_datetime=start_datetime, end_datetime=end_datetime)
            for id in ids:
                self.delete_elasticsearch_index_by_id(index=index, id=id)
        else:
            raise Exception('Empty parameters: index/ start_datetime/ end_datetime')

    @logger_time_stamp
    def get_all_indexes(self):
        """
        This method returns sorted elasticsearch indexes
        @return:
        """
        indexes = []
        # Fetch all indices
        indices = self.__es.cat.indices(format="json")
        for index in indices:
            indexes.append(index['index'])
        return sorted(indexes)
