import json
import os
from http import HTTPStatus

# 核心开关：从 Vercel 环境变量读取（1=开启，0=关闭）
SERVICE_ENABLED = os.getenv("SERVICE_ENABLED", "1") == "1"

def handler(request):
    """
    Vercel Python 函数入口，处理 POST 请求的设备认证
    """
    # 1. 全局开关：直接关闭所有访问
    if not SERVICE_ENABLED:
        response = {
            "status": "denied",
            "reason": "服务已关闭，禁止使用"
        }
        return json.dumps(response), HTTPStatus.FORBIDDEN, {"Content-Type": "application/json"}
    
    # 2. 仅允许 POST 请求
    if request.method != "POST":
        response = {
            "status": "denied",
            "reason": "仅支持 POST 请求"
        }
        return json.dumps(response), HTTPStatus.METHOD_NOT_ALLOWED, {"Content-Type": "application/json"}
    
    # 3. 解析请求参数
    try:
        # 兼容 Vercel 的 request 对象，处理不同格式的请求体
        if request.content_type == "application/json":
            data = request.get_json(silent=True) or {}
        else:
            data = json.loads(request.get_data().decode("utf-8")) if request.get_data() else {}
        
        device_id = data.get("device_id", "").strip()
        
        # 4. 校验设备ID格式（16位字母/数字）
        if not device_id or len(device_id) != 16 or not device_id.isalnum():
            response = {
                "status": "denied",
                "reason": "设备ID无效（需16位字母/数字）"
            }
            return json.dumps(response), HTTPStatus.BAD_REQUEST, {"Content-Type": "application/json"}
        
        # 5. 校验黑名单
        blacklist_str = os.getenv("BLACKLIST", "")
        blacklist = set(blacklist_str.split(",")) if blacklist_str else set()
        
        if device_id in blacklist:
            response = {
                "status": "denied",
                "reason": "设备已被拉黑"
            }
            return json.dumps(response), HTTPStatus.OK, {"Content-Type": "application/json"}
        
        # 6. 认证通过
        response = {
            "status": "allowed",
            "reason": "设备认证通过"
        }
        return json.dumps(response), HTTPStatus.OK, {"Content-Type": "application/json"}
    
    # 7. 捕获所有异常，避免服务崩溃
    except Exception as e:
        response = {
            "status": "denied",
            "reason": f"服务器错误：{str(e)}"
        }
        return json.dumps(response), HTTPStatus.INTERNAL_SERVER_ERROR, {"Content-Type": "application/json"}
