from collections import defaultdict
# unhappy_count = 0

# Bước 1: Tạo preference_rank cho mỗi người
# Bước 2: Tạo pair_map

# Bước 3: Duyệt mỗi người x:
#     y = pair_map[x]  // người ghép cặp với x
    
#     Duyệt từng người u trong preferences[x]:
#         Nếu u == y: dừng (vì u không thích hơn y được)
        
#         v = pair_map[u]  // người ghép cặp với u
        
#         Nếu preference_rank[u][x] < preference_rank[u][v]:
#             // u thích x hơn v
#             unhappy_count += 1
#             dừng vòng lặp này

# return unhappy_count

class Solution(object):
    def unhappyFriends(self, n, preferences, pairs):
        """
        :type n: int
        :type preferences: List[List[int]]
        :type pairs: List[List[int]]
        :rtype: int
        """
        unhappy = 0
        preference_rank = defaultdict(dict)
        
        # Bước 1: Tạo preference_rank cho mỗi người
        for person in range(n):
            for index, friend in enumerate(preferences[person]):
                preference_rank[person][friend] = index
        
        # Bước 2: Tạo pair_map
        pair_map = {}
        for x, y in pairs:
            pair_map[x] = y
            pair_map[y] = x
        
        # Bước 3: Duyệt mỗi người x
        for x in range(n):
            y = pair_map[x]  # người ghép cặp với x
            
            # Duyệt từng người u trong preferences[x]
            for u in preferences[x]:
                if u == y:
                    break  # dừng vì u không thích hơn y được
                
                v = pair_map[u]  # người ghép cặp với u
                
                if preference_rank[u][x] < preference_rank[u][v]:
                    # u thích x hơn v
                    unhappy += 1
                    break
        
        return unhappy


# Test Case
if __name__ == "__main__":
    solution = Solution()
    
    # Test 1
    n = 4
    preferences = [[1, 2, 3], [3, 2, 0], [3, 1, 0], [1, 2, 0]]
    pairs = [[0, 1], [2, 3]]
    result = solution.unhappyFriends(n, preferences, pairs)
    print(f"Test 1: {result}")  # Expected Output: 2
    
    # Test 2
    n = 2
    preferences = [[1], [0]]
    pairs = [[0, 1]]
    result = solution.unhappyFriends(n, preferences, pairs)
    print(f"Test 2: {result}")  # Expected Output: 0
    
    # Test 3
    n = 4
    preferences = [[1, 3, 2], [2, 3, 0], [0, 2, 1], [0, 1, 3]]
    pairs = [[1, 3], [0, 2]]
    result = solution.unhappyFriends(n, preferences, pairs)
    print(f"Test 3: {result}")  # Expected Output: 4



