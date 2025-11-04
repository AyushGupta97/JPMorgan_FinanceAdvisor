from langchain_community.tools import DuckDuckGoSearchResults
from typing import List, Union

class InternetSearchTool:
    def __init__(self):
        self.searcher = DuckDuckGoSearchResults()

    def search(self, query: str, max_results: int = 5) -> List[str]:
        results: Union[str, List[str]] = self.searcher.run(query)
        if isinstance(results, str):
            results = [results]
        return results[:max_results]
