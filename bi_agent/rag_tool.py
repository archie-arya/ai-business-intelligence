from langchain_core.tools import tool

from bi_agent.retriever import retrieve


@tool
def search_business_documents(query: str) -> str:
    """
    Search the business knowledge base for policies, definitions,
    business terminology, and other documented business context.

    Use this tool when the answer depends on information contained
    in business documents rather than numerical data stored in
    PostgreSQL tables.
    """

    results = retrieve(query, top_k=5)

    if not results:
        return "No relevant business documents were found."

    formatted_results = []

    for result in results:
        formatted_results.append(
            (
                f"Source: {result['source']}\n"
                f"Chunk: {result['chunk_index']}\n"
                f"Similarity: {result['similarity']:.4f}\n"
                f"Content:\n{result['content']}"
            )
        )

    return "\n\n---\n\n".join(formatted_results)