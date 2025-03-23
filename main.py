import requests
import time
import os
import json


class ProxySellerAPI:
    def __init__(self):
        self.api_key = self.load_api_key()
        self.base_url = f'https://proxy-seller.com/personal/api/v1/{self.api_key}/resident'
        self.output_file = "proxy_list.txt"
        self.previous_countries_file = "previous_countries.json"

    def load_api_key(self):
        # Try to load API key from file
        try:
            if os.path.exists("api_key.txt"):
                with open("api_key.txt", "r") as file:
                    return file.read().strip()
        except:
            pass

        # If file doesn't exist or there was an error, ask the user
        api_key = input("Введите ваш API-ключ для ProxySeller: ")

        # Save the API key for future use
        with open("api_key.txt", "w") as file:
            file.write(api_key)

        return api_key

    def get_lists(self):
        """Get all existing IP lists"""
        url = f'{self.base_url}/lists'

        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                if data.get("status") == "success":
                    # Based on the debug output, data itself contains the lists
                    if isinstance(data.get("data"), list):
                        return data["data"]
                    # Or it might be nested under 'items' as in the documentation
                    elif isinstance(data.get("data"), dict) and "items" in data["data"]:
                        return data["data"]["items"]
                    else:
                        print("Ошибка: Неожиданная структура данных в ответе.")
                        print("Структура ответа:", data)
                        return []
                else:
                    print("Ошибка: Некорректный формат ответа сервера.")
                    if "errors" in data and data["errors"]:
                        print("Сообщение об ошибке:", data["errors"])
            else:
                print(f'Ошибка при получении списка. Код ошибки: {response.status_code}')
                print('Ответ сервера:', response.text)
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")

        return []

    def display_lists(self, lists):
        """Display lists in a simple, comfortable format"""
        if not lists:
            print("Списков прокси не найдено или произошла ошибка при их получении.")
            return

        print("\n=== Доступные списки прокси ===")

        for i, item in enumerate(lists, 1):
            try:
                list_id = item.get('id', 'N/A')
                title = item.get('title', 'Без названия')

                # Handle geo information - showing all countries
                countries = []
                if 'geo' in item:
                    geo_info = item['geo']
                    # Check if geo is a list of country objects
                    if isinstance(geo_info, list):
                        for geo in geo_info:
                            if isinstance(geo, dict) and 'country' in geo:
                                countries.append(geo['country'])
                    # Or if it's a single country object
                    elif isinstance(geo_info, dict) and 'country' in geo_info:
                        countries.append(geo_info['country'])

                # Format the countries list
                countries_str = ", ".join(countries) if countries else 'N/A'

                print(f"{i}. ID: {list_id} - {title} - Страны: {countries_str}")
            except Exception as e:
                print(f"Ошибка при отображении элемента списка: {str(e)}")
                # Print item structure for debugging
                print(f"Структура элемента: {type(item)}")
                if isinstance(item, dict):
                    print(f"Ключи элемента: {item.keys()}")

        print("=" * 30)

        # Return the lists for use in other functions
        return lists

    def load_previous_countries(self):
        """Load previously used countries from a file"""
        if os.path.exists(self.previous_countries_file):
            try:
                with open(self.previous_countries_file, "r") as file:
                    return json.load(file)
            except Exception as e:
                print(f"Ошибка при загрузке предыдущих стран: {str(e)}")
        return {}

    def save_previous_countries(self, country, region="", city="", isp=""):
        """Save used countries to a file"""
        countries_data = self.load_previous_countries()

        countries_data[country] = {
            "region": region,
            "city": city,
            "isp": isp,
            "last_used": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            with open(self.previous_countries_file, "w") as file:
                json.dump(countries_data, file, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении предыдущих стран: {str(e)}")

    def create_lists(self):
        """Create one or multiple new IP lists"""
        print("\n=== Создание нового списка прокси ===")
        title = input("Введите название списка: ")

        # Ask how many lists to create
        try:
            num_lists = int(input("Сколько списков вы хотите создать (для получения более 1000 прокси)? [1]: ") or "1")
            if num_lists < 1:
                num_lists = 1
                print("Количество списков должно быть как минимум 1.")
        except ValueError:
            num_lists = 1
            print("Ошибка ввода. Установлено значение по умолчанию: 1 список.")

        # Load previously used countries
        previous_countries = self.load_previous_countries()

        # If there are previously used countries, ask if the user wants to use them
        use_previous = False
        if previous_countries:
            print("\nРанее использованные страны:")
            for i, (country, data) in enumerate(previous_countries.items(), 1):
                print(f"{i}. {country} (Последнее использование: {data.get('last_used', 'N/A')})")

            choice = input("\nИспользовать одну из предыдущих стран? (y/n, или номер страны): ")

            if choice.lower() == 'y' and previous_countries:
                # Use the most recently used country
                newest_country = max(previous_countries.items(), key=lambda x: x[1].get('last_used', ''))
                country = newest_country[0]
                region = newest_country[1].get('region', '')
                city = newest_country[1].get('city', '')
                isp = newest_country[1].get('isp', '')
                use_previous = True
                print(f"Используется страна: {country}")
            elif choice.isdigit() and 1 <= int(choice) <= len(previous_countries):
                # Use the selected country
                selected_country = list(previous_countries.items())[int(choice) - 1]
                country = selected_country[0]
                region = selected_country[1].get('region', '')
                city = selected_country[1].get('city', '')
                isp = selected_country[1].get('isp', '')
                use_previous = True
                print(f"Используется страна: {country}")

        if not use_previous:
            # Получаем данные о гео
            print("\nВыберите страну (доступные: US, GB, CA, DE, FR, NL, etc.)")
            country = input("Введите код страны (несколько стран вводятся без пробела!): ").upper()
            region = input("Введите регион (или оставьте пустым): ")
            city = input("Введите город (или оставьте пустым): ")
            isp = input("Введите провайдера (или оставьте пустым): ")

            # Save the country for future use
            self.save_previous_countries(country, region, city, isp)

        # Получаем информацию о портах
        try:
            num_ports = int(input("Введите количество портов на список (максимум 1000): ") or "1000")
            if num_ports > 1000:
                num_ports = 1000
                print("Максимальное количество портов ограничено до 1000.")
        except ValueError:
            num_ports = 1000
            print("Ошибка ввода. Установлено значение по умолчанию: 1000 портов.")

        # Получаем IP для белого списка
        whitelist = input("Введите IP-адреса для белого списка через запятую (или оставьте пустым): ")

        # Choose proxy format
        print("\nВыберите формат прокси:")
        print("1. login:password@host:port (default)")
        print("2. host:port@login:password")
        print("3. host:port:login:password")
        print("4. login:password:host:port")

        format_choice = input("Выберите формат [1]: ") or "1"
        proxy_format = int(format_choice) if format_choice.isdigit() and 1 <= int(format_choice) <= 4 else 1

        # Create lists
        total_proxies = 0
        all_proxy_lists = []

        for i in range(num_lists):
            list_title = title
            if num_lists > 1:
                list_title = f"{title} #{i + 1}"

            data = {
                'title': list_title,
                'whitelist': whitelist,
                'geo': {
                    'country': country,
                    'region': region,
                    'city': city,
                    'isp': isp
                },
                'ports': num_ports,
                'export': {
                    'ports': 10000,  # Начальный порт
                    'ext': 'txt'  # Формат экспорта
                }
            }

            try:
                response = requests.post(f'{self.base_url}/list/add', json=data)

                if response.status_code == 200:
                    response_data = response.json()

                    if response_data.get("status") == "success" and "data" in response_data:
                        proxy_data = response_data["data"]
                        print(f"\n=== Список прокси '{list_title}' успешно создан ===")
                        print(f"Название: {proxy_data.get('title', 'N/A')}")

                        # Generate proxy list
                        proxy_list = self.generate_proxy_list(proxy_data, num_ports, proxy_format)
                        all_proxy_lists.extend(proxy_list)
                        total_proxies += len(proxy_list)
                    else:
                        print("Ошибка: Некорректный формат ответа сервера.")
                        if "errors" in response_data and response_data["errors"]:
                            print("Сообщение об ошибке:", response_data["errors"])
                else:
                    print(f'Ошибка при создании списка. Код ошибки: {response.status_code}')
                    print('Ответ сервера:', response.text)
            except Exception as e:
                print(f"Произошла ошибка: {str(e)}")

        # Save all proxy lists to a single file
        if all_proxy_lists:
            # Create a safe filename
            safe_title = ''.join(c for c in title if c.isalnum() or c in ' _-').replace(' ', '_')
            filename = f"{safe_title}_proxies.txt"

            # Save to file
            with open(filename, "w") as file:
                file.write("\n".join(all_proxy_lists))

            print(f"\nВсего создано {total_proxies} прокси в {num_lists} списках.")
            print(f"Прокси сохранены в файл '{filename}'.")

        return total_proxies

    def generate_proxy_list(self, proxy_data, num_ports, format_type=1):
        """Generate proxy list in the specified format"""
        try:
            login = proxy_data.get("login")
            password = proxy_data.get("password")
            base_host = "res.proxy-seller.com"
            base_port = int(proxy_data.get("export", {}).get("ports", 10000))

            if login and password:
                # Generate proxy list in the specified format
                proxy_list = []

                for port in range(base_port, base_port + num_ports):
                    if format_type == 1:
                        # login:password@host:port
                        proxy = f"{login}:{password}@{base_host}:{port}"
                    elif format_type == 2:
                        # host:port@login:password
                        proxy = f"{base_host}:{port}@{login}:{password}"
                    elif format_type == 3:
                        # host:port:login:password
                        proxy = f"{base_host}:{port}:{login}:{password}"
                    elif format_type == 4:
                        # login:password:host:port
                        proxy = f"{login}:{password}:{base_host}:{port}"
                    else:
                        # Default format
                        proxy = f"{login}:{password}@{base_host}:{port}"

                    proxy_list.append(proxy)

                return proxy_list
            else:
                print("Ошибка: Не удалось получить логин и пароль из ответа сервера.")
        except Exception as e:
            print(f"Ошибка при генерации списка прокси: {str(e)}")

        return []

    def rename_list(self):
        """Rename an existing IP list"""
        # First, get all lists
        lists = self.get_lists()
        available_lists = self.display_lists(lists)

        if not available_lists:
            return

        # Ask for list selection
        try:
            selection = int(input("\nВыберите номер списка для переименования: "))

            if selection < 1 or selection > len(available_lists):
                print(f"Ошибка: выбран неверный номер списка.")
                return

            # Get the selected list
            selected_list = available_lists[selection - 1]
            list_id = selected_list.get('id')

            # Ask for new name
            new_title = input("Введите новое название для списка: ")

            # Make API request
            url = f'{self.base_url}/list/rename'
            data = {
                'id': list_id,
                'title': new_title
            }

            response = requests.post(url, json=data)

            if response.status_code == 200:
                response_data = response.json()

                if response_data.get("status") == "success":
                    print(f"Список успешно переименован в '{new_title}'.")
                else:
                    print("Ошибка: Некорректный формат ответа сервера.")
                    if "errors" in response_data and response_data["errors"]:
                        print("Сообщение об ошибке:", response_data["errors"])
            else:
                print(f'Ошибка при переименовании списка. Код ошибки: {response.status_code}')
                print('Ответ сервера:', response.text)
        except ValueError:
            print("Ошибка: Введите числовое значение.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")

    def delete_list(self):
        """Delete multiple existing IP lists"""
        # First, get all lists
        lists = self.get_lists()
        available_lists = self.display_lists(lists)

        if not available_lists:
            return

        # Ask for list selection
        try:
            selection_input = input("\nВыберите номера списков для удаления (через запятую, например: 1,3,5): ")
            selections = [int(x.strip()) for x in selection_input.split(',') if x.strip().isdigit()]

            # Validate selections
            valid_selections = []
            for selection in selections:
                if 1 <= selection <= len(available_lists):
                    valid_selections.append(selection)
                else:
                    print(f"Предупреждение: Номер {selection} вне диапазона и будет пропущен.")

            if not valid_selections:
                print("Ошибка: Не выбрано ни одного действительного списка.")
                return

            # Show selected lists
            print("\nВыбранные списки для удаления:")
            selected_lists = []
            for selection in valid_selections:
                selected_list = available_lists[selection - 1]
                list_id = selected_list.get('id')
                title = selected_list.get('title', 'Без названия')
                print(f"- {title} (ID: {list_id})")
                selected_lists.append((list_id, title))

            # Confirm deletion
            confirm = input(f"\nВы уверены, что хотите удалить {len(selected_lists)} выбранных списков? (y/n): ")
            if confirm.lower() != 'y':
                print("Операция отменена.")
                return

            # Delete each list
            deleted_count = 0
            for list_id, title in selected_lists:
                # Make API request
                url = f'{self.base_url}/list/delete'
                data = {
                    'id': list_id
                }

                try:
                    response = requests.delete(url, json=data)

                    if response.status_code == 200:
                        response_data = response.json()

                        if response_data.get("status") == "success":
                            print(f"Список '{title}' успешно удален.")
                            deleted_count += 1
                        else:
                            print(f"Ошибка при удалении списка '{title}'.")
                            if "errors" in response_data and response_data["errors"]:
                                print("Сообщение об ошибке:", response_data["errors"])
                    else:
                        print(f'Ошибка при удалении списка "{title}". Код ошибки: {response.status_code}')
                        print('Ответ сервера:', response.text)
                except Exception as e:
                    print(f"Произошла ошибка при удалении списка '{title}': {str(e)}")

            print(f"\nУдалено {deleted_count} из {len(selected_lists)} выбранных списков.")

        except ValueError:
            print("Ошибка: Неверный формат ввода.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")


def display_menu():
    """Display the main menu"""
    print("\n" + "=" * 50)
    print("       ProxySeller API Manager")
    print("=" * 50)
    print("1. Получить существующие списки IP")
    print("2. Создать новый список (или несколько)")
    print("3. Переименовать список")
    print("4. Удалить списки")
    print("0. Выход")
    print("=" * 50)
    return input("Выберите опцию: ")


def main():
    proxy_api = ProxySellerAPI()

    while True:
        choice = display_menu()

        if choice == "1":
            lists = proxy_api.get_lists()
            proxy_api.display_lists(lists)
            input("\nНажмите Enter для продолжения...")

        elif choice == "2":
            proxy_api.create_lists()
            input("\nНажмите Enter для продолжения...")

        elif choice == "3":
            proxy_api.rename_list()
            input("\nНажмите Enter для продолжения...")

        elif choice == "4":
            proxy_api.delete_list()
            input("\nНажмите Enter для продолжения...")

        elif choice == "0":
            print("\nВыход из программы...")
            break

        else:
            print("\nНеверный выбор. Пожалуйста, попробуйте снова.")


if __name__ == "__main__":
    main()