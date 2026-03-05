import json
import os

# 全局开关：1=开启，0=关闭（从Vercel环境变量读取）
SERVICE_ENABLED = os.getenv("SERVICE_ENABLED", "1") == "1"
# 设备黑名单：多个设备ID用逗号分隔
BLACKLIST = set(os.getenv("BLACKLIST", "").split(",")) if os.getenv("BLACKLIST") else set()

def handler(event, context):
    """
    Vercel Python Serverless 标准入口函数
    event：包含所有请求信息（方法、参数、请求体等）
    返回值：固定格式的字典（statusCode/body/headers）
    """
    # 1. 检查全局开关，直接关闭所有访问
    if not SERVICE_ENABLED:
        return {
            "statusCode": 403,
            "body": json.dumps({"status": "denied", "reason": "服务已关闭，禁止使用"}),
            "headers": {"Content-Type": "application/json; charset=utf-8"}
        }
    
    # 2. 只允许POST请求
    if event["httpMethod"] != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"status": "denied", "reason": "仅支持POST请求"}),
            "headers": {"Content-Type": "application/json; charset=utf-8"}
        }
    
    # 3. 解析请求体（兼容空请求体）
    try:
        data = json.loads(event["body"]) if event.get("body") else {}
        device_id = data.get("device_id", "").strip()
        
        # 4. 校验设备ID格式（必须16位字母/数字）
        if not device_id or len(device_id) != 16 or not device_id.isalnum():
            return {
                "statusCode": 400,
                "body": json.dumps({"status": "denied", "reason": "设备ID无效（需16位字母/数字）"}),
                "headers": {"Content-Type": "application/json; charset=utf-8"}
            }
        
        # 5. 校验黑名单
        if device_id in BLACKLIST:
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "denied", "reason": "该设备已被拉黑"}),
                "headers": {"Content-Type": "application/json; charset=utf-8"}
            }
        
        # 6. 认证通过
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "allowed", "reason": "设备认证通过"}),
            "headers": {"Content-Type": "application/json; charset=utf-8"}
        }
    
    # 7. 捕获所有异常，避免服务崩溃
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "denied", "reason": f"服务器错误：{str(e)}"}),
            "headers": {"Content-Type": "application/json; charset=utf-8"}
        }
