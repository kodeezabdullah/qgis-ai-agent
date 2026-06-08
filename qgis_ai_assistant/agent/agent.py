import json

from .openrouter_client import OpenRouterClient
from .tools import (
    TOOLS_SCHEMA,
    get_layers,
    get_attributes,
    run_query,
    buffer_analysis,
    highlight_features,
    remove_layer,
    rename_layer,
    zoom_to_layer,
    toggle_visibility,
    add_layer_from_path,
    clip_layer,
    intersect_layers,
    union_layers,
    dissolve_layer,
    merge_layers,
    spatial_join,
    calculate_ndvi,
    calculate_ndwi,
    hillshade,
    slope_analysis,
    aspect_analysis,
    zonal_statistics,
    raster_clip,
    unsupervised_classification,
    histogram_equalization,
    mosaic_rasters,
    band_composite,
    calculate_area,
    calculate_length,
    centroid,
    reproject_layer,
    fix_geometries,
    apply_categorized_style,
    apply_graduated_style,
    export_layer,
    export_to_csv,
    print_map,
    select_by_attribute,
    export_attribute_table,
    field_calculator,
    get_feature_count,
    filter_features,
    pan_sharpening,
    supervised_classification,
    calculate_ndre,
    apply_heatmap_style,
    change_layer_color,
    open_attribute_table,
    zoom_to_feature,
    get_crs,
    execute_qgis_code,
    generate_report,
    generate_csv,
    generate_map_image,
)


SYSTEM_PROMPT = (
    "You are an intelligent QGIS spatial analysis assistant.\n\n"
    "IMPORTANT RULES:\n"
    "1. ALWAYS call get_layers() first to see what layers exist.\n"
    "2. ALWAYS call get_attributes(layer_name) before any filter/query/select operation.\n"
    "3. Use ONLY the actual field names returned by get_attributes().\n"
    "4. Never assume field names — always check first.\n"
    "5. For filtering features, use run_query() with correct QGIS expression syntax.\n"
    "6. For hiding/showing specific features, use filter_features() with correct field and value.\n"
    "7. When the user says 'show only X', use filter_features() to filter the layer.\n"
    "8. Always explain what you did and what field you used.\n\n"
    "WHEN NO SPECIFIC TOOL EXISTS FOR A TASK:\n"
    "1. Write clean PyQGIS Python code to accomplish it.\n"
    "2. Call execute_qgis_code() with the code.\n"
    "3. Never say 'I cannot do this' — always try to write code first.\n"
    "4. Available in code: iface, QgsProject, processing, QgsVectorLayer, QgsRasterLayer, "
    "QgsExpression, QgsField, QgsCoordinateReferenceSystem, QVariant, QColor, and all qgis.core classes via 'qgis'.\n"
    "5. Assign the final value to a variable named 'result' to have it returned.\n\n"
    "CONVERSATION CONTEXT:\n"
    "You have access to the full conversation history above. "
    "Use previous context to understand follow-up questions. "
    "If the user says 'now do X' or 'also do Y', refer to previous messages.\n\n"
    "BEFORE generating any Word document or PDF file:\n"
    "1. First check if python-docx is installed by trying: import docx\n"
    "2. If ImportError, respond with EXACTLY this message:\n"
    "'To enable document generation, please run this command in OSGeo4W Shell first:\n\n"
    "python -m pip install pypdf python-docx openpyxl pandas\n\n"
    "After running, reload the plugin (Plugins → Plugin Reloader → qgis_ai_assistant) and ask me again!'\n"
    "3. Only proceed with document generation if import succeeds."
)

MAX_HISTORY_MESSAGES = 20

EMPTY_RESPONSE_FALLBACK = "Task completed. Let me know if you need anything else!"

MAX_ITERATIONS = 10

TOOL_REGISTRY = {
    "get_layers": get_layers,
    "get_attributes": get_attributes,
    "run_query": run_query,
    "buffer_analysis": buffer_analysis,
    "highlight_features": highlight_features,
    "remove_layer": remove_layer,
    "rename_layer": rename_layer,
    "zoom_to_layer": zoom_to_layer,
    "toggle_visibility": toggle_visibility,
    "add_layer_from_path": add_layer_from_path,
    "clip_layer": clip_layer,
    "intersect_layers": intersect_layers,
    "union_layers": union_layers,
    "dissolve_layer": dissolve_layer,
    "merge_layers": merge_layers,
    "spatial_join": spatial_join,
    "calculate_ndvi": calculate_ndvi,
    "calculate_ndwi": calculate_ndwi,
    "hillshade": hillshade,
    "slope_analysis": slope_analysis,
    "aspect_analysis": aspect_analysis,
    "zonal_statistics": zonal_statistics,
    "raster_clip": raster_clip,
    "unsupervised_classification": unsupervised_classification,
    "histogram_equalization": histogram_equalization,
    "mosaic_rasters": mosaic_rasters,
    "band_composite": band_composite,
    "calculate_area": calculate_area,
    "calculate_length": calculate_length,
    "centroid": centroid,
    "reproject_layer": reproject_layer,
    "fix_geometries": fix_geometries,
    "apply_categorized_style": apply_categorized_style,
    "apply_graduated_style": apply_graduated_style,
    "export_layer": export_layer,
    "export_to_csv": export_to_csv,
    "print_map": print_map,
    "select_by_attribute": select_by_attribute,
    "export_attribute_table": export_attribute_table,
    "field_calculator": field_calculator,
    "get_feature_count": get_feature_count,
    "filter_features": filter_features,
    "pan_sharpening": pan_sharpening,
    "supervised_classification": supervised_classification,
    "calculate_ndre": calculate_ndre,
    "apply_heatmap_style": apply_heatmap_style,
    "change_layer_color": change_layer_color,
    "open_attribute_table": open_attribute_table,
    "zoom_to_feature": zoom_to_feature,
    "get_crs": get_crs,
    "execute_qgis_code": execute_qgis_code,
    "generate_report": generate_report,
    "generate_csv": generate_csv,
    "generate_map_image": generate_map_image,
}


class QgisAiAgent:
    def __init__(self, api_key, model="moonshotai/kimi-k2.6:free"):
        self.client = OpenRouterClient(api_key=api_key, model=model)
        self.conversation_history = []

    def clear_history(self):
        self.conversation_history = []

    def _execute_tool(self, name, arguments):
        func = TOOL_REGISTRY.get(name)
        if func is None:
            return {"error": f"Unknown tool: {name}"}
        try:
            args = arguments if isinstance(arguments, dict) else json.loads(arguments or "{}")
        except (TypeError, ValueError) as e:
            return {"error": f"Invalid tool arguments: {e}"}
        try:
            return func(**args)
        except TypeError as e:
            return {"error": f"Invalid arguments for {name}: {e}"}
        except Exception as e:
            return {"error": f"Tool {name} failed: {e}"}

    def _trim_history(self):
        if len(self.conversation_history) > MAX_HISTORY_MESSAGES:
            self.conversation_history = self.conversation_history[-MAX_HISTORY_MESSAGES:]

    def run(self, user_query):
        user_message = {"role": "user", "content": user_query}
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.conversation_history)
        messages.append(user_message)

        final_text = None

        for _ in range(MAX_ITERATIONS):
            try:
                result = self.client.complete(messages, tools=TOOLS_SCHEMA)
            except Exception as e:
                return f"[API error] {e}"

            if not isinstance(result, dict):
                return "[API error] Unexpected response from model client."
            if "error" in result:
                return f"[API error] {result['error']}"

            message = result.get("message")
            if not isinstance(message, dict):
                return "[API error] Missing message in model response."
            messages.append(message)

            tool_calls = message.get("tool_calls")
            if not tool_calls:
                content = message.get("content")
                if content is None or (isinstance(content, str) and not content.strip()):
                    final_text = EMPTY_RESPONSE_FALLBACK
                else:
                    final_text = content
                self.conversation_history.append(user_message)
                self.conversation_history.append({"role": "assistant", "content": final_text})
                self._trim_history()
                return final_text

            for call in tool_calls:
                fn = call.get("function", {}) if isinstance(call, dict) else {}
                name = fn.get("name", "")
                arguments = fn.get("arguments", "{}")
                tool_result = self._execute_tool(name, arguments)
                try:
                    serialized = json.dumps(tool_result, default=str)
                except Exception as e:
                    serialized = json.dumps({"error": f"Could not serialize tool result: {e}"})
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.get("id", "") if isinstance(call, dict) else "",
                    "name": name,
                    "content": serialized,
                })

        return "[Agent stopped] Maximum iterations reached without a final response."
