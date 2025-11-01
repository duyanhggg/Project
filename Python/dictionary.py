def create_dictionary(): #Từ điển Anh - Việt
    dictionary = {
        "Lion":"Sư tử",
        "Tiger":"Hổ",
        "Elephant":"Voi",
        "Giraffe":"Hươu cao cổ",
        "Zebra":"Ngựa vằn"
    }
    return dictionary

def select_choice(): #Chọn chức năng
    print("1. Tra từ 🔍")
    print("2. Thêm từ ➕")
    print("3. Xoá từ ➖")
    print("4. Thoát chương trình 🚪")
    choice = input("Chọn chức năng (1-4): ")
    return choice
def lookup_word(dictionary): #Tra từ
    word = input("Nhập từ tiếng Anh cần tra: ")
    meaning = dictionary.get(word)
    if meaning:
        print(f"{word} nghĩa là: {meaning}")
    else:
        print(f"Không tìm thấy từ: {word}")
    print("Bạn có muốn tra từ khác không? (y/n)")
    choice = input()
    if choice.lower() == "y":
        lookup_word(dictionary)

def add_word(dictionary): #Thêm từ
    word = input("Nhập từ tiếng Anh cần thêm: ")
    meaning = input("Nhập nghĩa tiếng Việt của từ: ")
    dictionary[word] = meaning
    print(f"Đã thêm từ: {word} - {meaning}")
    print("Bạn có muốn thêm từ khác không? (y/n)")
    print("0.Quay lại menu chính")
    choice = input()
    if choice.lower() == "y":
        add_word(dictionary)
    if choice == "0":
        select_choice()

def remove_word(dictionary): #Xoá từ
    word = input("Nhập từ tiếng Anh cần xoá: ")
    if word in dictionary:
        del dictionary[word]
        print(f"Đã xoá từ thành công: {word}")
    else:
        print(f"Không tìm thấy từ: {word}")
    print("Bạn có muốn xoá từ khác không? (y/n)")
    print("0.Quay lại menu chính")
    choice = input()
    if choice.lower() == "y":
            remove_word(dictionary)
    if choice == "0":
        select_choice()

def update_word(dictionary): #Sửa từ
    word = input("Nhập từ tiếng Anh cần sửa: ")
    if word in dictionary:
        new_meaning = input("Nhập nghĩa tiếng Việt mới của từ: ")
        dictionary[word] = new_meaning
        print(f"Đã cập nhật từ: {word} - {new_meaning}")
    else:
        print(f"Không tìm thấy từ: {word}")
    print("Bạn có muốn sửa từ khác không? (y/n)")
    print("0.Quay lại menu chính")
    choice = input()
    if choice.lower() == "y":
        update_word(dictionary)
    if choice == "0":
        select_choice()

def exit_program(): #Thoát chương trình
    print("Cảm ơn bạn đã sử dụng TỪ ĐIỂN ANH VIỆT! Hẹn ngày gặp lại!")
    exit()

if __name__ == "__main__":
    dictionary = create_dictionary()
    while True:
        choice = select_choice()
        if choice not in ["1", "2", "3", "4"]:
            print("Lựa chọn không hợp lệ. Vui lòng chọn lại.")
            continue
        if choice == "1":
            lookup_word(dictionary)
        elif choice == "2":
            add_word(dictionary)
        elif choice == "3":
            remove_word(dictionary)
        elif choice == "4":
            update_word(dictionary)