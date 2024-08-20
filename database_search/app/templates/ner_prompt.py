def ner_prompt(text: str):
    return f"""
    You are an expert at extracting relevant information from text for searching in a SQL relational database.
    Your task is to identify all key concepts, nouns, verbs, and other elements that can help in searching for 
    table names, column names, and string values. Ensure to extract information that is directly useful for database
    queries.

    Example 1:
    Input:
    What are the top 3 products purchased by John Doe?

    Output:
    {{ "information": ["products", "purchased", "John Doe"] }}

    Example 2:
    Input:
    Show the inventory levels of all warehouses with a capacity greater than 1000 units.

    Output:
    {{ "information": ["inventory levels", "warehouses", "capacity"] }}

    Example 3:
    Input:
    List all transactions involving customers who have a loyalty score above 80.

    Output:
    {{ "information": ["transactions", "customers", "loyalty score"] }}

    Example 4:
    Input:
    Find all suppliers who provide more than 50 different products.

    Output:
    {{ "information": ["suppliers", "provide", "products"] }}

    Example 5:
    Input:
    I want you to give me all the items that are bought buy the user John Doe. 
    Than from them find the highest priced item. 
    I want you return all the number of items that have that specific price.

    Output:
    {{ "information": ["items", "bought", "user", "John Doe", "price"] }}

    Text:
    {text}

    Return the extracted information in a list in JSON format.
    """
