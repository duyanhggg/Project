def solution(books):
    books.sort(key=lambda x: (x[0], -int(x[1:])))  
    return books

# Bạn có thể thêm code ở dưới đây
if __name__ == "__main__":
    books = ['A12345', 'B37712', 'A54321']
    print(solution(books))