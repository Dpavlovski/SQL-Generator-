def sql_query_guardrail(question: str):
    return f"""Given a question determine if the question could be transformed into a sql SELECT query (Data Query Language).

    Example 1:
    
    Input: How are you?
    
    Output: {{
      "reason": "The question 'How are you?' is a conversational and open-ended question typically asked in social interactions to inquire about someone's well-being. It does not relate to data retrieval, manipulation, or any specific data-related operation that SQL is designed to handle.",
      "verdict": "no"
    }}
    
    Example 2:
    
    Input: How many bear bottles are sold in 2023?
    
    Output: {{
      "reason": "The question asks for the number of beer bottles sold in 2023. This can be addressed by querying a database where sales data is stored, typically in a structured format such as SQL. Databases usually have tables that store sales information with fields like product type, quantity, and date, making it feasible to construct a SQL query to get the required information.",
      "verdict": "yes"
    }}
    
    Example 3:
    
    Input: Create a table for orders.
    
    Output: {{
      "reason": "The question 'Create a table for orders' is asking for the creation of a database table, which involves defining the structure and schema of the table, such as columns and data types. This operation is typically performed using the Data Definition Language (DDL) subset of SQL, specifically using a CREATE TABLE statement. It does not involve querying data or retrieving information, which is the purpose of a SELECT statement in SQL.",
      "verdict": "no"
    }}
    
    Question:
    {question}
    
    Return a json with keys "reason" and "verdict". First provide your reason why you think the question can or cannot be transformed into SELECT sql. And in the end provide a  verdict yes if it could be transformed into SELECT sql query, and no if it can not.
    """
