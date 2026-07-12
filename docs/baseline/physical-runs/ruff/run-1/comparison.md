# Ruff Physical Run Comparison

The physical invocation used the fixed HEAD `c588a3f7f57461692652d339936222b4496c5953` and `standard` mode. The source tree was clean before and after the run.

The physical report deliberately bounded the deep read to CLI/configuration, lint/fix, and formatter paths: 15,258/21,703 declared lines (70.3%). The committed reference snapshot has a different bounded decomposition and calls out parser, semantic, LSP and `ty` gaps. The physical run preserves the same limitation boundary and additionally records that `cargo` and `rustc` were unavailable, so build, tests and Clippy were not performed.

P2: pass. P4: not evaluated because this project received one physical invocation in this extension.
