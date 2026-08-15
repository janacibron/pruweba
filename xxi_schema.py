import json,jsonschema
class SchemaValidator:
    def __init__(s):s.schema={"type":"object","required":["source","total","passed","checks"],"properties":{"source":{"type":"string"},"total":{"type":"integer","minimum":1},"passed":{"type":"integer","minimum":0},"failed":{"type":"integer","minimum":0},"checks":{"type":"array","items":{"type":"object","required":["name","status"],"properties":{"name":{"type":"string"},"status":{"enum":["PASS","FAIL","SKIP"]},"detail":{"type":"string"}}}}}};s.version=1
    def validate(s,evidence):return jsonschema.validate(evidence,s.schema)or True
print('[XXI] Schema Validator: ready')
