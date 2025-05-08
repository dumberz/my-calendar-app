from flask import Flask, render_template, request, redirect
from datetime import datetime
import os

app = Flask(__name__)

SCHEDULE_FILE = "schedule.txt"

# 일정 불러오기
def load_schedule():
    try:
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []

# 일정 저장하기
def save_schedule(schedule):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as file:
        for item in schedule:
            file.write(f"{item}\n")

# 일정 삭제하기
def delete_schedule(item):
    schedule = load_schedule()
    if item in schedule:
        schedule.remove(item)
    save_schedule(schedule)

# 일정 날짜 기준 정렬
def sort_schedule_by_date(schedule):
    return sorted(schedule, key=lambda x: datetime.strptime(x.split(" | ")[0], "%Y-%m-%dT%H:%M"))

@app.route('/')
def index():
    schedule = load_schedule()
    schedule = sort_schedule_by_date(schedule)
    return render_template('index.html', schedule=schedule)

@app.route('/add', methods=['POST'])
def add():
    item = request.form['item']
    date_str = request.form['date']
    schedule = load_schedule()

    if date_str:
        try:
            # 연도를 4자리로 제한
            parts = date_str.split('-')
            if len(parts[0]) > 4:
                parts[0] = parts[0][:4]  # 연도가 4자리를 초과하면 자르기
            date_str = '-'.join(parts)

            if "T" not in date_str:
                date_str += "T00:00"  # 시간 없이 날짜만 들어왔을 때 00:00으로 설정

            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
            schedule.append(f"{date_obj.strftime('%Y-%m-%dT%H:%M')} | {item}")
            save_schedule(schedule)

        except ValueError as e:
            print(f"날짜 처리 오류: {e}")
            return "날짜 형식 오류! 다시 시도해 주세요.", 400
    else:
        return "날짜가 입력되지 않았습니다.", 400

    return redirect('/')

@app.route('/delete/<item>')
def delete(item):
    delete_schedule(item)
    return redirect('/')

# 배포 환경을 위한 수정된 부분
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
