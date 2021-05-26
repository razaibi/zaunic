datatypes = {
    "int" : {
        "postgresql" : "INT",
        "sqlserver" : "INT",
        "c_sharp" : "Int32",
        "pydantic" : "int",
        "elixir" : "",
        "java" : "int",
        "javascript" : ""
    },
    "tinyint" : {
        "postgresql" : "SMALLINT",
        "sqlserver" : "TINYINT",
        "c_sharp" : "byte",
        "pydantic" : "int",
        "elixir" : "",
        "java" : "byte",
        "javascript" : ""
    },
    "bigint" : {
        "postgresql" : "BIGINT",
        "sqlserver" : "BIGINT",
        "c_sharp" : "Int64",
        "pydantic" : "int",
        "elixir" : "",
        "java" : "long",
        "javascript" : ""
    },
    "boolean" : {
        "postgresql" : "BOOLEAN",
        "sqlserver" : "BIT",
        "c_sharp" : "bool",
        "pydantic" : "int",
        "elixir" : "",
        "java" : "boolean",
        "javascript" : ""
    },
    "char" : {
        "postgresql" : "CHAR",
        "sqlserver" : "CHAR",
        "c_sharp" : "char",
        "pydantic" : "str",
        "elixir" : "",
        "java" : "char",
        "javascript" : ""
    },
    "varchar" : {
        "postgresql" : "VARCHAR",
        "sqlserver" : "VARCHAR",
        "c_sharp" : "string",
        "pydantic" : "str",
        "elixir" : "",
        "java" : "String",
        "javascript" : ""
    },
    "text" : {
        "postgresql" : "TEXT",
        "sqlserver" : "VARCHAR",
        "c_sharp" : "string",
        "pydantic" : "str",
        "elixir" : "",
        "java" : "String",
        "javascript" : ""
    }
    "float" : {
        "postgresql" : "DOUBLE PRECISION",
        "sqlserver" : "FLOAT",
        "c_sharp" : "float",
        "pydantic" : "float",
        "elixir" : "",
        "java" : "float",
        "javascript" : ""
    },
    "date" : {
        "postgresql" : "DATE",
        "sqlserver" : "DATE",
        "c_sharp" : "DateTime",
        "pydantic" : "datetime.date",
        "elixir" : "",
        "java" : "Date",
        "javascript" : ""
    },
    "time" : {
        "postgresql" : "TIMESTAMP",
        "sqlserver" : "DATETIME2",
        "c_sharp" : "DateTime",
        "pydantic" : "datetime.date",
        "elixir" : "",
        "java" : "Date",
        "javascript" : ""
    },
    "uuid" : {
        "postgresql" : "CHAR",
        "sqlserver" : "UNIQUEIDENTIFIER",
        "c_sharp" : "Guid",
        "pydantic" : "uuid.UUID",
        "elixir" : "",
        "java" : "UUID",
        "javascript" : ""
    }
}