from raft import task, Collection


@task
def dummy(c):
    pass


ns = Collection(dummy, Collection("subcollection"))
