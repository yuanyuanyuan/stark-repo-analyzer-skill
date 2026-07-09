# conflict-repo

A minimal synthetic repository used to exercise **real cross-module conflict
detection and repair** (T13).

The conflict: both `module_a/processor.py` and `module_b/processor.py` define a
public top-level function with the **same name** `process()`. `orchestrator.py`
imports both under aliases, but a reader / reviewer cannot tell which
`process` owns a given responsibility — this is a genuine cross-module
conflict that the independent cross-ref review is expected to flag and the
repair agent is expected to disambiguate.
