import os
import random
import time

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_url(region: str = 'br', tier='all'):
    return f'https://op.gg/pt/lol/statistics/champions?region={region}&tier={tier}'

region = 'br'
tiers = ('iron', 'bronze', 'silver', 'gold', 'platinum', 'emerald', 'diamond', 'master', 'grandmaster', 'challenger')

def get_champions(driver, region: str = 'global', tier: str = 'all', max_retries=5):
    delay = 5
    retries = 0

    url = f"https://op.gg/lol/statistics/champions?region={region}&tier={tier}"

    time.sleep(delay)
    driver.get(url)

    while retries < max_retries:
        try:
            # Espera tabela carregar
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "main table tbody tr"))
            )

            champions = []
            rows = driver.find_elements(By.CSS_SELECTOR, "main table tbody tr")
            for row in rows:
                try:
                    cols = row.find_elements(By.CSS_SELECTOR, "td")

                    champion = {
                        "nome": cols[1].text.strip(),
                        "jogos_jogados": cols[2].text.strip(),
                        "ama": cols[3].text.strip(),
                        "taxa_vitoria": cols[4].text.strip(),
                        "taxa_escolha": cols[5].text.strip(),
                        "taxa_banimento": cols[6].text.strip(),
                        "cs": cols[7].text.strip(),
                        "ouro": cols[8].text.strip(),
                        'region': region,
                        'tier': tier
                    }

                    champions.append(champion)
                except Exception:
                    print(f"Erro ao processar linha: {row.text}")
                    continue

            return champions

        except Exception as e:
            print(f"Tentativa {retries+1} falhou: {e}")
            retries += 1
            delay *= 2
            delay += random.uniform(0, 1)

    print(f"Falha ao obter campeões após {max_retries} tentativas.")
    return []

def get_champions_by_tier(driver, tier: str):
    champions = get_champions(driver, region, tier)

    df = pd.DataFrame(champions)
    if os.path.exists('champions.csv'):
        df.to_csv('champions.csv', mode='a', header=False, index=False, sep=';')
    else:
        df.to_csv('champions.csv', index=False, sep=';')

    print(f"Dados do tier '{tier}' salvos em 'champions.csv'")

def get_all_champions():
    options = webdriver.EdgeOptions()
    # options.add_argument('--headless')

    driver = webdriver.Edge(options=options)
    driver.maximize_window()

    for tier in tiers:
        get_champions_by_tier(driver, tier)

    driver.quit()

get_all_champions()
