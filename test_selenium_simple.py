import pytest


from selenium import webdriver #подключение библиотеки
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
driver = webdriver.Chrome('C:/chromedriver_win32/chromedriver') #получение объекта веб-драйвера для нужного браузера

@pytest.fixture(autouse=True)
def testing():
    driver.implicitly_wait(10)
    # Переходим на страницу авторизации
    driver.get('http://petfriends1.herokuapp.com/login')

    yield

    driver.quit()


def test_show_my_pets():
    # Вводим email
    driver.find_element_by_id('email').send_keys('ryt@mail.ru')
    # Вводим пароль
    driver.find_element_by_id('pass').send_keys('111111')
    # Нажимаем на кнопку входа в аккаунт
    driver.find_element_by_css_selector('button[type="submit"]').click()
    # Проверяем, что мы оказались на главной странице пользователя
    assert driver.find_element_by_tag_name('h1').text == "PetFriends"

    driver.find_element_by_css_selector('#navbarNav > ul > li:nth-child(1) > a').click()

    # Ждем, пока страница загрузится и получаем таблицу питомцев
    table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#all_my_pets > table > tbody"))
    )

    # запоминаем строки таблицы в массив
    rows = table.find_elements_by_tag_name("tr")
    petsAmount = len(rows)

    # проверка, что количетсво строк и текст на странице совпадают
    driver.find_element_by_xpath(f"//*[contains(., 'Питомцев: {petsAmount}')]")

    photosAmount = 0  # для подсчета фотографий
    names = set()  # для проверки одинаковых имён
    infos = set()  # для проверки одинаковых питомцев

    # проходимся по всем питомцам
    for i in range(petsAmount):
        row = rows[i]
        picSrc = row.find_element_by_tag_name('img').get_attribute('src')
        # если есть фото, увеличиваем общее число фотографий
        if picSrc != '':
            photosAmount += 1

        # считываем имя, возраст, породу
        name = row.find_element_by_css_selector('td:nth-child(2)').text
        poroda = row.find_element_by_css_selector('td:nth-child(3)').text
        age = row.find_element_by_css_selector('td:nth-child(4)').text

        # формируем по этим данным строку, чтобы обнаруживать повторяющихся питомцев
        # Получится строка типа "Жучка-$$-12-$$-Дворняга"
        info = get_pet_data(name, age, poroda)

        # проверяем, что такого ещё не было
        assert info in infos is False
        # и добавляем в set
        infos.add(info)

        # проверка, что есть имя
        assert name != ''
        # проверка, что имя уникально
        assert name in names is False
        # добавляем имя в set, чтобы для следующих питомцев оно тоже учитывалось
        names.add(name)

        # проверяем наличие породы и возраста
        assert poroda != ''
        assert age != ''

    # проверка количества фотографий
    assert photosAmount > petsAmount / 2


def get_pet_data(name, age, poroda):
    return f'{name}-$$-{age}-$$-{poroda}'
