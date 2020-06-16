from raft import task


@task(aliases=("z", "a"))
def toplevel(c):
    pass
