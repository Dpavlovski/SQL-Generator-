from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple
from pydantic import BaseModel


@dataclass(frozen=True)
class Database(BaseModel):
    dbname: str
    user: str
    password: str
    host: str
    port: int
    table_schema: Optional[str] = None
    date_created: Optional[datetime] = None


@dataclass(frozen=True)
class Column(BaseModel):
    name: str
    data_type: str
    is_nullable: bool
    collection_name: str
    foreign_key_table: Optional[str]
    is_primary_key: bool = False

    def __str__(self):
        constraints = []
        if self.is_primary_key:
            constraints.append("PRIMARY KEY")
        if self.foreign_key_table != "None":
            constraints.append(f"FOREIGN KEY REFERENCES {self.foreign_key_table}")
        if not self.is_nullable:
            constraints.append("NOT NULL")

        return f"{self.name} {self.data_type} {' '.join(constraints)}".strip()


@dataclass(frozen=True)
class Table(BaseModel):
    name: str
    columns: Tuple[Column, ...]

    def __str__(self):
        columns_str = "\n  ".join(str(column) for column in self.columns)
        return f"Table: {self.name}\n  {columns_str}"


class ForeignKey(BaseModel):
    from_column: str
    to_column: str
    to_table: str

    def __init__(self, data: Tuple[str]):
        super().__init__(
            from_column=data[0],
            to_column=data[1],
            to_table=data[2]
        )
