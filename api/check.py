import json
import os

def handler(request):
    if request.method != "POST":
        return json.dumps({"status": "denied", "reason": "Method not allowed"}), 405

    try:
        data = request.get_json()
        device_id = data.get("device_id", "").strip()

        if not device_id or len(device_id) != 16 or not device_id.isalnum():
            return json.dumps({"status": "denied", "reason": "Invalid ID"}), 400

        # 🔐 从环境变量读取黑名单（安全！别人看不到）
        blacklist_str = os.getenv("BLACKLIST", "")
        BLACKLIST = set(blacklist_str.split(",")) if blacklist_str else set()

        if device_id in BLACKLIST:
            return json.dumps({"status": "denied", "reason": "Blacklisted"}), 200
        else:
            return json.dumps({"status": "allowed"}), 200

    except Exception as e:
        return json.dumps({"status": "denied", "reason": str(e)}), 500
