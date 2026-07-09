def process(payload):
    """Export payload out of the pipeline.

    NOTE: 与 module_a.processor.process 同名，构成跨模块职责冲突。
    """
    return {"stage": "export", "module": "b", "payload": payload}
