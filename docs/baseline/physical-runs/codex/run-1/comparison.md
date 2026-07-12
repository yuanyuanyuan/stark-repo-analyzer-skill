# Codex Physical Run Comparison

The physical invocation used the fixed HEAD `9e552e9d15ba52bed7077d5357f3e18e330f8f38` and `standard` mode. The source tree was clean before and after the run.

The physical report declared three bounded regions: core session/turn orchestration, App Server protocol, and JavaScript packaging, with 12,692/15,369 declared lines (82.6%). The committed reference snapshot used a broader but shallower decomposition and reported lower aggregate coverage. These denominators are not interchangeable; the physical report preserves the excluded TUI, sandbox, MCP, SDK, cloud, generated and test areas.

P2: pass. P4: not evaluated because this project received one physical invocation in this extension.
