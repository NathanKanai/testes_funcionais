from selenium import webdriver # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.common.exceptions import TimeoutException, NoSuchElementException # type: ignore
import unittest
import time

class TesteFuncional(unittest.TestCase):

    def setUp(self):
        """Configura o navegador antes de cada teste"""
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        """Fecha o navegador após cada teste"""
        self.driver.quit()

    # ✅ CT-01: Login com credenciais válidas
    def test_01_login_valido(self):
        """CT-01_Login_Valido: Testa login válido em todas as plataformas"""
        plataformas = [
            {
                "nome": "SauceDemo",
                "url": "https://www.saucedemo.com",
                "usuario": "standard_user",
                "senha": "secret_sauce",
                "campo_usuario": "user-name",
                "campo_senha": "password",
                "botao_login": "login-button",
                "elemento_sucesso": "inventory_container"
            },
            {
                "nome": "TheInternet",
                "url": "https://the-internet.herokuapp.com/login",
                "usuario": "tomsmith",
                "senha": "SuperSecretPassword!",
                "campo_usuario": "username",
                "campo_senha": "password",
                "botao_login": "login",
                "elemento_sucesso": "secure"
            },
            {
                "nome": "PracticeTestAutomation",
                "url": "https://practicetestautomation.com/practice-test-login/",
                "usuario": "student",
                "senha": "Password123",
                "campo_usuario": "username",
                "campo_senha": "password",
                "botao_login": "submit",
                "elemento_sucesso": "post-title"
            },
            {
                "nome": "OrangeHRM",
                "url": "https://opensource-demo.orangehrmlive.com/",
                "usuario": "Admin",
                "senha": "admin123",
                "campo_usuario": "username",
                "campo_senha": "password",
                "botao_login": "oxd-login-button",
                "elemento_sucesso": "dashboard"
            }
        ]

        for plat in plataformas:
            with self.subTest(plataforma=plat["nome"]):
                self.driver.get(plat["url"])
                try:
                    # Preencher login
                    self.driver.find_element(By.ID, plat["campo_usuario"]).send_keys(plat["usuario"])
                    self.driver.find_element(By.ID, plat["campo_senha"]).send_keys(plat["senha"])
                    self.driver.find_element(By.CLASS_NAME if "oxd" in plat["botao_login"] else By.ID, plat["botao_login"]).click()

                    # Verificar sucesso
                    self.wait.until(EC.presence_of_element_located((By.XPATH, f"//*[contains(@class, '{plat['elemento_sucesso']}') or contains(text(), '{plat['elemento_sucesso']}')]")))
                    print(f"✅ CT-01_Login_Valido - {plat['nome']}: PASSOU")
                except TimeoutException:
                    self.fail(f"❌ CT-01_Login_Valido - {plat['nome']}: FALHOU")

    # ✅ CT-02: Logout funcional
    def test_02_logout_funcional(self):
        """CT-02_Logout_Funcional: Testa logout após login"""
        self._login_saucedemo()
        try:
            self.driver.find_element(By.ID, "react-burger-menu-btn").click()
            time.sleep(1)
            logout_link = self.wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
            logout_link.click()
            self.wait.until(EC.url_to_be("https://www.saucedemo.com/"))
            self.assertTrue(self.driver.find_element(By.ID, "login-button").is_displayed())
            print("✅ CT-02_Logout_Funcional: PASSOU")
        except Exception as e:
            self.fail(f"❌ CT-02_Logout_Funcional: FALHOU - {str(e)}")

    def _login_saucedemo(self):
        """Login auxiliar no SauceDemo"""
        self.driver.get("https://www.saucedemo.com")
        self.driver.find_element(By.ID, "user-name").send_keys("standard_user")
        self.driver.find_element(By.ID, "password").send_keys("secret_sauce")
        self.driver.find_element(By.ID, "login-button").click()
        self.wait.until(EC.url_contains("inventory"))

    # ✅ CT-03: Login com entrada inválida (senha errada)
    def test_03_entrada_invalida(self):
        """CT-03_Entrada_Invalida: Testa login com senha incorreta"""
        self.driver.get("https://www.saucedemo.com")
        self.driver.find_element(By.ID, "user-name").send_keys("standard_user")
        self.driver.find_element(By.ID, "password").send_keys("senha_errada")
        self.driver.find_element(By.ID, "login-button").click()

        try:
            erro = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h3[@data-test='error']")))
            self.assertIn("username and password do not match", erro.text.lower())
            print("✅ CT-03_Entrada_Invalida: PASSOU")
        except TimeoutException:
            self.fail("❌ CT-03_Entrada_Invalida: FALHOU - Mensagem de erro não apareceu")

    # ✅ CT-04: Login com campos vazios
    def test_04_campos_vazios(self):
        """CT-04_Campos_Vazios: Testa login com campos vazios"""
        self.driver.get("https://www.saucedemo.com")
        self.driver.find_element(By.ID, "login-button").click()

        try:
            erro_usuario = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//*[text()='Username is required']")))
            erro_senha = self.driver.find_element(By.XPATH, "//*[text()='Password is required']")
            self.assertTrue(erro_usuario.is_displayed() and erro_senha.is_displayed())
            print("✅ CT-04_Campos_Vazios: PASSOU")
        except TimeoutException:
            self.fail("❌ CT-04_Campos_Vazios: FALHOU - Validação não funcionou")

    # ✅ CT-05: Filtros no SauceDemo
    def test_05_filtros_saucedemo(self):
        """CT-05_Filtros_SauceDemo: Testa ordenação por nome e preço"""
        self._login_saucedemo()
        try:
            # Filtro A-Z
            filtro = self.driver.find_element(By.CLASS_NAME, "product_sort_container")
            filtro.click()
            self.driver.find_element(By.XPATH, "//option[text()='Name (A to Z)']").click()
            time.sleep(1)
            primeiro = self.driver.find_element(By.XPATH, "//div[@class='inventory_item_name']").text
            self.assertEqual(primeiro, "Sauce Labs Backpack", "Ordenação A-Z falhou")

            # Filtro por preço (Low to High)
            filtro.click()
            self.driver.find_element(By.XPATH, "//option[text()='Price (low to high)']").click()
            time.sleep(1)
            precos = [float(p.text.replace("$", "")) for p in self.driver.find_elements(By.CLASS_NAME, "inventory_item_price")]
            self.assertEqual(precos, sorted(precos), "Ordenação por preço falhou")

            print("✅ CT-05_Filtros_SauceDemo: PASSOU")
        except Exception as e:
            self.fail(f"❌ CT-05_Filtros_SauceDemo: FALHOU - {str(e)}")

    # ✅ CT-06: Adicionar ao carrinho
    def test_06_add_to_cart(self):
        """CT-06_Add_To_Cart: Adiciona produto ao carrinho"""
        self._login_saucedemo()
        try:
            self.driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
            carrinho = self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "shopping_cart_badge")))
            self.assertEqual(carrinho.text, "1")
            botao = self.driver.find_element(By.ID, "remove-sauce-labs-backpack").text
            self.assertEqual(botao, "Remove")
            print("✅ CT-06_Add_To_Cart: PASSOU")
        except Exception as e:
            self.fail(f"❌ CT-06_Add_To_Cart: FALHOU - {str(e)}")


# Executar os testes
if __name__ == "__main__":
    unittest.main(verbosity=2)