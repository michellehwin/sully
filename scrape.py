from bs4 import BeautifulSoup
import urllib.request
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin

# Initialize Firestore DB
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# city = input("Enter City:\n")
# state = input("Enter State:\n")
city = "Dallas"
state = "TX"
url = "https://www.yelp.com/search?find_desc=locally+owned+restaurants&find_loc=" + \
    city + "%2C" + state
ourUrl = urllib.request.urlopen(url)
soup = BeautifulSoup(ourUrl, 'html.parser')
localBusinesses = []
for i in soup.find_all('div', {'class': 'lemon--div__373c0__1mboc container__373c0__3HMKB hoverable__373c0__VqkG7 margin-t3__373c0__1l90z margin-b3__373c0__q1DuY padding-t3__373c0__1gw9E padding-r3__373c0__57InZ padding-b3__373c0__342DA padding-l3__373c0__1scQ0 border--top__373c0__3gXLy border--right__373c0__1n3Iv border--bottom__373c0__3qNtD border--left__373c0__d1B7K border-color--default__373c0__3-ifU'}):
    name = str(i.find('a', {
                  'class': "lemon--a__373c0__IEZFH link__373c0__1G70M link-color--inherit__373c0__3dzpk link-size--inherit__373c0__1VFlE"}))
    name = name.split("target=", 1)[1][3:-4]
    name = name.replace('&amp;', '&')
    doc_ref = db.collection('cities').document(
        city).collection('Food').document(name)
    # print(name)
    contact = str(i.find('p', {
                     'class':'lemon--p__373c0__3Qnnj text__373c0__2Kxyz text-color--black-extra-light__373c0__2OyzO text-align--right__373c0__1f0KI text-size--small__373c0__3NVWO'}))
    if (contact == None or len(contact) != 178):
        contact = ""
    else:
        contact = contact.split("text-size--small__373c0__3NVWO",1)[1][2:-4]
    # print(contact)
    address = str(i.find(
        'span', {"class": "lemon--span__373c0__3997G raw__373c0__3rcx7"}))
    address = address.split("3rcx7", 1)[1][2:-7]
    business = {"name": name, "contact": contact, "address": address}
    # doc_ref.set({
    #     'name' : name,
    #     'address' : address,
    #     'contact' : contact
    # })
    localBusinesses.append(business)
print(len(localBusinesses))
