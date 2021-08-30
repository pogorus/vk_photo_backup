import requests
from datetime import datetime
import sys
import json

class VkPhoto:
    def __init__(self, likes: int, date: str, size: str, url: str):
        self.likes = likes
        self.date = date
        self.size = size
        self.url = url

class VkDownloader:
    base_url = 'https://api.vk.com/method/'
    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_photo(self, id, count = '5'):
        get_photo_url = self.base_url + 'photos.get'
        get_photo_params = {
            'album_id': 'profile',
            'extended': '1',
            'photo_sizes': '1',
            'count': count,
            'owner_id': id
        }
        response = requests.get(get_photo_url, params={**self.params, **get_photo_params}).json()

        photo_list = []
        for photo in response['response']['items']:
            sizes_dict = {}
            largest_photo_type = ''
            largest_photo_url = ''
            for size in photo['sizes']:
                sizes_dict[size['type']] = size['url']
            for type in 'wzyxms':
                if type in list(sizes_dict.keys()):
                    largest_photo_type = type
                    largest_photo_url = sizes_dict[type]
                    break
            photo_list.append(VkPhoto(photo['likes']['count'], photo['date'], largest_photo_type, largest_photo_url))
        return photo_list

class YaUploader:
    base_url = 'https://cloud-api.yandex.net:443/'
    def __init__(self, token: str, folder_name: str):
        self.token = token
        self.folder_name = folder_name

    def updt(self, total, progress):

        barLength, status = 20, ""
        progress = float(progress) / float(total)
        if progress >= 1.:
            progress, status = 1, "\r\n"
        block = int(round(barLength * progress))
        text = "\r[{}] {:.0f}% {}".format(
            "#" * block + "-" * (barLength - block), round(progress * 100, 0),
            status)
        sys.stdout.write(text)
        sys.stdout.flush()

    def upload(self, files: list):
        headers = {
            'accept': 'application/json',
            'authorization': f'OAuth {self.token}'
        }

        requests.put(self.base_url + 'v1/disk/resources', params={'path': self.folder_name}, headers=headers)

        photo_names = []
        count = 0
        for file in files:
            if str(file.likes) in photo_names:
                file_name = str(file.likes) + '-' + datetime.fromtimestamp(file.date).strftime('%Y-%m-%d')
                photo_names.append(file_name)
            else:
                file_name = str(file.likes)
                photo_names.append(file_name)
            requests.post(self.base_url + 'v1/disk/resources/upload', params={'path': self.folder_name + '/' + file_name, 'url': file.url}, headers=headers)
            count += 1
            self.updt(len(files), count)

vk_token = input('Введите токен VK: ')
ya_token = input('Введите токен Yandex: ')
vk_id = input('Введите ID пользователя VK: ')

vk_photo = VkDownloader(vk_token, '5.131')

photos = vk_photo.get_photo(vk_id)

uploader = YaUploader(ya_token, vk_id)
uploader.upload(photos)

data = []
for photo in photos:
    data.append({'file_name': str(photo.likes) + '.jpg', 'size': str(photo.size)})
with open('photos.json', 'w') as f:
    json.dump(data, f, indent=2)

