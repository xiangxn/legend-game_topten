from bson import json_util
import mongoengine as me
from mongoengine.queryset.queryset import QuerySet


class MainAttrs(me.EmbeddedDocument):
    meta = {"collection": "mainattrs"}

    #装备id
    id = me.StringField(required=True, primary_key=True)
    #物理攻击
    attack = me.IntField(required=True)
    #道术攻击
    taoism = me.IntField(required=True)
    #魔法攻击
    magic = me.IntField(required=True)
    #物理防御
    defense = me.IntField(required=True)
    #魔法防御
    magicDefense = me.IntField(required=True)
    #体力值
    physicalPower = me.IntField(required=True)
    #魔力值
    magicPower = me.IntField(required=True)


class Equipment(me.EmbeddedDocument):
    # meta = {"collection": "equipment",'queryset_class': CustomQuerySet}
    meta = {"collection": "equipment"}

    #装备id
    id = me.StringField(required=True, primary_key=True)
    #装备编号
    number = me.IntField(required=True)
    #职业
    profession = me.IntField(required=True)
    #装备类型/部位
    category = me.IntField(required=True)
    #装备品质
    quality = me.IntField(required=True)
    #是否锁定
    locked = me.BooleanField(required=True)
    #是否装备
    isEquip = me.BooleanField(required=True)
    #锁定的token数量
    tokens = me.StringField(required=True)
    #战力
    power = me.IntField(required=True)
    #等级
    level = me.IntField(required=True)
    #当前强化次数
    increaseCount = me.IntField(required=True)
    #最高强化次数
    increaseMax = me.IntField(required=True)
    #套装Id
    suitId = me.IntField(required=True)
    #套装编号
    suitNumber = me.IntField(required=True)
    #主属性
    mainAttrs = me.EmbeddedDocumentField(MainAttrs)


class Goods(me.Document):
    # meta = {"collection": "goods", 'queryset_class': CustomQuerySet}
    meta = {"collection": "goods"}

    #商品id
    id = me.IntField(required=True, primary_key=True)
    #商品类型(1装备,2碎片,3艺术品)
    gclass = me.IntField(required=True)
    #商品状态GoodsStatus(1正常,2成交,3下架)
    status = me.IntField(required=True)
    #商品价格(商品总价)
    price = me.StringField(required=True)
    #数量
    amount = me.IntField(required=True)
    #卖家
    seller = me.StringField(required=True)
    #买家
    buyer = me.StringField(required=True)
    #道具id(装备id、碎片id、艺术品id)
    contentId = me.StringField(required=True)
    #支付币种合约地址
    payContract = me.StringField(required=True)
    content = me.EmbeddedDocumentField(Equipment)
