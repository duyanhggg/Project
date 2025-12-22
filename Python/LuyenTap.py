class Solution(object):
    def longestCommonPrefix(self, strs):
        """
        : type strs: List[str]
        :rtype: str
        """
        if not strs:
            return ""
        
        # Compare character by character across all strings
        for i in range(len(strs[0])):
            char = strs[0][i]
            for j in range(1, len(strs)):
                # If we've reached the end of a string or characters don't match
                if i >= len(strs[j]) or strs[j][i] != char:
                    return strs[0][:i]
        
        return strs[0]

# Test with examples
a = Solution()

# If you need user input, use eval or json.loads
user_input = input()
strs = eval(user_input)
print(a.longestCommonPrefix(strs))