from enum import Enum


class PostgresDataType(str, Enum):
    # Numeric types
    SMALLINT = "smallint"
    INTEGER = "integer"
    BIGINT = "bigint"
    DECIMAL = "decimal"
    NUMERIC = "numeric"
    REAL = "real"
    DOUBLE_PRECISION = "double precision"
    SMALLSERIAL = "smallserial"
    SERIAL = "serial"
    BIGSERIAL = "bigserial"

    # Monetary types
    MONEY = "money"

    # Character types
    CHAR = "character"
    VARCHAR = "character varying"
    TEXT = "text"

    # Binary types
    BYTEA = "bytea"

    # Date/Time types
    DATE = "date"
    TIME = "time"
    TIME_WITHOUT_TIME_ZONE = "time without time zone"
    TIME_WITH_TIME_ZONE = "time with time zone"
    TIMESTAMP = "timestamp"
    TIMESTAMP_WITHOUT_TIME_ZONE = "timestamp without time zone"
    TIMESTAMP_WITH_TIME_ZONE = "timestamp with time zone"
    INTERVAL = "interval"

    # Boolean type
    BOOLEAN = "boolean"

    # UUID type
    UUID = "uuid"

    # Geometric types
    POINT = "point"
    LINE = "line"
    LSEG = "lseg"
    BOX = "box"
    PATH = "path"
    POLYGON = "polygon"
    CIRCLE = "circle"

    # Network address types
    CIDR = "cidr"
    INET = "inet"
    MACADDR = "macaddr"

    # JSON types
    JSON = "json"
    JSONB = "jsonb"

    # XML type
    XML = "xml"

    # Arrays
    ARRAY = "array"

    # Range types
    INT4RANGE = "int4range"
    INT8RANGE = "int8range"
    NUMRANGE = "numrange"
    TSRANGE = "tsrange"
    TSTZRANGE = "tstzrange"
    DATERANGE = "daterange"

    # Composite types (user-defined types)
    COMPOSITE = "composite"

    # Object Identifier type
    OID = "oid"

    # Enumerated type (user-defined types)
    ENUM = "enum"

    # Pseudo types
    VOID = "void"
    RECORD = "record"
    ANY = "any"
    ANYARRAY = "anyarray"
