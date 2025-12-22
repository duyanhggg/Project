class Solution(object):
    def maxSumOfSquares(self, num, sum):
        """
        :type num: int
        :type sum: int
        :rtype: str
        """
        # Bước 0: Kiểm tra khả thi
        if sum > 9 * num or sum < 1:
            return ""
        
        # Bước 1: Khởi tạo array num chữ số
        digits = [0] * num
        remaining = sum
        
        # Bước 2: Greedy - Điền từ PHẢI sang TRÁI
        # Lý do: Tập trung chữ số lớn ở phải để score max
        for i in range(num - 1, -1, -1):
            digits[i] = min(9, remaining)
            remaining -= digits[i]
        
        # Bước 3: Đảm bảo chữ số đầu >= 1
        # Nếu chữ số đầu = 0, chuyển 1 từ chữ số kế tiếp
        if digits[0] == 0:
            for i in range(1, num):
                if digits[i] > 0:
                    digits[i] -= 1
                    digits[0] = 1
                    break
        
        return ''.join(map(str, digits))
