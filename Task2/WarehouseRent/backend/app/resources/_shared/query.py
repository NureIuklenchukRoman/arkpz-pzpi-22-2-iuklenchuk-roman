from sqlalchemy import and_, select, or_
from sqlalchemy import DateTime, Date, Time, Integer, SmallInteger, BigInteger, Boolean

def apply_filters_to_query(query, Model, filter: dict):
    filter = filter.dict()
    for column, value in filter.items():
        if value is None:
            continue
        if isinstance(value, dict):
            # Example: {"price": {"gt": 2}} or {"price": {"lt": 10}}
            for operator, operator_value in value.items():
                column_attr = getattr(Model, column)
                if operator == "gt":
                    query = query.filter(column_attr > operator_value)
                elif operator == "lt":
                    query = query.filter(column_attr < operator_value)
                elif operator == "ge":
                    query = query.filter(column_attr >= operator_value)
                elif operator == "le":
                    query = query.filter(column_attr <= operator_value)
                elif operator == "eq":
                    query = query.filter(column_attr == operator_value)
                elif operator == "ne":
                    query = query.filter(column_attr != operator_value)
        else:
            if isinstance(value, str):
                query = query.filter(getattr(Model, column).ilike(f"%{value}%"))
            elif isinstance(value, list):
                query = query.filter(getattr(Model, column).in_(value))
            else:
                query = query.filter(getattr(Model, column) == value)
                
    return query


def update_model(Model, data):
    for column, value in data.items():
        setattr(Model, column, value)