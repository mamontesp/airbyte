import requests
from abc import ABC
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.auth import NoAuth
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple


# Basic full refresh stream
class SocrataOpenDataStream(HttpStream, ABC):
    url_base = None
    DEFAULT_LIMIT = 3
    DEFAULT_OFFSET = 0

    def __init__(self, domain, limit: int = DEFAULT_LIMIT, offset: int = DEFAULT_OFFSET, **kwargs):
        self.domain = domain
        self.limit = limit or self.DEFAULT_LIMIT
        self.offset = offset or self.DEFAULT_OFFSET
        super().__init__(**kwargs)

    def next_page_token(self) -> Optional[Mapping[str, Any]]:
        self.offset = self.limit + self.offset
        paging_dictionary = {"$offset": self.offset}

        print(f'offset {self.offset}')
        return paging_dictionary
        
        #return None

    def request_params(self, stream_state=None, next_page_token: Mapping[str, Any] = None, **kwargs):
        
        stream_state = stream_state or {}
        params={"$offset": self.offset,
                "$limit": self.limit}
        print(f'next_page_token {next_page_token}')
        if next_page_token:
            params.update(next_page_token)
        
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        response_json = response.json()
        yield from response_json

    def read_records(
        self,
        sync_mode: SyncMode = SyncMode.full_refresh,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        
        #if stream_slice is None:
        #    return []

        try:
            path = self.path()
            response = requests.get(f'{self.domain}/{path}.json', params = {"$select": "count(*)"})
            record_count = response.json()[0]['count']
            for i in range(0, 12, self.limit):
                params = self.request_params(next_page_token = self.next_page_token())
                full_path = f'{self.domain}/{path}.json'
                
                response = requests.get(f'{self.domain}/{path}.json', params = params)
                
                if response.status_code == 200:
                    self.logger.info(f'Status code {response.status_code}')
                yield from response.json()

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            parsed_error = e.response.json()
            error_code = parsed_error.get("error", {}).get("code")
            error_message = parsed_error.get("message")
            # if the API Key doesn't have required permissions to particular stream, this stream will be skipped
            if status_code == 403:
                self.logger.warn(f"Stream {self.name} is skipped, due to {error_code}. Full message: {error_message}")
                pass
            else:
                self.logger.error(f"Syncing stream {self.name} is failed, due to {error_code}. Full message: {error_message}")

class DatosGovCoStream(SocrataOpenDataStream):
    def __init__(self):
        domain = "https://www.datos.gov.co/resource"
        super().__init__(domain)

class DatosGovCoProvidersGroupSecop(DatosGovCoStream):
    """
    TODO: Change class name to match the table/data source this stream corresponds to.
    """

    # TODO: Fill in the primary key. Required. This is usually a unique field in the stream, like an ID or a timestamp.

    primary_key = None

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        """
        code path in www.datos.gov.co for providers group dataset
        """
        return "ceth-n4bn"

