# TrueCrime-KGLLMs

This repository runs queries using a KGLLM (Microsoft GraphRAG) and compares responses to a naive LLM and naive RAG on the Serial Podcast data, but can be extended to other datasets. 

To query all the models, run queryAllModels.sh The script expects 4 arguments: <br>
--DATA_DIR: directory path to the input data <br>
--ROOT_DIR: directory path to the root directory in graphrag/ for running the GraphRAG pipeline. For more information see GraphRAG tutorial <br>
--QUERY_FILE: path to .txt file containing queries to ask the models <br>
--TEXT_FILES: information to be used in naive RAG <br>

Sample query files are provided
