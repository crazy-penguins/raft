import re

import six

from mock import patch

import raft
import raft.collection
import raft.exceptions
import raft.tasks
import raft.program


class Init:
    "__init__"

    def dunder_version_info(self):
        assert hasattr(raft, "__version_info__")
        ver = raft.__version_info__
        assert isinstance(ver, tuple)
        assert all(isinstance(x, int) for x in ver)

    def dunder_version(self):
        assert hasattr(raft, "__version__")
        ver = raft.__version__
        assert isinstance(ver, six.string_types)
        assert re.match(r"\d+\.\d+\.\d+", ver)

    def dunder_version_looks_generated_from_dunder_version_info(self):
        # Meh.
        ver_part = raft.__version__.split(".")[0]
        ver_info_part = raft.__version_info__[0]
        assert ver_part == str(ver_info_part)

    class exposes_bindings:
        def task_decorator(self):
            assert raft.task is raft.tasks.task

        def task_class(self):
            assert raft.Task is raft.tasks.Task

        def collection_class(self):
            assert raft.Collection is raft.collection.Collection

        def context_class(self):
            assert raft.Context is raft.context.Context

        def mock_context_class(self):
            assert raft.MockContext is raft.context.MockContext

        def config_class(self):
            assert raft.Config is raft.config.Config

        def pty_size_function(self):
            assert raft.pty_size is raft.terminals.pty_size

        def local_class(self):
            assert raft.Local is raft.runners.Local

        def runner_class(self):
            assert raft.Runner is raft.runners.Runner

        def promise_class(self):
            assert raft.Promise is raft.runners.Promise

        def failure_class(self):
            assert raft.Failure is raft.runners.Failure

        def exceptions(self):
            # Meh
            for obj in vars(raft.exceptions).values():
                if isinstance(obj, type) and issubclass(obj, BaseException):
                    top_level = getattr(raft, obj.__name__)
                    real = getattr(raft.exceptions, obj.__name__)
                    assert top_level is real

        def runner_result(self):
            assert raft.Result is raft.runners.Result

        def watchers(self):
            assert raft.StreamWatcher is raft.watchers.StreamWatcher
            assert raft.Responder is raft.watchers.Responder
            assert raft.FailingResponder is raft.watchers.FailingResponder

        def program(self):
            assert raft.Program is raft.program.Program

        def filesystemloader(self):
            assert raft.FilesystemLoader is raft.loader.FilesystemLoader

        def argument(self):
            assert raft.Argument is raft.parser.Argument

        def parsercontext(self):
            assert raft.ParserContext is raft.parser.ParserContext

        def parser(self):
            assert raft.Parser is raft.parser.Parser

        def parseresult(self):
            assert raft.ParseResult is raft.parser.ParseResult

        def executor(self):
            assert raft.Executor is raft.executor.Executor

        def call(self):
            assert raft.call is raft.tasks.call

        def Call(self):
            # Starting to think we shouldn't bother with lowercase-c call...
            assert raft.Call is raft.tasks.Call

    class offers_singletons:
        @patch("raft.Context")
        def run(self, Context):
            result = raft.run("foo", bar="biz")
            ctx = Context.return_value
            ctx.run.assert_called_once_with("foo", bar="biz")
            assert result is ctx.run.return_value

        @patch("raft.Context")
        def sudo(self, Context):
            result = raft.sudo("foo", bar="biz")
            ctx = Context.return_value
            ctx.sudo.assert_called_once_with("foo", bar="biz")
            assert result is ctx.sudo.return_value
