from raft import task
from raft.util import debug


@task
def foo(c):
    debug("my-sentinel")
