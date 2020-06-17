from raft import task


@task
def mytask(c):
    assert c.outer.inner.hooray == "yml"
