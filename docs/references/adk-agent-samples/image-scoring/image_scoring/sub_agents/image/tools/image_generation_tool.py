from datetime import datetime
from google import genai
from google.genai import types
from google.adk.tools import ToolContext
from google.cloud import storage
from .... import config


client = genai.Client(
    vertexai=True
)


async def generate_images(imagen_prompt: str, tool_context: ToolContext):

    try:

        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=imagen_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="9:16",
                safety_filter_level="block_low_and_above",
                person_generation="allow_adult",
            ),
        )
        generated_image_paths = []
        if response.generated_images is not None:
            for generated_image in response.generated_images:
                # 取得圖像位元組
                image_bytes = generated_image.image.image_bytes
                counter = str(tool_context.state.get("loop_iteration", 0))
                artifact_name = f"generated_image_" + counter + ".png"
                # 呼叫儲存到 gcs 的函式
                if config.GCS_BUCKET_NAME:
                    save_to_gcs(tool_context, image_bytes, artifact_name, counter)

                # 儲存為 ADK 成品 (可選，如果其他 ADK 元件仍然需要)
                report_artifact = types.Part.from_bytes(
                    data=image_bytes, mime_type="image/png"
                )

                await tool_context.save_artifact(artifact_name, report_artifact)
                print(f"圖像也已儲存為 ADK 成品：{artifact_name}")

                return {
                    "status": "success",
                    "message": f"圖像已生成。ADK 成品：{artifact_name}。",
                    "artifact_name": artifact_name,
                }
        else:
            # model_dump_json 可能不存在，或者不是取得錯誤詳細資訊的最佳方式
            error_details = str(response)  # 或可用的更具體的錯誤欄位
            print(f"未生成圖像。回應：{error_details}")
            return {
                "status": "error",
                "message": f"未生成圖像。回應：{error_details}",
            }

    except Exception as e:

        return {"status": "error", "message": "未生成圖像。 {e}"}


def save_to_gcs(tool_context: ToolContext, image_bytes, filename: str, counter: str):
    # --- 儲存到 GCS ---
    storage_client = storage.Client()  # 初始化 GCS 客戶端
    bucket_name = config.GCS_BUCKET_NAME

    unique_id = tool_context.state.get("unique_id", "")
    current_date_str = datetime.utcnow().strftime("%Y-%m-%d")
    unique_filename = filename
    gcs_blob_name = f"{current_date_str}/{unique_id}/{unique_filename}"

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob_name)

    try:
        blob.upload_from_string(image_bytes, content_type="image/png")
        gcs_uri = f"gs://{bucket_name}/{gcs_blob_name}"

        # 將 GCS URI 儲存在會話上下文中
        # 將 GCS URI 儲存在會話上下文中
        tool_context.state["generated_image_gcs_uri_" + counter] = gcs_uri

    except Exception as e_gcs:

        # 決定這是否為工具的致命錯誤
        return {
            "status": "error",
            "message": f"圖像已生成但上傳到 GCS 失敗：{e_gcs}",
        }
        # --- 結束儲存到 GCS ---
