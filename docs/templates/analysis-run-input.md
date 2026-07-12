# Analysis Run Input

```yaml
run_id: <stable human-readable id>
input:
  kind: local-path | public-url | owner-repo
  value: <path or public identifier>
analysis_mode: standard
graphify:
  extraction_mode: deep
  backend: auto-detect
  output: <WORK_DIR>/graphify-out
workspace: <WORK_DIR>
```

Before the run starts, resolve `input` to a read-only repository and record:

- absolute source path and source commit;
- whether the source was cloned or supplied locally;
- Graphify version, detected backend and model name (never credentials);
- tool versions and timestamps;
- external research URLs or the explicit offline reason;
- selected modules, coverage targets and bounded-scope limitations.

The input file is the fixed context for a repeatability comparison. Temporary paths, timestamps and run IDs are normalized out of the comparison; source commit, mode, source references, coverage and failure classification are not.
