from google.adk.tools import ToolContext


async def get_image(tool_context: ToolContext):
    try:
        
        artifact_name = (
            f"generated_image_" + str(tool_context.state.get("loop_iteration", 0)) + ".png"
        )
        artifact = await tool_context.load_artifact(artifact_name)
    


        return {
            "status": "success",
            "message": f"圖像成品 {artifact_name} 成功載入。"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"載入成品 {artifact_name} 時發生錯誤：{str(e)}"
        }
