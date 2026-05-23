"""搬家规划 Agent 节点模块"""
from typing import Dict, Any
from app.agent.state import MovingAgentState
from app.llm.client import get_llm_client
import json
import logging

logger = logging.getLogger(__name__)

async def parse_requirements(state: MovingAgentState) -> MovingAgentState:
    """节点 1: 解析搬家需求"""
    logger.info("📋 [搬家Agent] 解析搬家需求")
    llm = get_llm_client()
    prompt = f"""分析用户的搬家需求，提取以下关键信息：
    - source_address: 出发地址
    - target_address: 目标地址
    - source_rooms: 原房屋房间列表，如 ["客厅", "主卧", "次卧", "厨房", "卫生间"]
    - target_rooms: 新房屋房间列表
    - mover_count: 搬家人数（默认2人）
    - moving_date: 搬家日期 (YYYY-MM-DD格式)
    - estimated_cost: 预算（数字，单位元）
    用户输入: {state['user_message']}
    返回 JSON 格式，只包含提取到的信息，未知字段设为 null。"""
    try:
        response = await llm.agenerate([prompt])
        text = response.generations[0][0].text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        result = json.loads(text.strip())
        state['source_address'] = result.get('source_address')
        state['target_address'] = result.get('target_address')
        state['source_rooms'] = result.get('source_rooms', [])
        state['target_rooms'] = result.get('target_rooms', [])
        state['mover_count'] = result.get('mover_count', 2)
        state['moving_date'] = result.get('moving_date')
        state['estimated_cost'] = result.get('estimated_cost')
        logger.info("✅ 需求解析完成")
    except Exception as e:
        logger.error(f"❌ 需求解析失败: {e}")
        state['error'] = str(e)
    return state

async def generate_items(state: MovingAgentState) -> MovingAgentState:
    """节点 2: 生成物品清单"""
    logger.info("📦 [搬家Agent] 生成物品清单")
    llm = get_llm_client()
    rooms = state.get('source_rooms', []) or ["客厅", "主卧", "厨房", "卫生间"]
    prompt = f"""根据以下房间类型，生成详细的搬家物品清单：
    房间列表: {json.dumps(rooms, ensure_ascii=False)}
    每个物品需要包含：
    - name: 物品名称
    - category: 分类（衣物/电器/书籍/厨具/日用品/家具/贵重物品）
    - room: 所属房间
    - quantity: 数量
    - unit: 单位
    - priority: 打包优先级 (high/normal/low)
    - fragile: 是否易碎 (true/false)
    - valuable: 是否贵重 (true/false)
    返回 JSON 数组格式。"""
    try:
        response = await llm.agenerate([prompt])
        text = response.generations[0][0].text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        items = json.loads(text.strip())
        state['items'] = [{"name": i.get("name", ""), "category": i.get("category", "日用品"),
                          "room": i.get("room", "其他"), "quantity": i.get("quantity", 1),
                          "unit": i.get("unit", "件"), "priority": i.get("priority", "normal"),
                          "fragile": i.get("fragile", False), "valuable": i.get("valuable", False)} for i in items]
        logger.info(f"✅ 生成 {len(state['items'])} 个物品")
    except Exception as e:
        logger.error(f"❌ 清单生成失败: {e}")
        state['items'] = []
    return state

async def plan_packing(state: MovingAgentState) -> MovingAgentState:
    """节点 3: 规划打包方案"""
    logger.info("📋 [搬家Agent] 规划打包方案")
    llm = get_llm_client()
    prompt = f"""根据物品清单，规划最佳打包方案：
    物品总数: {len(state.get('items', []))} 件
    生成箱子信息：
    - box_number: 箱号 (A-01, B-02 等)
    - room: 所属房间
    - items: 箱内物品名称列表
    - label: 标签描述
    - fragile: 是否含易碎品 (true/false)
    - priority: 优先级
    返回 JSON 数组格式。"""
    try:
        response = await llm.agenerate([prompt])
        text = response.generations[0][0].text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        boxes = json.loads(text.strip())
        state['boxes'] = boxes
        logger.info(f"✅ 规划了 {len(boxes)} 个箱子")
    except Exception as e:
        logger.error(f"❌ 打包规划失败: {e}")
        state['boxes'] = []
    return state

async def calculate_cost(state: MovingAgentState) -> MovingAgentState:
    """节点 4: 计算搬家费用"""
    logger.info("💰 [搬家Agent] 计算搬家费用")
    base_fee = 300
    distance_fee = 500
    item_fee = len(state.get('items', [])) * 15
    box_fee = len(state.get('boxes', [])) * 25
    floor_fee = 200
    fragile_count = sum(1 for i in state.get('items', []) if i.get('fragile'))
    valuable_count = sum(1 for i in state.get('items', []) if i.get('valuable'))
    fragile_fee = fragile_count * 20
    valuable_fee = valuable_count * 50
    total = base_fee + distance_fee + item_fee + box_fee + floor_fee + fragile_fee + valuable_fee
    state['estimated_cost'] = total
    state['cost_breakdown'] = {
        "起步价": base_fee,
        "距离费": distance_fee,
        "物品费": item_fee,
        "箱子费": box_fee,
        "楼层费": floor_fee,
        "易碎品附加": fragile_fee,
        "贵重物品附加": valuable_fee
    }
    logger.info(f"✅ 估算费用: ¥{total}")
    return state

async def generate_guide(state: MovingAgentState) -> MovingAgentState:
    """节点 5: 生成还原指南"""
    logger.info("✅ [搬家Agent] 生成还原指南")
    llm = get_llm_client()
    prompt = f"""根据箱子信息，生成新家还原指南：
    目标房间: {json.dumps(state.get('target_rooms', []), ensure_ascii=False)}
    箱子列表: {json.dumps(state.get('boxes', [])[:10], ensure_ascii=False)}
    生成还原步骤，返回 JSON 数组，每项包含：
    - step: 步骤编号
    - action: 操作描述
    - target_room: 目标房间
    - box_number: 相关箱号"""
    try:
        response = await llm.agenerate([prompt])
        text = response.generations[0][0].text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        guide = json.loads(text.strip())
        state['unpacking_guide'] = guide
    except Exception as e:
        logger.error(f"❌ 还原指南生成失败: {e}")
        state['unpacking_guide'] = []
    return state

async def generate_response(state: MovingAgentState) -> MovingAgentState:
    """节点 6: 生成最终回复"""
    logger.info("💬 [搬家Agent] 生成回复")
    items = state.get('items', [])
    boxes = state.get('boxes', [])
    cost = state.get('estimated_cost', 0)
    breakdown = state.get('cost_breakdown', {})
    fragile_count = sum(1 for i in items if i.get('fragile'))
    valuable_count = sum(1 for i in items if i.get('valuable'))
    response = f"""🏠 **搬家规划已完成！**

---
**📍 搬家信息**
| 项目 | 内容 |
|------|------|
| 出发地 | {state.get('source_address', '待补充')} |
| 目的地 | {state.get('target_address', '待补充')} |
| 搬家日期 | {state.get('moving_date', '待确定')} |
| 搬家人数 | {state.get('mover_count', 2)} 人 |

---
**📦 物品统计**
| 类别 | 数量 |
|------|------|
| 总物品数 | {len(items)} 件 |
| 预计箱子数 | {len(boxes)} 箱 |
| 易碎物品 | {fragile_count} 件 |
| 贵重物品 | {valuable_count} 件 |

---
**💰 费用估算**
"""
    for item, amount in breakdown.items():
        response += f"| {item} | ¥{amount} |\n"
    response += f"| **总计** | **¥{cost}** |\n"
    response += """
---
**💡 温馨提示**
1. 🔴 **贵重物品**（首饰、现金、电子设备）建议随身携带
2. ⚠️ **易碎物品**（玻璃、陶瓷、画框）做好防护标记
3. 📄 **重要文件**（证件、合同）单独整理一箱
4. 👕 **当天衣物**和洗漱用品最后打包，作为"第一箱"
"""
    state['response'] = response
    state['generated_checklist'] = {
        "items": items, "boxes": boxes, "cost": cost,
        "source_address": state.get('source_address'), "target_address": state.get('target_address')
    }
    state['suggested_actions'] = ["查看完整物品清单", "导出打包清单", "保存到项目"]
    logger.info("✅ 回复生成完成")
    return state
