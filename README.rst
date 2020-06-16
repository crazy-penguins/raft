Welcome to Invoke (raft)!
==================

Invoke is a Python (2.7 and 3.4+) library for managing shell-oriented
subprocesses and organizing executable Python code into CLI-invokable tasks. It
draws inspiration from various sources (``make``/``rake``, Fabric 1.x, etc) to
arrive at a powerful & clean feature set.

For a high level introduction, including example code, please see `our main
project website <http://pyinvoke.org>`_; or for detailed API docs, see `the
versioned API website <http://docs.pyinvoke.org>`_.

Raft is a forked version of invoke that undoes one thing about ``invoke``--
preserving underscores by default.  In invoke, the following task:

.. code-block:: python

    @task
    def some_task(ctx):
       """
       This is some task
       """
       print('Hello, raft!')

must be run as ``invoke some-task``.  raft preserves the underscore, and instead
we would have ``raft some_task``.

