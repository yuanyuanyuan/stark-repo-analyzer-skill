def process(payload):
    """Ingest payload into the pipeline.

    NOTE: 与 module_b.processor.process 同名，构成跨模块职责冲突。
    """
    return {"stage": "ingest", "module": "a", "payload": payload}
