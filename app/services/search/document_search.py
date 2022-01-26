from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DocumentSearch(TfidfVectorizer):
    def __init__(self, documents: List):
        self.documents = documents
        super(DocumentSearch, self).__init__(stop_words="english")

    def search(self, query):
        """
        Search; this will return documents that match the user query,
        and rank them
        Parameters:
          - query: the query string
        """
        results = []
        try:
            vec_query = self.fit_transform([query]).toarray()
            for idx, document in enumerate(self.documents):
                doc = document.full_text
                vec_document = self.transform([doc]).toarray()
                similarity = cosine_similarity(vec_query, vec_document)
                if similarity >= 0.7:
                    job = {
                        "title": document.title,
                        "url": document.url,
                        "source": document.source,
                        "similarity_score": similarity,
                        "organization": document.organization,
                        "posted_date":document.posted_date
                    }
                    results.append(job)
            return sorted(
                results, key=lambda item: item["similarity_score"], reverse=True
            )
        except Exception:
            raise ValueError("not a valid sentence")
