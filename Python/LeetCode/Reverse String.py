class Solution(object):
    def reverseString(self, s):
        """
        :type s: List[str]
        :rtype: None Do not return anything, modify s in-place instead.
        """
        s.reverse()
        print(s)

s = ["h","e","l","l","o"]
obj = Solution()
obj.reverseString(s)