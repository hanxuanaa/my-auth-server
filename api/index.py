import json
import os

# 核心开关：从 Vercel 环境变量读取，1=开启，0=关闭
SERVICE_ENABLED = os.getenv("SERVICE_ENABLED", "1") == "1"

def handler(request):
    # 第一步：先检查服务是否开启
    if not SERVICE_ENABLED:
        return json.dumps({
            "status": "denied", 
            "reason": "服务已关闭，禁止使用"
        }), 403  # 403 表示拒绝访问
    
    # 第二步：保留你原来的认证逻辑
    if request.method != "POST":
        return json.dumps({"status": "denied", "reason": "Method not allowed"}), 405

    try:
        data = request.get_json()
        device_id = data.get("device_id", "").strip()

        if not device_id or len(device_id) != 16 or not device_id.isalnum():
            return json.dumps({"status": "denied", "reason": "Invalid ID"}), 400

        # 从环境变量读取黑名单（防止倒卖，可随时加黑）
        blacklist_str = os.getenv("BLACKLIST", "")
        BLACKLIST = set(blacklist_str.split(",") if blacklist_str else set())

        if device_id in BLACKLIST:
            return json.dumps({"status": "denied", "reason": "Blacklisted"}), 200
        else:
            return json.dumps({"status": "allowed", "reason": "Valid ID"}), 200

    except Exception as e:
        return json.dumps({"status": "denied", "reason": str(e)}), 500
