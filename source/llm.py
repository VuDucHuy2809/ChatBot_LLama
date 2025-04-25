from langchain_community.llms import LlamaCpp

model_path = 'model/ggml-vistral-7B-chat-q8.gguf' 

llm_kwargs = {
    "temperature": 0,
    "max_tokens": 512,
    "top_p" : 0.95,
    "top_k":40,
    "n_gpu_layers": 0,
    "n_batch": 512,
    "verbose": False,
    "n_ctx": 8192,
}

llm = LlamaCpp(
    model_path=model_path,
    **llm_kwargs,
)