# import requests
#
# # from app.crud import get_all_jobs
# from app.config import settings
# from app.services.search.document import Document
# from app.database import dynamodb_web_service, dynamodb
# import boto3
#
#
# # def get_jobs():
# #     # date = datetime.now().astimezone().replace(hour=0,minute=0, second=0, microsecond=0).isoformat().replace('+',
# #     # '%2B')
# #     url = f"https://api.reliefweb.int/v1/jobs?appname=apidoc&filter[field]=country.name&filter[value]=Somalia&limit=1000"
# #     url += f"&preset=latest&profile=full&fields[include][]"
# #     resp = requests.get(url)
# #     data = resp.json()
# #     return data
# #
# #
# # def get_refined_job_list():
# #     jobs = get_jobs()
# #     som_jobs = []
# #     for item in jobs["data"]:
# #         city = ""
# #         if "city" in item["fields"].keys():
# #             city = item["fields"]["city"][0]["name"]
# #         job = dict(
# #             title=item["fields"]["title"],
# #             category=item["fields"]["career_categories"][0]["name"],
# #             posted_date=item["fields"]["date"]["created"],
# #             url=item["fields"]["url"],
# #             country="Somalia",
# #             city=city,
# #             organization=item["fields"]["source"][0]["name"],
# #             source="reliefweb",
# #         )
# #         som_jobs.append(job)
# #         # create_jobs(job=job, db= SessionLocal())
# #     return som_jobs
#
#
# def create_documents():
#     table = dynamodb.Table('jobs')
#     jobs_ = table.scan()['Items']
#     # print(jobs_)
#     # jobs = get_refined_job_list()
#     # print(jobs)
#     docs = []
#     for job in jobs_:
#         docs.append(Document(**job))
#     return docs
