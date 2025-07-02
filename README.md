**Overview**

This is sequel to my [previous project](https://github.com/YashKushwaha/chatbot_ui) where I used llama index framework to build chat bots. In this project, I have implemented the Agent frameworks available in llama-index. 

I have implemented `FunctionAgent` and `ReActAgent` till now.

**LLM Used**
- For `ReActAgent` models with thinking capability are required
- Current pipeline tested with [qwen3:14b](https://ollama.com/library/qwen3:14b) model served using [Ollama](https://ollama.com/download/linux)
- Models that couldn't be used as ReAct agent because they don't support thinking - [Mistral-7B](https://huggingface.co/lmstudio-community/Mistral-7B-Instruct-v0.3-GGUF), [Phi -4](https://huggingface.co/lmstudio-community/phi-4-GGUF) (though it's [reasoning variant](https://huggingface.co/microsoft/Phi-4-reasoning) can)
- TODO : Test OpenAI models & [Nova lite models](https://aws.amazon.com/ai/generative-ai/nova/) on AWS bedrock


**Data Pipeline**
- [`SQUAD` dataset from huggingface](https://huggingface.co/datasets/rajpurkar/squad) is used to create knowledge base
  - SQuAD : Stanford Question Answering Dataset. [Homepage](https://rajpurkar.github.io/SQuAD-explorer/)
  - a reading comprehension dataset, consisting of questions posed by crowdworkers on a set of Wikipedia articles, where the answer to every question is a segment of text, or span, from the corresponding reading passage, or the question might be unanswerable
  - Extensively used to benchmark LLMs
- Raw data is processed and stored in MongoDB, server being run locally through Docker. [Docker Image Link](https://hub.docker.com/_/mongo)
- Embedding model used - [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
  - Used FastAPI to convert the model into a service running locally which allows decoupling of embedding model from main LLM application
  - To use the embedding model being server locally, a custom client for remote embedding servers was created by extending the `BaseEmbedding` class [defined in llama index](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/base/embeddings/base.py) as defined [here](https://docs.llamaindex.ai/en/stable/module_guides/models/embeddings/#custom-embedding-model) 
-  ChromaDB running locally in [client-server mode](https://docs.trychroma.com/docs/run-chroma/client-server) is used as the vector database
   - No customization done to settings 
   - Default settings being - [hnws algorithm](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world) & l2 distance metric

**Back End**
- FastAPI used to create endpoints to interact with the LLM & the agents
- App made modular by having a separate folder for routes and grouping endpoints based on their utility
  -  end points serving the front end are defined in `/backend/routes/ui_routes.py`
  -  end points to interact with llm/agent defined in `/backend/routes/api_routes.py`
  -  Separate endpoints to view the details of MongoDB server & ChromaDB server attached to the app (`/backend/routes/db_routes.py`, `/backend/routes/vec_db_routes.py`)

**Front End**
- Allows user to interact with LLMs/Agents being served with FastAPI backend
- Vanilla HTML, CSS & JS to create the front end, no framework used
- HTML templates are defined for FastAPI to render through Jinja tempplating
- JS makes the call from front end to back end & displays server response in Front End
  - Code highlighting using [highlight.js](https://highlightjs.org/)
  - Markdown in server response converted to html tags using [marked.js](https://marked.js.org/)
- TODO :
  - Improve the color theme and layout of the application 
  - Back end and front end can be fully separated by using dedicated JS frameworks

## Observability and Experiment Logging
- llama index uses very high level of abstraction thus simple print statement or logging cant be used to understand the internal workings of llama index (e.g. agent.run(query))
- But llama index has support for different call back managers and tracing tools
- Current project used [MLFlow Tracing & integration with llamaindex](https://docs.llamaindex.ai/en/stable/examples/observability/MLflow/) 
  - [ML Flow llama index documentation](https://mlflow.org/docs/latest/genai/flavors/llama-index/index.html)
  - [ML flow - llama index api reference](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.llama_index.html)