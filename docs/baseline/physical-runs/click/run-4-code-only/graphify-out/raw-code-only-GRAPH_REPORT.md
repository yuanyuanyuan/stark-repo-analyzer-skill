# Graph Report - /private/tmp/stark-click-code-only-pilot  (2026-07-13)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1910 nodes · 3916 edges · 170 communities (97 shown, 73 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 883 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 103
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 124
- Community 125
- Community 126
- Community 127
- Community 128
- Community 129
- Community 130
- Community 131
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136
- Community 137
- Community 138
- Community 139
- Community 140
- Community 141
- Community 142
- Community 143
- Community 144
- Community 145
- Community 146
- Community 147
- Community 148
- Community 149
- Community 150
- Community 151
- Community 152
- Community 153
- Community 154
- Community 155
- Community 156
- Community 157

## God Nodes (most connected - your core abstractions)
1. `cli()` - 205 edges
2. `Context` - 195 edges
3. `Parameter` - 116 edges
4. `Command` - 114 edges
5. `CliRunner` - 74 edges
6. `Option` - 64 edges
7. `BadParameter` - 60 edges
8. `CompletionItem` - 60 edges
9. `Group` - 57 edges
10. `Argument` - 50 edges

## Surprising Connections (you probably didn't know these)
- `list_users()` --calls--> `CompletionItem`  [INFERRED]
  /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/examples/completion/completion.py → /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/shell_completion.py
- `test_term_len()` --calls--> `term_len()`  [INFERRED]
  /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/tests/test_compat.py → /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/_compat.py
- `test_flag_auto_detection()` --calls--> `Option`  [INFERRED]
  /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/tests/test_options.py → /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/core.py
- `test_file_error_surrogates()` --calls--> `FileError`  [INFERRED]
  /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/tests/test_types.py → /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/exceptions.py
- `test_completion_item_data()` --calls--> `CompletionItem`  [INFERRED]
  /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/tests/test_shell_completion.py → /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/shell_completion.py

## Import Cycles
- 3-file cycle: `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/__init__.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/core.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/termui.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/__init__.py`
- 3-file cycle: `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/core.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/termui.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/types.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/core.py`
- 4-file cycle: `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/__init__.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/decorators.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/core.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/termui.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/__init__.py`
- 4-file cycle: `/Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/__init__.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/types.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/core.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/termui.py -> /Users/chuzu/projests/stark-repo-analyzer-reference-sources/click/src/click/__init__.py`

## Communities (170 total, 73 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.03
Nodes (23): Color, ColorInt, EngineType, HashType, Letter, Number, test_aliases_for_flags(), test_bool_flag_group_competition_with_default_map() (+15 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (60): A Group can be built with a dict of commands., A Group can be built with a list of commands., Check how default is processed when options compete for the same variable name., User parameters never clash with the automatic help option, which     stores its, Optional Choice arguments reuse the type's brackets instead of doubling.      Wi, ``DateTime`` arguments behave the same way as ``Choice``., Claiming the reserved storage name of the automatic help option     triggers a w, When ``package_name`` (detected or passed) is an import name that     differs fr (+52 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (56): FixtureRequest, CliRunner, PathLike, The CLI runner provides functionality to invoke a Click command line     script, A context manager that creates a temporary directory and         changes the cur, runner(), Test that invoke `catch_exceptions` takes the value from CliRunner if not set, Writing to stderr should escape invalid characters instead of     raising a Unic (+48 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (31): CoreArgument, CoreOption, CoreParameter, T_FLAG_NEEDS_VALUE, T_UNSET, BadArgumentUsage, BadOptionUsage, NoSuchOption (+23 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (31): copy(), Copies one or multiple files to a new location.  This copies all     files from, Test how a required argument is processing the provided values., An argument is bracketed in the usage line only when it is optional., An argument with empty or missing help text must not gain a stray leading     sp, Comprehensive check of default-value processing for arguments with     ``nargs``, Some defaults are not valid when nargs is set., Test that overriding type_cast_value is supported      In particular, the argume (+23 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (39): Tests for ``CliRunner`` stream lifecycle and ownership.  Covers the stream manag, After the isolation context exits, stream values are readable., Basic ``logging.warning()`` inside a command must not crash., Logging + prompt (the exact #824 reproducer)., Multiple sequential ``invoke()`` calls with logging (#3110 reproducer).      Iss, A ``StreamHandler`` explicitly attached to stderr must survive ``invoke()``., Simulate what ``--log-cli-level`` does: add a handler to root     before invoke., Basic ``ThreadPoolExecutor`` usage inside a command. (+31 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (17): Context, The context is a special internal object that holds state relevant     for the s, Get the default for the parameter. Tries         :meth:`Context.lookup_default`, Returns the value found in the environment variable(s) attached to this, Process the raw environment variable string for this parameter.          Returns, Get a stringified version of the param for use in error messages to         indi, :class:`Option` resolves its environment variable the same way as         :func:, Finds the outermost context. (+9 more)

### Community 7 - "Community 7"
Cohesion: 0.14
Nodes (27): BadParameter, An exception that formats out a standardized error message for a     bad paramet, CompletionItem, Represents a completion value and metadata about the value. The     default meta, ChoiceInfoDict, CompositeParamType, DateTimeInfoDict, FileInfoDict (+19 more)

### Community 8 - "Community 8"
Cohesion: 0.14
Nodes (29): Exception, type, _BaseCommand, CommandCollection, _FakeSubclassCheck, __getattr__(), _MultiCommand, ParameterSource (+21 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (15): _format_deprecated_label(), Any, Return the parenthesized deprecation label shown in help text., This function when given an info name and arguments will kick         off the pa, Gather information that could be useful for a tool generating         user-facin, Convert and validate a value against the parameter's         :attr:`type`, :attr, A value is considered missing if:          - it is :attr:`UNSET`,         - or i, Process the value of this parameter:          1. Type cast the value using :meth (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (36): _Marker, test flag with default map, The first ``default=True`` wins when multiple ``flag_value`` options share     a, ``lookup_default()`` should return ``None`` for missing keys, not :attr:`UNSET`., A callable in ``default_map`` is invoked with ``call=True``     (the default) an, Smoke test: a single option's default is type-coerced.      This covers basic si, ``get_parameter_source()`` reports the correct origin for a parameter     value, ``get_parameter_source()`` is available during ``ParamType.convert``.      Uses (+28 more)

### Community 11 - "Community 11"
Cohesion: 0.07
Nodes (24): _create_progress(), item_show_func should show the current item being yielded., ``PAGER`` pointing to a nonexistent binary falls back to the text stdout., Exceptions should still flush the yielded stream in ``finally``., test_confirmation_prompt(), test_file_prompt_default_format(), test_get_pager_file_flushes_stream_on_exception(), test_get_pager_file_pager_missing_binary_falls_back() (+16 more)

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (30): Option, Options are usually optional values on the command line and     have some extra, Choice, The choice type allows a value to be checked against a fixed set     of supporte, _get_completions(), _get_words(), test_absolute_path(), test_argument_default() (+22 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (18): Array, Buffer, c_char, Structure, ConsoleStream, get_buffer(), _get_text_stderr(), _get_text_stdin() (+10 more)

### Community 14 - "Community 14"
Cohesion: 0.08
Nodes (29): blur_cmd(), cli(), copy_filename(), crop_cmd(), display_cmd(), emboss_cmd(), generator(), open_cmd() (+21 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (20): F, Command, Group, Gets short help for the command or makes it by shortening the         long help, Return a list of completions for the incomplete value. Looks         at the name, A group is a command that nests other commands (or more groups).      :param nam, Registers another :class:`Command` with this group.  If the name         is not, A shortcut decorator for declaring and attaching a command to         the group. (+12 more)

### Community 16 - "Community 16"
Cohesion: 0.18
Nodes (30): _find_binary_reader(), _find_binary_writer(), _force_correct_text_reader(), _force_correct_text_stream(), _force_correct_text_writer(), get_binary_stderr(), get_binary_stdin(), get_binary_stdout() (+22 more)

### Community 17 - "Community 17"
Cohesion: 0.08
Nodes (18): BashComplete, get_completion_class(), Any, _ValueT_co, Base class for providing shell completion support. A subclass for     a given sh, The name of the shell function defined by the completion         script., Perform shell completion for the given CLI program.      :param cli: Command bei, Vars for formatting :attr:`source_template`.          By default this provides ` (+10 more)

### Community 18 - "Community 18"
Cohesion: 0.10
Nodes (28): _build_prompt(), confirm(), edit(), _format_default(), open_url(), _interpret_color(), launch(), _mask_hidden_input() (+20 more)

### Community 19 - "Community 19"
Cohesion: 0.07
Nodes (17): The leading subcommand token is bracketed only when it is optional., Cover the edge-case in which the eagerness of help option was not     respected,, A command with empty or missing help text must render the deprecation     label, test_abort_exceptions_with_disabled_standalone_mode(), test_auto_shorthelp(), test_custom_parser(), test_default_maps(), test_deprecated_empty_help_no_leading_space() (+9 more)

### Community 20 - "Community 20"
Cohesion: 0.14
Nodes (25): TypeGuard, get_best_encoding(), isatty(), Returns the default stream encoding if not found., _BufferedTextPagerStream, get_pager_file(), getchar(), _has_binary_buffer() (+17 more)

### Community 21 - "Community 21"
Cohesion: 0.16
Nodes (25): _AnyCallable, CmdType, FC, GrpType, argument(), command(), confirmation_option(), custom_version_option() (+17 more)

### Community 22 - "Community 22"
Cohesion: 0.08
Nodes (18): Editor, Open files in the user's editor., _ApostropheReprType, _CustomTypeNoValue, _CustomTypeWithRawValue, _MixedQuotedAndRawType, Custom type that mentions the user input both quoted (built-in     pattern) and, Custom type whose error message never references the value. (+10 more)

### Community 23 - "Community 23"
Cohesion: 0.10
Nodes (16): TypeIs, File, _is_file_like(), Path, IO, PathLike, The ``Path`` type is similar to the :class:`File` type, but     returns the file, Return a special completion marker that tells the completion         system to u (+8 more)

### Community 24 - "Community 24"
Cohesion: 0.14
Nodes (7): ProgressBar, BaseException, TracebackType, V, Update the progress bar by advancing a specified number of         steps, and op, Return a generator which yields the items added to the bar         during constr, test_progressbar_length_hint()

### Community 25 - "Community 25"
Cohesion: 0.08
Nodes (20): Fix: https://github.com/pallets/click/issues/3136, Checks all callbacks are called on exit, even the nasty ones hidden within     c, Test to check that make_pass_decorator doesn't consume arguments based on     in, A context's ``show_default`` setting defaults to the value from     the parent c, test_close_before_exit(), test_close_before_pop(), test_context_meta(), test_context_pushing() (+12 more)

### Community 26 - "Community 26"
Cohesion: 0.10
Nodes (22): strip_ansi(), Every complete CSI sequence is stripped, alone or wrapped in text., Everything the legacy pattern stripped, the CSI grammar still strips., The match ends at the first final byte., Text that merely resembles an escape sequence is never stripped., An unterminated sequence (missing its final byte) is left untouched., ``_ansi_re`` matches a complete sequence end to end as one token., test_ansi_re_matches_whole_sequence() (+14 more)

### Community 27 - "Community 27"
Cohesion: 0.08
Nodes (16): :author: @r-m-n     Including attribution to #612, The error hint should only show non-shadowed help option names,     picking the, ``HelpFormatter.write_usage`` renders a single usage line whose     trailing sep, End-to-end: a command with no parameters and an empty or absent     ``options_me, test_basic_functionality(), test_command_write_usage_no_args(), test_formatting_empty_help_lines(), test_formatting_usage_error_help_hint() (+8 more)

### Community 28 - "Community 28"
Cohesion: 0.11
Nodes (13): get_app_dir(), KeepOpenFile, make_default_short_help(), open_file(), _posixify(), Any, AnyStr, IO (+5 more)

### Community 29 - "Community 29"
Cohesion: 0.11
Nodes (11): ABC, Parameter, r"""A parameter to a command comes in two versions: they are either     :class:`, Returns the human readable name of this parameter.  This is the         same as, ParamType, Returns the metavar default for this param if it provides one., Optionally might return extra information about a missing         parameter., Convert the value to the correct type. This is not called if         the value i (+3 more)

### Community 30 - "Community 30"
Cohesion: 0.10
Nodes (12): alias(), AliasedGroup, cli(), commit(), Config, Commits pending changes., Adds an alias to the specified configuration file., This subclass of a group supports looking up aliases in a config     file and wi (+4 more)

### Community 31 - "Community 31"
Cohesion: 0.12
Nodes (10): _get_argv_encoding(), convert_type(), DateTime, _guess_type(), Any, The default behavior of Click is to apply a type on a value directly.     This w, Infer a type from *ty* or *default*.      Returns *ty* unchanged when it is not, Find the most appropriate :class:`ParamType` for the given Python     type. If t (+2 more)

### Community 32 - "Community 32"
Cohesion: 0.13
Nodes (8): Argument, Returns all the pieces that go into the usage line and returns         it as a l, Creates the underlying option parser for this command., Writes all the options into the formatter if they exist., Writes the arguments that have a help record into the formatter., Arguments are positional parameters to a command.  They generally     provide fe, The computed command path.  This is used for the ``usage``         information o, test_option_custom()

### Community 33 - "Community 33"
Cohesion: 0.10
Nodes (14): augment_usage_errors(), batch(), _check_iter(), AbstractContextManager, V, Context manager that attaches extra information to exceptions., Check if the value is iterable but not a string. Raises a type     error, or ret, Returns the parameter value produced by the parser.          If the parser did n (+6 more)

### Community 34 - "Community 34"
Cohesion: 0.11
Nodes (17): clear(), cli(), colordemo(), edit(), locate(), open(), pause(), progress() (+9 more)

### Community 35 - "Community 35"
Cohesion: 0.14
Nodes (16): _ShellCompleteT, add_completion_class(), _is_incomplete_argument(), _is_incomplete_option(), Determine the context and last complete command or parameter         from the co, Register a :class:`ShellComplete` subclass under the given name.     The name wi, Determine if the given parameter is an argument that can still     accept values, Check if the value looks like the start of an option. (+8 more)

### Community 36 - "Community 36"
Cohesion: 0.11
Nodes (5): Detecting the ``-`` dash sentinel must not compare ``bytes`` against     ``str``, Ensures that the error handling in ``click.File`` is robust.      ``EILSEQ`` sho, test_file_error_surrogates(), test_file_surrogates(), test_path_dash_no_byteswarning()

### Community 37 - "Community 37"
Cohesion: 0.18
Nodes (12): BytesIO, make_input_stream(), _pause_echo(), Any, IO, Mixes `<stdout>` and `<stderr>` streams.      The result is available in the ``o, Returns the environment overrides for invoking a script., A context manager that sets up the isolation for invoking of a         command l (+4 more)

### Community 38 - "Community 38"
Cohesion: 0.17
Nodes (6): _FixupStream, _is_jupyter_kernel_output(), _NonClosingTextIOWrapper, Any, The new io interface needs more from streams than streams     traditionally impl, should_strip_ansi()

### Community 39 - "Community 39"
Cohesion: 0.14
Nodes (8): Writes a unicode string into the internal buffer., Increases the indentation., Decreases the indentation., Writes a heading into the buffer., Writes a paragraph into the buffer., Writes re-indented text into the buffer.  This rewraps and         preserves par, Helpful context manager that writes a paragraph, a heading,         and the inde, A context manager that increases the indentation.

### Community 40 - "Community 40"
Cohesion: 0.13
Nodes (10): ModuleType, This is the way to invoke a script with all the bells and         whistles as a, Check if the shell is asking for tab completion, process         that, then exit, Alias for :meth:`main`., Return a list of completions for the incomplete value. Looks         at the name, Return a list of completions for the incomplete value. If a         ``shell_comp, _detect_program_name(), _expand_args() (+2 more)

### Community 41 - "Community 41"
Cohesion: 0.16
Nodes (11): cli(), clone(), commit(), delete(), Sets the user credentials.      This will override the current user config., Commits outstanding changes.      Commit changes to the given files into the rep, Repo is a command line tool that showcases how to build complex     command line, Clones a repository.      This will clone the repository at SRC into the folder (+3 more)

### Community 42 - "Community 42"
Cohesion: 0.17
Nodes (7): Writes the usage line into the formatter.          This is a low-level method ca, Writes the help into the formatter if it exists.          This is a low-level me, Writes the help text to the formatter if it exists., Writes the epilog into the formatter if it exists., HelpFormatter, This class helps with formatting text-based help pages.  It's     usually just n, Returns the buffer contents.

### Community 43 - "Community 43"
Cohesion: 0.14
Nodes (9): ExceptionInfo, BaseException, Holds the captured result of an invoked CLI script.      :param runner: The runn, The terminal output as unicode string, as the user would see it.          .. ver, The standard output as unicode string., The standard error as unicode string.          .. versionchanged:: 8.2, Result, test_file_lazy_mode() (+1 more)

### Community 44 - "Community 44"
Cohesion: 0.14
Nodes (10): cli(), mine_remove(), mine_set(), Moves SHIP to the new location X,Y., Makes SHIP fire to X,Y., Sets a mine at a specific coordinate., Naval Fate.      This is the docopt example adopted to Click but with some actua, Removes a mine at a specific coordinate. (+2 more)

### Community 45 - "Community 45"
Cohesion: 0.22
Nodes (13): T, make_pass_decorator(), pass_context(), pass_meta_key(), pass_obj(), P, R, Create a decorator that passes a key from     :attr:`click.Context.meta` as the (+5 more)

### Community 46 - "Community 46"
Cohesion: 0.18
Nodes (6): _FDCapture, The buffer this object contains belongs to some other object,         so prevent, Return the file descriptor of the saved original stream when         ``CliRunner, Given a command object it will return the default program name         for it., Invokes a command in an isolated environment.  The arguments are         forward, Redirect a file descriptor to a temporary file for capture.      Saves the curre

### Community 47 - "Community 47"
Cohesion: 0.15
Nodes (11): _NamedTextIOWrapper, A :class:`~io.TextIOWrapper` with custom ``name`` and ``mode``     that does not, After wrappers are garbage-collected, mixer buffers remain open., Calling ``close()`` on the wrapper must leave the buffer open., Garbage-collecting the wrapper must leave the buffer open., Multiple wrappers on the same buffer can be closed independently., test_mixer_buffers_survive_wrapper_gc(), test_multiple_wrappers_same_buffer() (+3 more)

### Community 48 - "Community 48"
Cohesion: 0.15
Nodes (12): A group with ``group_class = type`` should create subgroups of     the same type, A command invoked from a custom context should have a new     context with the s, A context with a custom ``formatter_class`` should format help     using that ty, A command with a custom ``context_class`` should produce a     context using tha, A group with a custom ``command_class`` should create subcommands     of that ty, A group with a custom ``group_class`` should create subgroups     of that type b, test_command_context_class(), test_context_formatter_class() (+4 more)

### Community 49 - "Community 49"
Cohesion: 0.18
Nodes (9): RuntimeError, Self, _check_nested_chain(), get_current_context(), push_context(), Returns the current click context.  This can be used as a way to     access the, Pushes a new context to the current stack., Internal helper to get the default value of the color flag.  If a     value is p (+1 more)

### Community 50 - "Community 50"
Cohesion: 0.18
Nodes (6): cli(), ComplexCLI, Environment, Logs a message to stderr., Logs a message to stderr only if verbose is enabled., A complex command line interface.

### Community 51 - "Community 51"
Cohesion: 0.26
Nodes (9): term_len(), iter_rows(), join_options(), measure_table(), Writes a usage line into the buffer.          :param prog: the program name., Writes a definition list into the buffer.  This is how options         and comma, Given a list of option strings this joins them in the most appropriate     way a, A helper function that intelligently wraps text.  By default, it     assumes tha (+1 more)

### Community 52 - "Community 52"
Cohesion: 0.20
Nodes (11): echo_via_pager(), get_pager_file(), progressbar(), TextIO, V, Context manager.      Yields a writable file-like object which can be used as an, This function takes a text and shows it via an environment specific     pager on, This function creates an iterable context manager that can be used     to iterat (+3 more)

### Community 53 - "Community 53"
Cohesion: 0.25
Nodes (5): _FloatValueT, _FloatValueT_co, _NumberRangeBase, Find the valid value to clamp to bound in the given         direction., Describe the range for use in help text.

### Community 54 - "Community 54"
Cohesion: 0.18
Nodes (11): click, click-example-aliases, click-example-colors, click-example-completion, click-example-complex, click-example-imagepipe, click-example-inout, click-example-naval (+3 more)

### Community 55 - "Community 55"
Cohesion: 0.18
Nodes (6): iter_params_for_processing(), NoReturn, Returns all declared parameters in the order they should be processed.      The, Aborts the execution of the program with a specific error         message., make_str(), Converts a value into a valid string.

### Community 56 - "Community 56"
Cohesion: 0.22
Nodes (5): _complete_visible_commands(), Extra format methods for multi methods that adds all the commands         after, This helper method can be used with the context object to promote         it to, List all the subcommands of a group that start with the     incomplete value and, Create a new context of the same type as this context, but         for a new com

### Community 57 - "Community 57"
Cohesion: 0.29
Nodes (6): Any, IO, clear(), Clears the terminal screen.  This will have the effect of clearing     the whole, echo(), Print a message and newline to stdout or a file. This should be     used instead

### Community 58 - "Community 58"
Cohesion: 0.22
Nodes (6): Return the longest prefix of ``text`` containing at most ``n`` visible     chara, ``textwrap.TextWrapper`` variant that measures widths by visible     character c, Wrap chunks counting widths in visible characters.          Mirrors the algorith, TextWrapper, _truncate_visible(), test_truncate_visible()

### Community 59 - "Community 59"
Cohesion: 0.29
Nodes (3): FuncParamType, _ValueT_co, _ValueT_contra

### Community 60 - "Community 60"
Cohesion: 0.22
Nodes (6): A generator that yields then raises: click writes the partial output to     the, Repeated exceptions during ``echo_via_pager`` must not leak subprocesses.      R, test_echo_via_pager_yields_before_exception(), _test_gen_func_fails(), _test_gen_func_yields_then_fails(), test_stress_echo_via_pager_exception_cleanup()

### Community 61 - "Community 61"
Cohesion: 0.20
Nodes (10): pager(), Demonstrates using the pager., _get_real_pager_command(), Return a real pager binary path used to exercise the pipe pager branch.      ..w, Run through the pipe pager backend selected by ``PAGER``., A real pager should exercise the BinaryIO branch., ``echo_via_pager`` should honor ``color`` like ``get_pager_file``., _run_get_pager_file_with_real_pager() (+2 more)

### Community 62 - "Community 62"
Cohesion: 0.20
Nodes (5): Formats the usage line into a string and returns it.          Calls :meth:`forma, Formats the help into a string and returns it.          Calls :meth:`format_help, Creates the :class:`~click.HelpFormatter` for the help and         usage output., Helper method to get formatted usage string for the current         context and, Helper method to get formatted help page for the current         context and com

### Community 63 - "Community 63"
Cohesion: 0.27
Nodes (7): BaseException, TracebackType, Invoke all close callbacks registered with         :meth:`call_on_close`, and ex, Unwind the exit stack by calling its :meth:`__exit__` providing the exception, Exits the application with a given exit code.          .. versionchanged:: 8.2, pop_context(), Removes the top level from the stack.

### Community 64 - "Community 64"
Cohesion: 0.22
Nodes (5): BoolParamType, NoReturn, Helper method to fail with an invalid value message., Convert a string to a boolean value.          If the value is already a boolean,, UUID

### Community 65 - "Community 65"
Cohesion: 0.22
Nodes (5): BaseException, PathLike, TracebackType, Closes the underlying file, no matter what., This function only closes the file if it was opened by the lazy         file wra

### Community 66 - "Community 66"
Cohesion: 0.22
Nodes (7): ReadableBuffer, BytesIOCopy, Patch ``io.BytesIO`` to let the written stream be copied to another.      .. ver, ``BytesIOCopy`` writes to itself and to ``copy_to``., ``BytesIOCopy.flush()`` also flushes ``copy_to``., test_bytesiocopy_flush_propagates(), test_bytesiocopy_writes_to_both()

### Community 67 - "Community 67"
Cohesion: 0.25
Nodes (3): _AtomicFile, BaseException, TracebackType

### Community 68 - "Community 68"
Cohesion: 0.25
Nodes (6): FishComplete, Produce the completion data to send back to the shell.          By default this, Shell completion for Fish., .. versionchanged:: 8.4.2             Escape newlines and replace tabs with spac, test_context_settings(), test_fish_format_completion_escapes_help()

### Community 70 - "Community 70"
Cohesion: 0.22
Nodes (4): test_open_file(), test_open_file_atomic_permissions_existing_file(), test_open_file_atomic_permissions_new_file(), test_open_file_ignore_errors_stdin()

### Community 72 - "Community 72"
Cohesion: 0.25
Nodes (5): _format_deprecated_suffix(), Return the trailing reason for a ``DeprecationWarning`` message,     prefixed wi, Given a context, this invokes the attached callback (if it exists)         in th, Process the value produced by the parser from user input.          Always proces, Set the source of a parameter. This indicates the location         from which th

### Community 74 - "Community 74"
Cohesion: 0.25
Nodes (3): test_aliased_command_canonical_name(), AliasedGroup, Example from https://click.palletsprojects.com/en/stable/advanced/#command-alias

### Community 76 - "Community 76"
Cohesion: 0.25
Nodes (8): Class1, Class2, A ``default_map`` entry should override the auto-aligned callable ``flag_value``, Help text with ``show_default=True`` should display the class name, not     inst, Non-basic flag_value types are passed through unchanged without     requiring ``, test_callable_flag_value_default_map(), test_callable_flag_value_show_default(), test_flag_value_not_stringified_for_custom_types()

### Community 77 - "Community 77"
Cohesion: 0.29
Nodes (4): ParseResult, cli(), Validation.      This example validates parameters in different ways.  It does i, URL

### Community 78 - "Community 78"
Cohesion: 0.29
Nodes (3): echo should not fail when stdout and stderr are None with pythonw on Windows., test_echo(), test_echo_no_streams()

### Community 79 - "Community 79"
Cohesion: 0.29
Nodes (4): On non-Windows, prompt and confirm pass the full prompt text to the     underlyi, If too few lines of input are given, prompt should exit, not hang., test_full_prompt_passed_to_readline(), test_prompts_eof()

### Community 81 - "Community 81"
Cohesion: 0.33
Nodes (3): test_command_no_parens(), test_custom_command_no_parens(), test_params_argument()

### Community 82 - "Community 82"
Cohesion: 0.40
Nodes (3): Option, Returns the names for the help option., Returns the help option object.          Skipped if :attr:`add_help_option` is `

### Community 84 - "Community 84"
Cohesion: 0.50
Nodes (4): getchar(), pause(), Fetches a single character from the terminal and returns it.  This     will alwa, This command stops execution and waits for the user to press any     key to cont

### Community 89 - "Community 89"
Cohesion: 0.50
Nodes (3): hello(), The simple example from https://github.com/pallets/click#a-simple-example., Simple program that greets NAME for a total of COUNT times.

### Community 95 - "Community 95"
Cohesion: 0.67
Nodes (3): get_binary_stream(), BinaryIO, Returns a system stream for byte processing.      :param name: the name of the s

### Community 96 - "Community 96"
Cohesion: 0.67
Nodes (3): get_text_stream(), TextIO, Returns a system stream for text processing.  This usually returns     a wrapped

## Knowledge Gaps
- **11 isolated node(s):** `on-create-command.sh script`, `click-example-aliases`, `click-example-colors`, `click-example-completion`, `click-example-complex` (+6 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **73 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `cli()` connect `Community 1` to `Community 0`, `Community 129`, `Community 2`, `Community 131`, `Community 4`, `Community 5`, `Community 135`, `Community 136`, `Community 137`, `Community 10`, `Community 139`, `Community 138`, `Community 12`, `Community 11`, `Community 145`, `Community 19`, `Community 147`, `Community 149`, `Community 148`, `Community 150`, `Community 24`, `Community 25`, `Community 27`, `Community 155`, `Community 45`, `Community 70`, `Community 74`, `Community 75`, `Community 76`, `Community 78`, `Community 81`, `Community 83`, `Community 126`, `Community 127`?**
  _High betweenness centrality (0.260) - this node is a cross-community bridge._
- **Why does `CliRunner` connect `Community 2` to `Community 0`, `Community 97`, `Community 37`, `Community 5`, `Community 43`, `Community 76`, `Community 141`, `Community 46`, `Community 15`, `Community 80`, `Community 86`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Why does `Command` connect `Community 15` to `Community 2`, `Community 3`, `Community 7`, `Community 8`, `Community 9`, `Community 12`, `Community 17`, `Community 21`, `Community 32`, `Community 33`, `Community 35`, `Community 37`, `Community 40`, `Community 42`, `Community 43`, `Community 46`, `Community 47`, `Community 49`, `Community 55`, `Community 56`, `Community 62`, `Community 66`, `Community 68`, `Community 69`, `Community 72`, `Community 73`, `Community 74`, `Community 82`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Are the 204 inferred relationships involving `cli()` (e.g. with `test_argument_help()` and `test_argument_help_optional_metavar()`) actually correct?**
  _`cli()` has 204 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `Context` (e.g. with `Abort` and `BadParameter`) actually correct?**
  _`Context` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `Parameter` (e.g. with `Abort` and `BadParameter`) actually correct?**
  _`Parameter` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 61 inferred relationships involving `Command` (e.g. with `Abort` and `BadParameter`) actually correct?**
  _`Command` has 61 INFERRED edges - model-reasoned connections that need verification._