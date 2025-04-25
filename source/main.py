from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache
from chain import get_answer
from fastapi import FastAPI, HTTPException, Form, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn
import json
from typing import Any, Dict, List
from langchain.globals import set_llm_cache
from langchain_core.caches import RETURN_VAL_TYPE
from langchain_elasticsearch import ElasticsearchCache

### CACHE
app = FastAPI()

#set_llm_cache(InMemoryCache())  # Use InMemoryCache
#set_llm_cache(SQLiteCache(database_path="QA.db"))  # Use SQLiteCache
class SearchableElasticsearchCache(ElasticsearchCache):
    @property
    def mapping(self) -> Dict[str, Any]:
        mapping = super().mapping
        mapping["mappings"]["properties"]["parsed_llm_output"] = {
            "type": "text",
            "analyzer": "standard",
        }
        return mapping

    def build_document(
        self, prompt: str, llm_string: str, return_val: RETURN_VAL_TYPE
    ) -> Dict[str, Any]:
        body = super().build_document(prompt, llm_string, return_val)
        body["parsed_llm_output"] = self._parse_output(body["llm_output"])
        return body

    @staticmethod
    def _parse_output(data: List[str]) -> List[str]:
        parsed_outputs = []
        for output in data:
            try:
                parsed = json.loads(output)
                content = parsed.get("kwargs", {}).get("message", {}).get("kwargs", {}).get("content", "")
                parsed_outputs.append(content)
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing output: {output}, Error: {e}")
                parsed_outputs.append("error")  # Thêm giá trị mặc định nếu lỗi
        return parsed_outputs

set_llm_cache(
    SearchableElasticsearchCache(
        #es_url="http://localhost:9200", index_name="llm-chat-cache"
        es_url="http://host.docker.internal:9200", index_name="llm-chat-cache"
    )
)

# Define input model for HTTP POST
class Input(BaseModel):
    input: str
    
    
@app.get("/")
async def hello_world():
    return {"message": "Welcome to chatbot!"}

@app.post("/chatbot")
async def process(input: str = Form(...)):
    try:
        # Use langchain with dynamically included operation and essay in the prompt
        output = get_answer(input)
        return {"output": output}
    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# WebSocket route for real-time communication
@app.websocket("/ws/chatbot")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Accept WebSocket connection
    
    try:
        while True:
            # Receive message from the client (user)
            data = await websocket.receive_text()
            
            # Use langchain to process the input and get the output
            output = get_answer(data)
            
            # Send the answer back to the client (user)
            await websocket.send_text(f"Response: {output}")
    
    except WebSocketDisconnect:
        print("Client disconnected")
        await websocket.close()

###
