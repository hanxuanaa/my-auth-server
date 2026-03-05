import json
import os

# 全局开关（从环境变量读取）
SERVICE_ENABLED = os.getenv("SERVICE_ENABLED", "1") == "1"
# 设备黑名单
BLACKLIST = set(os.getenv("BLACKLIST", "").split(",")) if os.getenv("BLACKLIST") else set()

def handler(event, context):
    """Vercel Serverless Function 标准入口"""
    # 1. 检查服务开关
    if not SERVICE_ENABLED:
        return {
            "statusCode": 403,
            "body": json.dumps({"status": "denied", "reason": "服务已关闭"}),
            "headers": {"Content-Type": "application/json"}
        }
    
    # 2. 仅处理POST请求
    if event["httpMethod"] != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"status": "denied", "reason": "仅支持POST请求"}),
            "headers": {"Content-Type": "application/json"}
        }
    
    # 3. 解析请求体
    try:
        data = json.loads(event["body"]) if event["body"] else {}
        device_id = data.get("device_id", "").strip()
        
        # 4. 校验设备ID格式
        if not device_id or len(device_id) != 16 or not device_id.isalnum():
            return {
                "statusCode": 400,
                "body": json.dumps({"status": "denied", "reason": "设备ID无效（16位字母/数字）"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        # 5. 校验黑名单
        if device_id in BLACKLIST:
            return {
                "statusCode": 200,
                "body": json.dumps({"status": "denied", "reason": "设备已拉黑"}),
                "headers": {"Content-Type": "application/json"}
            }
        
        # 6. 认证通过
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "allowed", "reason": "认证通过"}),
            "headers": {"Content-Type": "application/json"}
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"status": "denied", "reason": f"服务器错误：{str(e)}"}),
            "headers": {"Content-Type": "application/json"}
        }
