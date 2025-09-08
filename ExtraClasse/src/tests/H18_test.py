"""
Teste história de usuário H18

História de usuário:
    Como um usuário do sistema, gostaria de fazer login com todos os meus dados salvos
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def test_h18_login_with_saved_data():
    # Configuração do driver do Selenium
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")  # Minimiza logs do Chrome
    service = Service(log_path='NUL')  # Oculta logs do ChromeDriver no Windows

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get("http://localhost:5173/login")  # URL do sistema

    # Localizar os campos de entrada e preencher com dados salvos
    username_field = driver.find_element(By.NAME, "matricula")
    password_field = driver.find_element(By.NAME, "senha")

    username_field.send_keys("robson") # matricula
    password_field.send_keys("1234") # senha

    # Enviar o formulário
    password_field.send_keys(Keys.RETURN)

    # print(driver.find_element(By.CLASS_NAME, "mt-2").text)

    # Verificar se o login foi bem-sucedido
    assert "Bem-vindo(a), Robson!" in driver.find_element(By.CLASS_NAME, "mt-2").text # mensagem de boas-vindas
    print("Teste 1/1 - OK")

    print("Teste H18 concluído com sucesso!")

    # Fechar o navegador
    driver.quit()

if __name__ == "__main__":
    print("Iniciando o teste H18...")
    test_h18_login_with_saved_data()