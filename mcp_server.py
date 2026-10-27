# -*- coding: utf-8 -*-
"""
GenPark Ctrip Destination Crowd Density Router MCP Server
Exposes attraction crowd density routing and queue optimization tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import GenParkCtripDestinationCrowdDensityRouter

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-ctrip-destination-crowd-density-router", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "optimize_attraction_visitation",
                        "description": "Optimizes real-time attraction visitor dispersion and queueing wait times using queuing theory and dynamic heatmap routing.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "attraction_name": {"type": "string"},
                                "maximum_daily_capacity": {"type": "integer"},
                                "requested_visit_hour": {"type": "number"},
                                "current_live_visitors": {"type": "integer"}
                            },
                            "required": ["attraction_name"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "optimize_attraction_visitation":
            router = GenParkCtripDestinationCrowdDensityRouter()
            res = router.optimize_attraction_visitation(
                attraction_name=args.get("attraction_name", "Forbidden City"),
                maximum_daily_capacity=args.get("maximum_daily_capacity", 40000),
                requested_visit_hour=args.get("requested_visit_hour", 11.0),
                current_live_visitors=args.get("current_live_visitors", 35000),
                alternative_sister_pois=args.get("alternative_sister_pois")
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        r = GenParkCtripDestinationCrowdDensityRouter()
        test_res = r.optimize_attraction_visitation("Shanghai Disney Resort", 60000, 13.0, 52000)
        print(f"Test Saturation: {test_res['current_saturation_pct']}%")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
