# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 13:36:54 2024

@author: emrengin
"""

import pytest
from app import app
from bs4 import BeautifulSoup  # HTML parse etmek için kütüphane

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_valid_csrf(client):
    response = client.get('/login')
    print("GET /login yanıtı: ", response.data)  # Çıktıyı görmek için
    assert response.status_code == 200

    # HTML yanıtından CSRF token'i al
    soup = BeautifulSoup(response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})['value']  # Token'i çıkar

    # Geçerli form gönderimi
    response = client.post('/login', data={
        'username': 'emre',
        'password': 's%J!u4Q7',
        'csrf_token': csrf_token
    })
    print("GET /login doğru csrf yanıtı: ", response.data)  # Çıktıyı görmek için
    assert response.status_code == 302  # Başarılı yönlendirme

def test_invalid_csrf(client):
    # Hatalı CSRF token ile form gönderimi
    response = client.post('/login', data={
        'username': 'emre',
        'password': 's%J!u4Q7',
        'csrf_token': 'gecersiz-token'
    })
    print("GET /login yanlış csrf yanıtı: ", response.data)  # Çıktıyı görmek için
    assert response.status_code == 400  # Hata kodu
