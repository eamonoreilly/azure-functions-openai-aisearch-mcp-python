import azure.functions as func
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name("IngestData")
@app.route(methods=["POST"])
@app.embeddings_store_output(arg_name="requests", input= "{Text}", input_type="rawtext", connection_name="AZURE_AISEARCH_ENDPOINT", collection="openai-index", model="%EMBEDDING_MODEL_DEPLOYMENT_NAME%")
def ingest_data(req: func.HttpRequest, requests: func.Out[str]) -> func.HttpResponse:
    user_message = req.get_json()
    if not user_message:
        return func.HttpResponse(json.dumps({"message": "No message provided"}), status_code=400, mimetype="application/json")
    requests.set(json.dumps(user_message))
    response_json = {
        "status": "success",
        "title": user_message.get("Title"),
        "text": user_message.get("Text")
    }
    return func.HttpResponse(json.dumps(response_json), status_code=200, mimetype="application/json")


# This contains the input tool properties for the get_support_information MCP tool.
tool_properties_get_support_json = json.dumps([
    {
        "propertyName": "searchText",
        "propertyType": "string",
        "description": "The search text to use for retrieving support incident information."
    }
])
# This is the MCP tool that will be used to retrieve support information based on the search text.
@app.function_name("GetSupportInformation")
@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_support_information",
    description="Retrieves support incident information based on a search prompt.",
    toolProperties=tool_properties_get_support_json,
)
@app.semantic_search_input(arg_name="result", connection_name="AZURE_AISEARCH_ENDPOINT", collection="openai-index", query="{arguments.searchText}", embeddings_model="%EMBEDDING_MODEL_DEPLOYMENT_NAME%", chat_model="%CHAT_MODEL_DEPLOYMENT_NAME%")
def prompt(context, result: str) -> str:
    result_json = json.loads(result)
    return result_json.get("Response")