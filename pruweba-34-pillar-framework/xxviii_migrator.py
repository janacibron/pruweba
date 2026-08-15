class VersionMigrator:
    def __init__(s):s.migrations={}
    def register(s,from_v,to_v,fn):s.migrations[(from_v,to_v)]=fn
    def migrate(s,state,from_v,to_v):return s.migrations.get((from_v,to_v),lambda x:x)(state)
    def path(s,state,versions):r=state;[r:=s.migrate(r,v,versions[i+1])for i,v in enumerate(versions[:-1])];return r
print('[XXVIII] Version Migrator: ready')
