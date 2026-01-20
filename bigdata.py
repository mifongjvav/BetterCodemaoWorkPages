import json
from collections import defaultdict

class TagTracker:
    def __init__(self, file="data.json"):
        self.file = file
        self.views = defaultdict(int)  # 使用defaultdict记录访问次数
        self._load()
    
    def add(self, tag):
        """记录标签访问"""
        self.views[tag] += 1
    
    def get_weights(self):
        """获取归一化权重（保留3位小数）"""
        total = sum(self.views.values())
        if total == 0:
            return {}
        
        # 计算每个标签的权重
        weights = {}
        for tag, count in self.views.items():
            weight = count / total
            weights[tag] = round(weight, 3)  # 保留3位小数
        
        return weights
    
    def save(self):
        """保存到文件"""
        with open(self.file, 'w', encoding='utf-8') as f:
            json.dump(dict(self.views), f,ensure_ascii=False, indent=2)
    
    def _load(self):
        """从文件加载"""
        try:
            with open(self.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 将普通字典转换为defaultdict
                for tag, count in data.items():
                    self.views[tag] = count
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # 文件不存在或格式错误，保持空的defaultdict


# 使用示例
if __name__ == "__main__":
    # 创建追踪器
    tracker = TagTracker("simple_tags.json")
    
    # 模拟访问：a看1次，b看3次
    print("记录访问: a看1次, b看3次")
    tracker.add("a")          # a访问1次
    tracker.add("b")          # b访问3次
    tracker.add("b")
    tracker.add("b")
    
    # 获取权重
    weights = tracker.get_weights()
    print(f"权重: a={weights.get('a', 0)}, b={weights.get('b', 0)}")
    print(f"a权重: {weights.get('a', 0):.3f}, b权重: {weights.get('b', 0):.3f}")
    
    # 再访问b一次
    print("\n再访问b一次...")
    tracker.add("b")
    
    weights = tracker.get_weights()
    print(f"新权重: a={weights.get('a', 0):.3f}, b={weights.get('b', 0):.3f}")
    print(f"a权重减少: 0.25→{weights.get('a', 0):.3f}")
    print(f"b权重增加: 0.75→{weights.get('b', 0):.3f}")
    
    # 保存到文件
    tracker.save()
    print(f"\n数据已保存到 {tracker.file}")
    
    # 显示文件内容
    print("\n保存的文件内容:")
    with open(tracker.file, 'r') as f:
        print(f.read())