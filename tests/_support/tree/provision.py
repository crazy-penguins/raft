"System setup code."

from raft import task


@task
def db(c):
    "Stand up one or more DB servers."
    pass


@task
def web(c):
    "Stand up a Web server."
    pass
