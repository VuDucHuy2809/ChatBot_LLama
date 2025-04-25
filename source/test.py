from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
print("✅ Kết nối thành công:", es.ping())