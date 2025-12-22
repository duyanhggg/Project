# Definition for singly-linked list.
# class ListNode(object):
#     def __init__(self, val=0, next=None):
#         self.val = val
#         self.next = next
class Solution(object):
    def mergeTwoLists(self, list1, list2):
        """
        :type list1: Optional[ListNode]
        :type list2: Optional[ListNode]
        :rtype: Optional[ListNode]
        """
        merge_lists= []
        list1_clean = ''.join(filter(str.isdigit, list1))
        list2_clean = ''.join(filter(str.isdigit, list2))
        merge_lists = list1_clean + list2_clean
        me_list = sorted(set(merge_lists))
        print(me_list)

list1 = input()
list2 = input()
sol = Solution()
sol.mergeTwoLists(list1, list2)