import weaviate

class weaviateUtils:
    def __init__(self, host: str, port: int, additional_headers: dict):
        self.client = weaviate.Client(
            url=f"http://{host}:{port}", additional_headers=additional_headers
        )

    def checkDBStatus(self):
        return self.client.is_ready()

    def listAllCollections(self):
        return self.client.schema.get()["classes"]

    def createCollection(self, class_obj):
        self.client.schema.create_class(class_obj)

    def deleteCollection(self, collection_name):
        self.client.schema.delete_class(collection_name)

    def insertObjectsIntoCollection(self, objects: list, collection_name: str):
        for obj in objects:
            self.client.data_object.create(class_name=collection_name, data_object=obj)

    def getClientObj(self):
        return self.client

    def performVectorSearch(self, en_lang_input):
        vector_search_response = (
            self.client.query.get(
                "Manapuram_v1", ["title", "section", "subsection", "content"]
            )
            .with_hybrid(
                query=en_lang_input,
            )
            .with_additional(["score", "explainScore"])
            .with_limit(5)
            .do()
        )
        return vector_search_response
