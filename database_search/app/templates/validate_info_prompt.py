def validate_info_prompt(
        table_info: str,
        question: str
) -> str:
    return f"""You are a Postgres expert. Given table info determine whether there is enough information to create a Postgres query from the given question.
    Give a verdict of "no" if there is no sufficient information or if something is missing to create the query from the given question. Return a list of suggested tables that you think are missing.
    Give a verdict of "yes" if this information is all that is needed to create the query, and no other information is needed to create the query from the given question.
    IMPORTANT: Provide your reason for what you have decided. 

    Here are the table info: 
    {table_info}

    Question:
    {question}

    Return a json with keys "reason" and "verdict". First provide your reason for whether there is or is not enough sufficient information. Provide a verdict of value yes or no from the reason. 
    If the verdict is "no", return "missing_tables" a list of missing tables. 
    """
