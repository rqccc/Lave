import uuid
import requests
import time
import os
from PIL import Image
import io
from tkinter import Tk, filedialog
import string
import random


def gen(n):
    name = ""
    while True:
        n, r = divmod(n, 26)
        name = chr(ord('a') + r) + name
        if n == 0:
            break
        n -= 1
    return name



def open_image_prompt():
    root = Tk()
    root.withdraw()

    return filedialog.askopenfilename(
        title="Select Gamepass Image",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")]
    )


def binary(path):
    img = Image.open(path).convert("L")
    bw = img.point(lambda x: 255 if x > 128 else 0)
    
    buf = io.BytesIO()
    bw.save(buf, format="PNG")
    buf.seek(0)
    return buf



class Roblox:
    def __init__(self, cookie):
        self.session = requests.Session()
        self.session.cookies.update({".ROBLOSECURITY": cookie})

        csrf = self.session.post("https://auth.roblox.com/v2/logout")
        csrf_token = csrf.headers.get("X-CSRF-TOKEN")
        if csrf_token:
            self.session.headers.update({"X-CSRF-TOKEN": csrf_token})
        else:
            raise Exception(f"Lave | Invalid cookie | {csrf.json()}")
        
        response = self.session.get("https://users.roblox.com/v1/users/authenticated")
        if response.status_code == 200:
            self.userid = response.json()["id"]
        else:
            raise Exception(f"Roblox.GetOwner | Failed to retrieve id | {response.json()}")

    def Unfriend(self, id):
        while True:
            response = self.session.post(f"https://friends.roblox.com/v1/users/{id}/unfriend")
            if response.status_code == 200:
                print(f"Roblox.Unfriend | {id}")
                break
            else:
                print("Roblox.Unfriend | Rate limited. Retrying in 60s")
                time.sleep(60)

    def GetFriends(self, id):
        response = self.session.get(f"https://friends.roblox.com/v1/users/{id}/friends")
        json = response.json()

        if response.status_code == 200:
            compile = []

            for user in json.get("data"):
                compile.append(user.get("id"))

            return compile
        else:
            print("Roblox.GetFriends | Rate limited. Retrying in 60s")

    def GetBadges(self, id):
        badges = []
        cursor = ""

        while True:
            response = self.session.get(
                f"https://badges.roblox.com/v1/users/{id}/badges",
                params={"limit": 100, "cursor": cursor}
            )

            json = response.json()
            if response.status_code == 200:
                badges.extend(json["data"])
                cursor = json.get("nextPageCursor", "")
                if not cursor:
                    break
            else:
                raise Exception("Roblox.GetBadges | Rate limited. Retrying in 60s")

        return badges

    def DeleteBadge(self, id):
        while True:
            response = self.session.delete(f"https://badges.roblox.com/v1/user/badges/{id}")
            if response.status_code == 200:
                print(f"Roblox.DeleteBadge | {id}")
                break
            else:
                print("Roblox.DeleteBadge | Rate limited. Retrying in 60s")
                time.sleep(60)

    def GetFollowing(self, id):
        following = []
        cursor = ""

        while True:
            response = self.session.get(
                f"https://friends.roblox.com/v1/users/{id}/followings",
                params={"limit": 100, "cursor": cursor}
            )

            json = response.json()
            if response.status_code == 200:
                following.extend(item.get("id") for item in json["data"])
                cursor = json.get("nextPageCursor", "")
                if not cursor:
                    break
            else:
                raise Exception("Roblox.GetFollowing | Rate limited. Retrying in 60s")

        return following

    def Unfollow(self, id):
        while True:
            response = self.session.post(f"https://friends.roblox.com/v1/users/{id}/unfollow")
            if response.status_code == 200:
                print(f"Roblox.Unfollow | {id}")
                break
            else:
                print("Roblox.Unfollow | Rate limited. Retrying in 60s")
                time.sleep(60)
    
    def GetGames(self, id):
        games = []
        cursor = ""

        while True:
            response = self.session.get(
                f"https://games.roblox.com/v2/users/{id}/games",
                params={"limit": 50, "cursor": cursor}
            )

            json = response.json()
            if response.status_code == 200:
                games.extend(json["data"])
                cursor = json.get("nextPageCursor", "")
                if not cursor:
                    break
            else:
                raise Exception("Roblox.GetGames | Rate limited. Retrying in 60s")

        return games
    
    def PrivateGame(self, id):
        while True:
            response = self.session.post(f"https://develop.roblox.com/v1/universes/{id}/deactivate")
            if response.status_code == 200:
                print(f"Roblox.PrivateGame | {id}")
                break
            else:
                print("Roblox.PrivateGame | Rate limited. Retrying in 60s")
                time.sleep(20)
    
    def FetchItems(self):
        items = []
        cursor = ""

        while cursor is not None:
            response = self.session.get(
                f"https://catalog.roblox.com/v2/search/items/details",
                params={"salesTypeFilter": 1, "creatorName": "Roblox", "minPrice": 0, "maxPrice": 0, "limit": 120, "cursor": cursor}
            )

            json = response.json()
            if response.status_code == 200:
                for item in json.get("data", []):
                    items.append(item)
                    name = item.get("name")
                    print(f"Roblox.FetchItems | {name}")
                
                cursor = json.get("nextPageCursor")
            else:
                print("Roblox.FetchItems | Rate limited. Retrying in 60s")
                time.sleep(60)

        return items
    
    def GetProductId(self, id, isBundle):
        while True:
            link = ""
            if isBundle:
                link = f"https://catalog.roblox.com/v1/bundles/{id}/details"
            else:
                link = f"https://economy.roblox.com/v2/assets/{id}/details"
            
            req = self.session.get(link)
            js = req.json()
            if req.status_code == 200:
                found = js.get("CollectibleProductId")
                if found:
                    return found
                
                found = js.get("collectibleItemDetail").get("collectibleProductId")
                if found:
                    return found
                
                break
            else:
                print("Roblox.GetProductId | Rate limited. Retrying in 60s")
                time.sleep(60)
    
    def PurchaseItem(self, item):
        id = item["id"]
        itemid = item["collectibleItemId"]
        name = item["name"]
        isbundle = item["itemType"] == "Bundle"
        pid = self.GetProductId(id, isbundle)
        
        while True:
            req = self.session.post(
                f"https://apis.roblox.com/marketplace-sales/v1/item/{itemid}/purchase-item",
                json={"expectedCurrency": 1, "expectedPrice": 0, "expectedSellerId": 1, "expectedPurchaserType": "User", "expectedSellerType": "User", "expectedPurchaserId": self.userid, "collectibleItemId": itemid, "collectibleProductId": pid, "idempotencyKey": str(uuid.uuid4())}
            )
            
            res = req.json()
            if req.status_code == 429:
                print("Roblox.PurchaseItem | Rate limited. Retrying in 60s")
                time.sleep(60)
                continue

            if "purchaseResult" in res and res.get("purchaseResult") == "Purchase transaction is failed.":
                print(f"Roblox.PurchaseItem | {name} is already owned")
                return
               
            print(f"Roblox.PurchaseItem | Successfully purchased {name}")
            return

    def GetConversations(self):
        convo = []
        cursor = ""
        while True:
            response = self.session.get("https://apis.roblox.com/platform-chat-api/v1/get-user-conversations", params={
                "include_user_data": True,
                "pageSize": 20,
                "cursor": cursor
            })

            js = response.json()
            if response.status_code == 200:
                convo.extend(js["conversations"])
                cursor = js.get("next_cursor")
                if not cursor:
                    break
            else:
                print(f"Roblox.GetConversations | Rate limited | {js}")
                time.sleep(60)

        return convo

    def CreateConversation(self, id):
        while True:
            response = self.session.post("https://apis.roblox.com/platform-chat-api/v1/create-conversations", json={
                "conversations": [
                    {
                        "type": "one_to_one",
                        "participant_user_ids": [id]
                    }
                ],
                "include_user_data": True
            })
            
            if response.status_code == 200:
                return js["conversations"]
            else:
                print("Roblox.CreateConversation | Rate limited. Retrying in 60s")
                time.sleep(60)
    
    def SendMessage(self, id, message):
        while True:
            response = self.session.post("https://apis.roblox.com/platform-chat-api/v1/send-messages", json={
                "conversation_id": id,
                "messages": [
                    {"content": message}
                ]
            })

            if response.status_code == 200:
                print(f"Roblox.SendMessage | Messaged {id}")
                return
            else:
                print("Roblox.SendMessage | Rate limited. Retrying in 60s")
                time.sleep(60)
    
    def CreateGamepass(self, name, description, universe_id, image_path):
        image = binary(image_path)

        while True:
            response = self.session.post("https://apis.roblox.com/game-passes/v1/game-passes",
                data={
                    "name": name,
                    "description": description,
                    "universeId": universe_id
                },
                files={
                    "file": ("icon.png", image, "image/png")
                }
            )
            
            js = response.json()
            if response.status_code == 200:
                print(f"Roblox.CreateGamepass | Created {name}")
                return js["gamePassId"]
            else:
                print(f"Roblox.CreateGamepass | Rate limited | {js}")
                time.sleep(60)
    
    def EditGamepass(self, id, forsale, price, isregional):
        while True:
            response = self.session.post(f"https://apis.roblox.com/game-passes/v1/game-passes/{id}/details",
                data = {
                    "isForSale": forsale,
                    "price": price,
                    "isRegionalPricingEnabled": isregional
                }
            )
            
            if response.status_code == 200:
                print(f"Roblox.EditGamepass | Edited {id}")
                return
            else:
                print(f"Roblox.EditGamepass | Rate limited. Retrying in 60s")
                time.sleep(60)


Version = "v1.0.0"


def Menu():
    print(f'''
    ██╗░░░░░░█████╗░██╗░░░██╗███████╗   ｜   Version: {Version}
    ██║░░░░░██╔══██╗██║░░░██║██╔════╝   ｜   
    ██║░░░░░███████║╚██╗░██╔╝█████╗░░   ｜   
    ██║░░░░░██╔══██║░╚████╔╝░██╔══╝░░   ｜   
    ███████╗██║░░██║░░╚██╔╝░░███████╗   ｜   
    ╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝   ｜    
    \n''')


def Commands():
    CommandList = ["Clear Badges", "Clear Friends", "Clear Following", "Private Games", "Get Free Items", "Mass DM"]
    print("".join(
        f"      {i}: {cmd}\n"
        for i, cmd in enumerate(CommandList, start=1)
    ))


def Clear():
    os.system("cls" if os.name == "nt" else "clear")


if os.name == "nt":
    os.system("color 6")
else:
    print("\033[33m", end="")

Menu()
Cookie = input("COOKIE: ")

API = Roblox(Cookie)
Clear()

def Menu():
    print(f'''
    ██╗░░░░░░█████╗░██╗░░░██╗███████╗   ｜   Version: {Version}
    ██║░░░░░██╔══██╗██║░░░██║██╔════╝   ｜   User: {API.userid}
    ██║░░░░░███████║╚██╗░██╔╝█████╗░░   ｜   
    ██║░░░░░██╔══██║░╚████╔╝░██╔══╝░░   ｜   
    ███████╗██║░░██║░░╚██╔╝░░███████╗   ｜   
    ╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝   ｜   
    \n''')

while True:
    Clear()
    Menu()
    Commands()
    Command = input("> ")
    Clear()
    Menu()

    if Command == "1":
        Badges = API.GetBadges(API.userid)

        for Badge in Badges:
            ID = Badge.get("id")
            API.DeleteBadge(ID)

        print("Lave | Successfully deleted badges!")
    elif Command == "2":
        Friends = API.GetFriends(API.userid)

        for ID in Friends:
            API.Unfriend(ID)

        print("Lave | Successfully unfriended everyone!")
    elif Command == "3":
        Following = API.GetFollowing(API.userid)

        for ID in Following:
            API.Unfollow(ID)

        print("Lave | Successfully unfollowed everyone!")
    elif Command == "4":
        Games = API.GetGames(API.userid)
        
        for Game in Games:
            ID = Game.get("id")
            API.PrivateGame(ID)
         
        print("Lave | Successfully privated games!")
    elif Command == "5":
        Free = API.FetchItems()
        
        for Item in Free:
            API.PurchaseItem(Item)
        
        print("Lave | Successfully bought free items!")
    elif Command == "6":
        Message = input("Message: ")
        Clear()
        
        Friends = API.GetFriends(API.userid)
        Convos = API.GetConversations()
        
        def HasConvo(Id):
            for Convo in Convos:
                if Id in Convo["participant_user_ids"]:
                    return Convo
        
        for Friend in Friends:
            Id = HasConvo(Friend).get("id") or API.CreateConversation(Friend)[0]["id"]
            if Id:
                API.SendMessage(Id, Message)
        
        print("Lave | Successfully mass dm'd!")
    
    input("Press anything to continue...")
