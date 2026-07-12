# HTTPX Physical Run Comparison

The physical invocation used the fixed HEAD `b5addb64f0161ff6bfe94c124ef76f6a1fba5254` and `standard` mode. The source tree was clean before and after the run.

Compared with the committed reference snapshot, the physical report uses a different narrative decomposition: client lifecycle, message/URL semantics, transports and supporting facilities. Its bounded coverage is 8,600/8,827 lines (97.43%), versus the committed report's 100% claim. This is a scope/report difference, not a source identity mismatch; both reports explicitly exclude runtime network and test behavior.

P2: pass. P4: not evaluated because this project received one physical invocation in this extension.
