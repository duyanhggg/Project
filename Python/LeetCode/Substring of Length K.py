class Solution(object):
    def hasSpecialSubstring(self, s, k):
        """
        :type s: str
        :type k: int
        :rtype: bool
        """
        res = []
        for i in range((len(s))):
            substring = s[i:i + k]
            if substring in s[i + k:]:
                return True
        return False

s = input()
k = int(input())
solution = Solution()
if solution.hasSpecialSubstring(s, k) == True:
    print("true")
else:
    print("false")