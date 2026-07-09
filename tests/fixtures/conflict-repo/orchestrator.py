from module_a.processor import process as ingest
from module_b.processor import process as export


def run(item):
    ingested = ingest(item)
    exported = export(ingested)
    return exported
