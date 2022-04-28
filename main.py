from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher
from web3 import Web3
from web3.middleware import geth_poa_middleware
from legend import Legend
import time

legend = {}


@dispatcher.add_method
def topTen():
    '''
  测试的一个rpc方法
  :return: 
  '''
    hero = legend.top_ten()
    return hero


@dispatcher.add_method
def updatePower(address):
    return legend.update_power(address)


@dispatcher.add_method
def searchGoods(type, profession=-1, category=-1, level=-1, page=1, pageSize=20, seller=None):
    if seller is not None:
        if (legend.api.isChecksumAddress(seller) == False):
            seller = legend.api.toChecksumAddress(seller)
    return legend.search_goods(type, profession, category, level, page, pageSize, seller)


@dispatcher.add_method
def syncGoods(goods_id):
    flag = legend.get_goods(goods_id)
    if False == flag:
        time.sleep(5)
        flag = legend.get_goods(goods_id)
    return flag


@dispatcher.add_method
def delGoods(goods_id):
    return legend.del_goods(goods_id)


@Request.application
def application(request):
    '''
   服务的主方法，handle里面的dispatcher就是代理的rpc方法，可以写多个dispatcher
  :param request: 
  :return: 
  '''
    response = JSONRPCResponseManager.handle(request.get_data(cache=False, as_text=True), dispatcher)
    # headers = {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "content-type"}
    # return Response(response.json, mimetype='application/json', headers=headers)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    legend = Legend()
    run_simple('localhost', 9090, application)
    # run_simple('localhost', 9091, application)
