#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import sys

from airbyte_cdk.entrypoint import launch
from source_socrata_open_data import SourceSocrataOpenData

if __name__ == "__main__":
    source = SourceSocrataOpenData()
    launch(source, sys.argv[1:])
