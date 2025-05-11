import flet as ft
import json
import os
from datetime import datetime, timedelta
import uuid

# مسیر فایل JSON برای ذخیره داده‌ها
DATA_FILE = "words.json"

# تابع برای بارگذاری داده‌ها از فایل JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"words": {}, "schedules": {}}

# تابع برای ذخیره داده‌ها در فایل JSON
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تابع برای دریافت تاریخ‌های مرور پیش‌فرض
def get_default_review_dates():
    today = datetime.now().date()
    return [
        today,
        today + timedelta(days=1),
        today + timedelta(days=3),
        today + timedelta(days=10)
    ]

# تابع برای دریافت تاریخ‌های مرور در صورت "بلد نبودم"
def get_failed_review_dates():
    today = datetime.now().date()
    return [
        today + timedelta(days=1),
        today + timedelta(days=2),
        today + timedelta(days=5),
        today + timedelta(days=7),
        today + timedelta(days=15)
    ]

# تابع اصلی برنامه
def main(page: ft.Page):
    page.title = "برنامه یادگیری لغات"
    page.rtl = True
    page.fonts = {"B Nazanin": "assets/B Nazanin.ttf"}  # مسیر فونت را بررسی کنید
    page.theme = ft.Theme(font_family="B Nazanin")
    data = load_data()

    # تابع برای تغییر صفحه
    def navigate_to(view):
        page.controls.clear()
        page.controls.append(view)
        page.update()

    # صفحه اصلی
    def main_view():
        return ft.Column([
            ft.Text("به برنامه یادگیری لغات خوش آمدید!", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("کلمه جدید", on_click=lambda e: navigate_to(new_word_view())),
            ft.ElevatedButton("مرور کلمات امروز", on_click=lambda e: navigate_to(review_view()))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # صفحه افزودن کلمه جدید
    def new_word_view():
        english_field = ft.TextField(label="کلمه انگلیسی", width=300)
        meaning_field = ft.TextField(label="معنی کلمه", width=300)

        def save_word(e):
            if english_field.value and meaning_field.value:
                word_id = str(uuid.uuid4())
                data["words"][word_id] = {
                    "english": english_field.value,
                    "meaning": meaning_field.value
                }
                review_dates = get_default_review_dates()
                for date in review_dates:
                    date_str = date.isoformat()
                    if date_str not in data["schedules"]:
                        data["schedules"][date_str] = []
                    data["schedules"][date_str].append(word_id)
                save_data(data)
                page.snack_bar = ft.SnackBar(ft.Text("کلمه با موفقیت ذخیره شد!"))
                page.snack_bar.open = True
                navigate_to(main_view())
            else:
                page.snack_bar = ft.SnackBar(ft.Text("لطفاً هر دو فیلد را پر کنید!"))
                page.snack_bar.open = True

        return ft.Column([
            ft.Text("افزودن کلمه جدید", size=24, weight=ft.FontWeight.BOLD),
            english_field,
            meaning_field,
            ft.ElevatedButton("ذخیره کلمه", on_click=save_word),
            ft.ElevatedButton("بازگشت", on_click=lambda e: navigate_to(main_view()))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # صفحه مرور کلمات
    def review_view():
        today = datetime.now().date().isoformat()
        words_to_review = data["schedules"].get(today, [])
        if not words_to_review:
            return ft.Column([
                ft.Text("هیچ کلمه‌ای برای مرور امروز وجود ندارد!", size=24),
                ft.ElevatedButton("بازگشت", on_click=lambda e: navigate_to(main_view()))
            ], alignment=ft.MainAxisAlignment.CENTER)

        current_index = [0]
        show_meaning = [False]

        def update_card():
            if current_index[0] < len(words_to_review):
                word_id = words_to_review[current_index[0]]
                word = data["words"][word_id]
                card_content = [
                    ft.Text(word["english"], size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(word["meaning"], size=18, visible=show_meaning[0])
                ]
                buttons = [
                    ft.ElevatedButton("نمایش معنی", on_click=lambda e: toggle_meaning()),
                    ft.ElevatedButton("بلد بودم", on_click=lambda e: mark_known(word_id)),
                    ft.ElevatedButton("بلد نبودم", on_click=lambda e: mark_unknown(word_id))
                ]
                if show_meaning[0]:
                    buttons.pop(0)  # حذف دکمه نمایش معنی پس از نمایش
                return ft.Column(card_content + buttons, alignment=ft.MainAxisAlignment.CENTER)
            else:
                del data["schedules"][today]  # حذف لیست مرور امروز
                save_data(data)
                return ft.Column([
                    ft.Text("کلمات امروز مرور شده‌اند!", size=24),
                    ft.ElevatedButton("بازگشت", on_click=lambda e: navigate_to(main_view()))
                ], alignment=ft.MainAxisAlignment.CENTER)

        def toggle_meaning():
            show_meaning[0] = True
            page.controls[0] = update_card()
            page.update()

        def mark_known(word_id):
            current_index[0] += 1
            show_meaning[0] = False
            page.controls[0] = update_card()
            page.update()

        def mark_unknown(word_id):
            review_dates = get_failed_review_dates()
            for date in review_dates:
                date_str = date.isoformat()
                if date_str not in data["schedules"]:
                    data["schedules"][date_str] = []
                if word_id not in data["schedules"][date_str]:
                    data["schedules"][date_str].append(word_id)
            save_data(data)
            current_index[0] += 1
            show_meaning[0] = False
            page.controls[0] = update_card()
            page.update()

        return update_card()

    # نمایش صفحه اصلی
    navigate_to(main_view())

# اجرای برنامه
if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")