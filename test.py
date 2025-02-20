def calculate_time(N, K, a):
    days_to_N = 0
    days_to_all = 0
    current_things = [0] * N

    while True:
        days_to_N += 1
        # Mỗi ngày sản xuất K thùng cho mỗi phân xưởng
        for i in range(N):
            current_things[i] += K
        
        # Phân phối thùng vào các toa
        for i in range(N):
            if current_things[i] > a[i]:
                if i < N - 1:
                    current_things[i + 1] += current_things[i] - a[i]
                current_things[i] = a[i]

        # Kiểm tra toa N
        if current_things[N - 1] == a[N - 1]:
            break

    days_to_N = days_to_N

    # Reset cho việc kiểm tra tất cả các toa
    current_things = [0] * N
    days_to_all = 0

    while True:
        days_to_all += 1
        for i in range(N):
            current_things[i] += K

        for i in range(N):
            if current_things[i] > a[i]:
                if i < N - 1:
                    current_things[i + 1] += current_things[i] - a[i]
                current_things[i] = a[i]

        if all(current_things[i] == a[i] for i in range(N)):
            break

    return days_to_N, days_to_all

# Đọc dữ liệu từ tệp VC.INP
with open('VC.INP', 'r') as f:
    lines = f.readlines()
    N, K = map(int, lines[0].strip().split())
    a = list(map(int, lines[1].strip().split()))

t_N, t_total = calculate_time(N, K, a)

with open('VC.OUT', 'w') as f:
    f.write(f"{t_N} {t_total}\n")
