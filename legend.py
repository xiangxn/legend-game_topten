from web3.contract import ConciseContract
from database.model import Equipment, Goods, MainAttrs
import mongoengine
from mongoengine.queryset.visitor import Q
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os.path

top_ten_file = "./TopTen.json"


class Legend:
    def __init__(self) -> None:
        mongoengine.connect(db="bsclegend", host="localhost", port=3001)
        # mongoengine.connect(db="legendtest", host="localhost", port=3001)
        # self.api = Web3(Web3.HTTPProvider('https://http-mainnet-node.huobichain.com'))
        # self.api = Web3(Web3.HTTPProvider('HTTP://127.0.0.1:7545'))
        self.api = Web3(Web3.HTTPProvider('https://bsc-dataseed4.binance.org/'))
        # self.api = Web3(Web3.HTTPProvider('https://http-testnet.hecochain.com'))
        self.api.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.hero_address = "0x9b08fDb2B5B41F5Da4dD7D070d3e558af742a88a"
        self.market_address = "0xe674Ef9a40f17f1f8E239469B1b416b341E7Cbb5"
        self.equipment_address = "0xEb3e14412A0FCce4CEB7a9e7592f35C6675Bf6B7"
        self.hero_abi = self._loadAbi("Hero")
        self.market_abi = self._loadAbi("Market")
        self.equipment_abi = self._loadAbi("Equipment")

    def _loadAbi(self, name):
        cf = open("./abi/" + name + ".json", "r")
        abi = json.load(cf)
        cf.close()
        return abi

    def get_hero_info(self, address):
        addr = address
        if (self.api.isChecksumAddress(address) == False):
            addr = self.api.toChecksumAddress(address)
        contract = self.api.eth.contract(self.hero_address, abi=self.hero_abi)
        result = contract.functions.getHeroInfo(addr).call()
        hero = {}
        hero['address'] = addr
        if (len(result) == 2):
            hero['profession'] = result[1][0]
            hero['name'] = result[1][2]
            hero['power'] = result[1][6]
        return hero

    def read_base_address(self):
        path = "./Address.json"
        cf = open(path, "r")
        addrs = json.load(cf)
        data = []
        for addr in addrs:
            tmp = self.get_hero_info(addr)
            data.append(tmp)
        return data

    def top_ten(self):
        data = []
        if (os.path.isfile(top_ten_file)):
            with open(top_ten_file, "r") as f:
                data = json.load(f)
        else:
            tmp = self.read_base_address()
            data = self._save_top_ten(tmp)
        return data

    def _save_top_ten(self, data):
        data.sort(key=lambda elem: elem['power'], reverse=True)
        if (len(data) > 30):
            data = data[:30]
        with open(top_ten_file, "w") as f:
            json.dump(data, f)
        return data

    def update_power(self, address):
        hero = self.get_hero_info(address)
        data = self.top_ten()
        index = -1
        for i, item in enumerate(data):
            if item['address'] == hero['address']:
                index = i
        if index > -1:
            data.pop(index)
        data.append(hero)
        self._save_top_ten(data)
        return hero

    def async_goods(self):
        contract = self.api.eth.contract(address=self.market_address, abi=self.market_abi)
        contract = ConciseContract(contract)
        self._search_goods(contract, 0, 0, 50)

    def get_goods(self, goods_id):
        contract = self.api.eth.contract(address=self.market_address, abi=self.market_abi)
        contract = ConciseContract(contract)
        result = contract.getGoods(goods_id)
        # print(result)
        if result and str(goods_id) == str(result[0]):
            goods = Goods(id=str(result[0]))
            goods.gclass = result[1]
            goods.status = result[2]
            goods.price = str(result[3])
            goods.amount = result[4]
            goods.seller = result[5]
            goods.buyer = "0x0" if result[6] is None else result[6]
            goods.contentId = str(result[7])
            if goods.gclass == 1:
                goods.content = self.sync_equipment(result[7])  #str(item[7])
            goods.payContract = result[8]
            try:
                goods.save()
            except Exception as e:
                print("save goods err:", e)
                return False
            return True
        return False

    def del_goods(self, goods_id):
        goods = Goods.objects(id=str(goods_id)).first()
        goods.delete()
        return True

    def _search_goods(self, contract, type, goods_id, count):
        result = contract.searchGoods(type, goods_id, count)
        more = result[0]
        data = result[1]
        for item in data:
            if item[0] == 0:
                continue
            goods = Goods(id=str(item[0]))
            goods.gclass = item[1]
            goods.status = item[2]
            goods.price = str(item[3])
            goods.amount = item[4]
            goods.seller = item[5]
            goods.buyer = "0x0" if item[6] is None else item[6]
            goods.contentId = str(item[7])
            if goods.gclass == 1:
                goods.content = self.sync_equipment(item[7])  #str(item[7])
            goods.payContract = item[8]
            goods.save()
            goods_id = goods.id
            print("sync: ", goods.id)

        if more == True:
            self._search_goods(contract, type, goods_id + 1, count)

    def sync_equipment(self, equipmentId):
        contract = self.api.eth.contract(address=self.equipment_address, abi=self.equipment_abi)
        contract = ConciseContract(contract)
        result = contract.getEquipment(int(equipmentId))
        # print(result)
        if len(result) == 2 and result[1][0] != 0:
            equip = Equipment(id=str(result[0]))
            equip.number = result[1][0]
            equip.profession = result[1][1]
            equip.category = result[1][2]
            equip.quality = result[1][3]
            equip.locked = result[1][4]
            equip.isEquip = result[1][5]
            equip.tokens = str(result[1][6])
            equip.power = result[1][7]
            equip.level = result[1][8]
            equip.increaseCount = result[1][9]
            equip.increaseMax = result[1][10]
            equip.suitId = result[1][11]
            equip.suitNumber = result[1][12]
            equip.mainAttrs = MainAttrs(id=str(result[0]))
            equip.mainAttrs.attack = result[1][13][0]
            equip.mainAttrs.taoism = result[1][13][1]
            equip.mainAttrs.magic = result[1][13][2]
            equip.mainAttrs.defense = result[1][13][3]
            equip.mainAttrs.magicDefense = result[1][13][4]
            equip.mainAttrs.physicalPower = result[1][13][5]
            equip.mainAttrs.magicPower = result[1][13][6]
            # equip.mainAttrs.save()
            # equip.save()
            return equip
        return equipmentId

    def search_goods(self, type=-1, profession=-1, category=-1, level=-1, page=1, pageSize=20, seller=None):
        result = {}
        result['page'] = page
        result['pageSize'] = pageSize
        offset = (page - 1) * pageSize
        count = 0
        tmp = {}
        query = Q(id__gt=0)
        if type == 1:
            if profession > -1 and category > -1:
                query = Q(gclass=type) & Q(content__profession=profession) & Q(content__category=category)
            elif profession > -1:
                query = Q(gclass=type) & Q(content__profession=profession)
            else:
                query = Q(gclass=type)
        elif type == -1:
            pass
        else:
            query = Q(gclass=type)

        if seller is not None:
            query = query & Q(seller=seller)
        if level > -1:
            if level == 1:
                level = [11, 20]
            elif level == 2:
                level = [21, 30]
            elif level == 3:
                level = [31, 40]
            elif level == 4:
                level = [41, 50]
            else:
                level = [1, 10]
            query = query & (Q(content__level__gte=level[0]) & Q(content__level__lte=level[1]))

        count = Goods.objects(query).count()
        tmp = Goods.objects(query).order_by("-id").skip(offset).limit(pageSize)
        result['totalPage'] = int(count / pageSize) + (0 if count % pageSize == 0 else 1)
        result['list'] = tmp.to_json()
        return result
