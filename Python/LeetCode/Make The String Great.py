class Solution(object):
    def makeGood(self, s):
        """
        :type s: str
        :rtype: str
        """
        stack = []
        for char in s:
            # Kiểm tra nếu stack không trống và ký tự hiện tại tạo cặp xấu
            if stack and stack[-1].lower() == char.lower() and stack[-1] != char:
                stack.pop()  # Xóa ký tự trước
            else:
                stack.append(char)  # Thêm ký tự hiện tại
        
        return "".join(stack)
    
s = input()
solution = Solution()
print(solution.makeGood(s))
