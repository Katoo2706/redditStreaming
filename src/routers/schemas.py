# define Avro schema: https://avro.apache.org/docs/1.11.1/specification/

people_value_v1 = """{
    "namespace": "com.avro.exampledomain",
    "name": "Person",
    "type": "record",
    "fields": [
        {
            "name": "name",
            "type": "string"
        },
        {
            "name": "title",
            "type": "string"
        }
    ]
}"""


# Schema changes
people_value_v2 = """{
    "namespace": "com.avro.exampledomain",
    "name": "Person",
    "type": "record",
    "fields": [
        {
            "name": "first_name",
            "type": "string"
        },
        {
            "name": "last_name",
            "type": "string"
        },
        {
            "name": "title",
            "type": "string"
        }
    ]
}"""