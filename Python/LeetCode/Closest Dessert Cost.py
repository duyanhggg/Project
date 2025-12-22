class Solution(object):
    def closestCost(self, baseCosts, toppingCosts, target):
        """
        :type baseCosts: List[int]
        :type toppingCosts: List[int]
        :type target: int
        :rtype: int
        """
        # Sắp xếp toppings
        toppingCosts.sort()
        
        # Tạo tất cả tổ hợp topping có thể
        possible_topping_costs = {0}
        
        for topping in toppingCosts:
            new_costs = set()
            for cost in possible_topping_costs:
                for count in range(len(toppingCosts) + 1):
                    new_costs.add(cost + count * topping)   
            possible_topping_costs.update(new_costs)
        
        # Tìm chi phí gần target nhất
        closest_cost = float('inf')
        min_diff = float('inf')
        
        for base in baseCosts:
            for topping_cost in possible_topping_costs:
                total_cost = base + topping_cost
                diff = abs(total_cost - target)
                
                # Cập nhật nếu gần hơn, hoặc bằng nhưng nhỏ hơn
                if diff < min_diff or (diff == min_diff and total_cost < closest_cost):
                    min_diff = diff
                    closest_cost = total_cost
        return closest_cost

baseCosts = [1,7]
toppingCosts = [3,4]
target = 10
Sol = Solution()
print(Sol.closestCost(baseCosts, toppingCosts, target))