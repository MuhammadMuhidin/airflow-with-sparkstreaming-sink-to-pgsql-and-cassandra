import requests

class RandomUser:
    def __init__(self):
        self.data = self.get_data()
        
    def get_data(self):
        """Mengambil data dari API RandomUser dan mengembalikan sebagai JSON."""
        res = requests.get("https://randomuser.me/api/")
        res = res.json()
        return res['results'][0]

    def format_data(self):
        """Memformat data yang diambil dari API menjadi dictionary yang lebih mudah dibaca."""
        data = {}
        res = self.data
        
        # Mengisi data ke dictionary
        data['gender'] = res['gender']
        data['title'] = res['name']['title']
        data['first_name'] = res['name']['first']
        data['last_name'] = res['name']['last']
        data['street_number'] = res['location']['street']['number']
        data['street_name'] = res['location']['street']['name']
        data['city'] = res['location']['city']
        data['state'] = res['location']['state']
        data['country'] = res['location']['country']
        data['postcode'] = res['location']['postcode']
        data['latitude'] = res['location']['coordinates']['latitude']
        data['longitude'] = res['location']['coordinates']['longitude']
        data['timezone_offset'] = res['location']['timezone']['offset']
        data['timezone_description'] = res['location']['timezone']['description']
        data['email'] = res['email']
        data['uuid'] = res['login']['uuid']
        data['username'] = res['login']['username']
        data['password'] = res['login']['password']
        data['dob_date'] = res['dob']['date']
        data['dob_age'] = res['dob']['age']
        data['registered_date'] = res['registered']['date']
        data['registered_age'] = res['registered']['age']
        data['phone'] = res['phone']
        data['cell'] = res['cell']
        data['id_name'] = res['id']['name']
        data['id_value'] = res['id']['value']
        data['picture_large'] = res['picture']['large']
        data['picture_medium'] = res['picture']['medium']
        data['picture_thumbnail'] = res['picture']['thumbnail']
        data['nationality'] = res['nat']
        
        return data

if __name__ == "__main__":
    user = RandomUser()
    data = user.format_data()
    print(data)