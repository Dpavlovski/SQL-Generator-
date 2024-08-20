def chat_output_template(
        query: str,
        output: str
) -> str:
    return f"""
           Generated SQL query:

           {query}

           Output:

           {output}
           """
