import pytest
import requests
import random
import json
from typing import Dict, Any, List

class TestAdvertisementAPI:
    BASE_URL = "https://qa-internship.avito.com"
    
    def generate_seller_id(self) -> int:
        """Генерация seller_id в диапазоне 111111-999999"""
        return random.randint(111111, 999999)
    
    def create_advertisement_data(self, seller_id: int = None) -> Dict[str, Any]:
        """Создание тестовых данных для объявления"""
        if seller_id is None:
            seller_id = self.generate_seller_id()
            
        return {
            "sellerID": seller_id,
            "name": f"Test Item {random.randint(1000, 9999)}",
            "price": random.randint(100, 10000),
            "statistics": {
                "likes": random.randint(0, 100),
                "viewCount": random.randint(0, 1000),
                "contacts": random.randint(0, 50)
            }
        }
    
    def test_create_advertisement_success(self):
        """TC001: Успешное создание объявления с валидными данными"""
        data = self.create_advertisement_data()
        
        response = requests.post(f"{self.BASE_URL}/api/1/item", json=data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        response_data = response.json()
        
        # Проверяем обязательные поля в ответе
        assert "id" in response_data, "id not found in response"
        assert "sellerId" in response_data, "sellerId not found in response"
        assert "name" in response_data, "name not found in response"
        assert "price" in response_data, "price not found in response"
        assert "createdAt" in response_data, "createdAt not found in response"
        assert "statistics" in response_data, "statistics not found in response"
        
        # Проверяем структуру statistics
        stats = response_data["statistics"]
        assert "likes" in stats, "likes not found in statistics"
        assert "viewCount" in stats, "viewCount not found in statistics"
        assert "contacts" in stats, "contacts not found in statistics"
        
        # Проверяем соответствие данных
        assert response_data["sellerId"] == data["sellerID"]
        assert response_data["name"] == data["name"]
        assert response_data["price"] == data["price"]
        
        return response_data["id"], data["sellerID"]
    
    def test_create_advertisement_missing_required_fields(self):
        """TC002: Создание объявления без обязательных полей"""
        # Отправляем без поля statistics
        data = {
            "sellerID": self.generate_seller_id(),
            "name": "Test Item",
            "price": 1000
            # statistics отсутствует
        }
        
        response = requests.post(f"{self.BASE_URL}/api/1/item", json=data)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
        
        # Проверяем структуру ошибки
        error_data = response.json()
        assert "result" in error_data, "result not found in error response"
        assert "status" in error_data, "status not found in error response"
    
    def test_create_advertisement_invalid_data_types(self):
        """TC003: Создание объявления с невалидными типами данных"""
        data = {
            "sellerID": "invalid_string",  # Должно быть integer
            "name": "Test Item",
            "price": 1000,
            "statistics": {
                "likes": 10,
                "viewCount": 100,
                "contacts": 5
            }
        }
        
        response = requests.post(f"{self.BASE_URL}/api/1/item", json=data)
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
    
    def test_get_advertisement_by_id_success(self):
        """TC004: Успешное получение существующего объявления"""
        # Сначала создаем объявление
        item_id, seller_id = self.test_create_advertisement_success()
        
        # Получаем объявление по ID
        response = requests.get(f"{self.BASE_URL}/api/1/item/{item_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        response_data = response.json()
        
        # Проверяем, что ответ - массив
        assert isinstance(response_data, list), f"Expected list, got {type(response_data)}"
        assert len(response_data) > 0, "Empty response array"
        
        # Проверяем первый элемент массива
        item = response_data[0]
        assert item["id"] == item_id
        assert "sellerId" in item
        assert "name" in item
        assert "price" in item
        assert "createdAt" in item
        assert "statistics" in item
    
    def test_get_nonexistent_advertisement(self):
        """TC005: Получение несуществующего объявления"""
        non_existent_id = "nonexistent123"
        
        response = requests.get(f"{self.BASE_URL}/api/1/item/{non_existent_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.text}"
        
        error_data = response.json()
        assert "result" in error_data, "result not found in error response"
        assert "status" in error_data, "status not found in error response"
    
    def test_get_advertisement_invalid_id(self):
        """TC006: Получение объявления с невалидным ID форматом"""
        # Тестируем с очень длинным ID
        invalid_id = "a" * 1000
        
        response = requests.get(f"{self.BASE_URL}/api/1/item/{invalid_id}")
        
        # Может вернуть 400 или 404 в зависимости от реализации
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}. Response: {response.text}"
    
    def test_get_seller_advertisements_success(self):
        """TC007: Успешное получение объявлений существующего продавца"""
        seller_id = self.generate_seller_id()
        
        # Создаем несколько объявлений для одного продавца
        created_items = []
        for _ in range(2):
            data = self.create_advertisement_data(seller_id)
            response = requests.post(f"{self.BASE_URL}/api/1/item", json=data)
            if response.status_code == 200:
                created_items.append(response.json()["id"])
        
        # Получаем все объявления продавца
        response = requests.get(f"{self.BASE_URL}/api/1/{seller_id}/item")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        response_data = response.json()
        
        assert isinstance(response_data, list), f"Expected list, got {type(response_data)}"
        
        # Проверяем, что все возвращенные объявления принадлежат указанному продавцу
        for item in response_data:
            assert item["sellerId"] == seller_id, f"Item {item['id']} has wrong sellerId"
    
    def test_get_nonexistent_seller_advertisements(self):
        """TC008: Получение объявлений несуществующего продавца"""
        non_existent_seller_id = 888888  # Предполагаем, что такого нет
        
        response = requests.get(f"{self.BASE_URL}/api/1/{non_existent_seller_id}/item")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        response_data = response.json()
        
        assert isinstance(response_data, list), f"Expected list, got {type(response_data)}"
        assert len(response_data) == 0, "Expected empty list for non-existent seller"
    
    def test_get_seller_advertisements_invalid_id(self):
        """TC009: Получение объявлений с невалидным sellerID"""
        invalid_seller_id = "invalid_seller"
        
        response = requests.get(f"{self.BASE_URL}/api/1/{invalid_seller_id}/item")
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}. Response: {response.text}"
    
    def test_get_advertisement_stats_v1_success(self):
        """TC010: Успешное получение статистики существующего объявления (v1)"""
        # Сначала создаем объявление
        item_id, seller_id = self.test_create_advertisement_success()
        
        # Получаем статистику через v1
        response = requests.get(f"{self.BASE_URL}/api/1/statistic/{item_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        response_data = response.json()
        
        assert isinstance(response_data, list), f"Expected list, got {type(response_data)}"
        assert len(response_data) > 0, "Empty statistics array"
        
        # Проверяем структуру статистики
        stats = response_data[0]
        assert "likes" in stats
        assert "viewCount" in stats
        assert "contacts" in stats
    
    def test_get_advertisement_stats_v2_success(self):
        """TC011: Успешное получение статистики существующего объявления (v2)"""
        # Сначала создаем объявление
        item_id, seller_id = self.test_create_advertisement_success()
        
        # Получаем статистику через v2
        response = requests.get(f"{self.BASE_URL}/api/2/statistic/{item_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        response_data = response.json()
        
        assert isinstance(response_data, list), f"Expected list, got {type(response_data)}"
        assert len(response_data) > 0, "Empty statistics array"
        
        # Проверяем структуру статистики
        stats = response_data[0]
        assert "likes" in stats
        assert "viewCount" in stats
        assert "contacts" in stats
    
    def test_get_nonexistent_advertisement_stats(self):
        """TC012: Получение статистики несуществующего объявления"""
        non_existent_id = "nonexistent123"
        
        response = requests.get(f"{self.BASE_URL}/api/1/statistic/{non_existent_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.text}"
    
    def test_delete_advertisement_success(self):
        """TC013: Успешное удаление существующего объявления"""
        # Сначала создаем объявление
        item_id, seller_id = self.test_create_advertisement_success()
        
        # Удаляем объявление
        response = requests.delete(f"{self.BASE_URL}/api/2/item/{item_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
        
        # Пытаемся получить удаленное объявление
        get_response = requests.get(f"{self.BASE_URL}/api/1/item/{item_id}")
        assert get_response.status_code == 404, f"Expected 404 after deletion, got {get_response.status_code}"
    
    def test_delete_nonexistent_advertisement(self):
        """TC014: Удаление несуществующего объявления"""
        non_existent_id = "nonexistent123"
        
        response = requests.delete(f"{self.BASE_URL}/api/2/item/{non_existent_id}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}. Response: {response.text}"
    
    def test_delete_advertisement_invalid_id(self):
        """TC015: Удаление объявления с невалидным ID"""
        invalid_id = "invalid_id_@#"
        
        response = requests.delete(f"{self.BASE_URL}/api/2/item/{invalid_id}")
        
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}. Response: {response.text}"
    
    def test_full_advertisement_cycle(self):
        """TC016: Полный цикл работы с объявлением"""
        # 1. Создаем объявление
        data = self.create_advertisement_data()
        create_response = requests.post(f"{self.BASE_URL}/api/1/item", json=data)
        assert create_response.status_code == 200, "Failed to create advertisement"
        created_item = create_response.json()
        item_id = created_item["id"]
        seller_id = data["sellerID"]
        
        # 2. Получаем объявление по ID
        get_response = requests.get(f"{self.BASE_URL}/api/1/item/{item_id}")
        assert get_response.status_code == 200, "Failed to get advertisement by ID"
        retrieved_items = get_response.json()
        assert len(retrieved_items) > 0, "No items returned"
        retrieved_item = retrieved_items[0]
        
        # 3. Проверяем согласованность данных
        assert retrieved_item["id"] == item_id
        assert retrieved_item["sellerId"] == seller_id
        assert retrieved_item["name"] == data["name"]
        assert retrieved_item["price"] == data["price"]
        
        # 4. Получаем статистику (v1 и v2)
        stats_v1_response = requests.get(f"{self.BASE_URL}/api/1/statistic/{item_id}")
        assert stats_v1_response.status_code == 200, "Failed to get statistics v1"
        
        stats_v2_response = requests.get(f"{self.BASE_URL}/api/2/statistic/{item_id}")
        assert stats_v2_response.status_code == 200, "Failed to get statistics v2"
        
        # 5. Получаем все объявления продавца
        seller_response = requests.get(f"{self.BASE_URL}/api/1/{seller_id}/item")
        assert seller_response.status_code == 200, "Failed to get seller advertisements"
        seller_items = seller_response.json()
        
        # Проверяем, что созданное объявление есть в списке
        seller_item_ids = [item["id"] for item in seller_items]
        assert item_id in seller_item_ids, "Created item not found in seller's list"
        
        # 6. Удаляем объявление
        delete_response = requests.delete(f"{self.BASE_URL}/api/2/item/{item_id}")
        assert delete_response.status_code == 200, "Failed to delete advertisement"
    
    def test_item_id_uniqueness(self):
        """TC017: Проверка уникальности ID создаваемых объявлений"""
        item_ids = set()
        
        # Создаем несколько объявлений
        for _ in range(3):
            data = self.create_advertisement_data()
            response = requests.post(f"{self.BASE_URL}/api/1/item", json=data)
            
            if response.status_code == 200:
                item_id = response.json()["id"]
                # Проверяем, что item_id уникален
                assert item_id not in item_ids, f"Duplicate item_id found: {item_id}"
                item_ids.add(item_id)
    
    def test_stats_consistency_between_versions(self):
        """TC018: Сравнение статистики из разных endpoint'ов"""
        # Создаем объявление
        item_id, seller_id = self.test_create_advertisement_success()
        
        # Получаем статистику через обе версии API
        stats_v1_response = requests.get(f"{self.BASE_URL}/api/1/statistic/{item_id}")
        stats_v2_response = requests.get(f"{self.BASE_URL}/api/2/statistic/{item_id}")
        
        assert stats_v1_response.status_code == 200, "v1 statistics failed"
        assert stats_v2_response.status_code == 200, "v2 statistics failed"
        
        stats_v1 = stats_v1_response.json()
        stats_v2 = stats_v2_response.json()
        
        # Проверяем, что обе версии возвращают данные
        assert len(stats_v1) > 0, "v1 statistics empty"
        assert len(stats_v2) > 0, "v2 statistics empty"
        
        # Проверяем структуру данных (значения могут отличаться из-за обновлений)
        v1_item = stats_v1[0]
        v2_item = stats_v2[0]
        
        assert "likes" in v1_item and "likes" in v2_item
        assert "viewCount" in v1_item and "viewCount" in v2_item
        assert "contacts" in v1_item and "contacts" in v2_item

if __name__ == "__main__":
    pytest.main([__file__, "-v"])