from datetime import datetime
from typing import List

from dateutil import parser
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
        # try:
        vec_query = self.fit_transform([query]).toarray()
        for idx, document in enumerate(self.documents):
            doc = document.full_text
            vec_document = self.transform([doc]).toarray()
            similarity = cosine_similarity(vec_query, vec_document)
            if similarity >= 0.7 and document.posted_date:
                job = {
                    "title": document.title,
                    "url": document.url,
                    "source": document.source,
                    "similarity_score": similarity,
                    "organization": document.organization,
                    "posted_date": document.posted_date,
                }
                if document.source == "Somalijobs":
                    if document.posted_date == "Today":
                        job["days_since_posted"] = 0
                    elif document.posted_date == "Yesterday":
                        job["days_since_posted"] = 1
                    else:
                        job["days_since_posted"] = abs((
                                                               datetime.now().date()
                                                               - parser.parse(document.posted_date).date()
                                                       ).days)
                elif document.source == "weworkremotely":
                    job["days_since_posted"] = abs((
                                                           datetime.now().date()
                                                           - parser.parse(document.posted_date).date()
                                                   ).days)

                else:
                    # print(job)
                    job["days_since_posted"] = abs(
                        (datetime.now().date() - parser.parse(document.posted_date).date()).days)
                if document.source == 'diractly':
                    job['url'] = "/" + job['url'].split('/',1)[1]
                    # print(job['url'])


                results.append(job)
        return sorted(
            results, key=lambda item: item["days_since_posted"], reverse=False
        )
        # except Exception as e:
        #     print(e)
        #     raise ValueError("not a valid sentence")
