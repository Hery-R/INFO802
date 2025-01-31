from spyne import Integer, Unicode, rpc, Application, ServiceBase, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server


class TimePriceService(ServiceBase):
    @rpc(Integer, Integer, Integer, _returns=Iterable(Unicode))
    def get_time_price(ctx, distance , autonomy, recharge_time):
        time = distance/autonomy*60 + recharge_time
        price = time * 2
        return [u'{:.2f}'.format(time/60), u'{:.2f}'.format(price)]


application = Application([TimePriceService], 'time_price.soap',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())
wsgi_application = WsgiApplication(application)


if __name__ == '__main__':
    server = make_server('127.0.0.1', 8000, wsgi_application)
    server.serve_forever()

