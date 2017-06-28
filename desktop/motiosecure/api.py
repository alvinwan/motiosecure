import zerorpc

class MotioSecureApi:
    pass


def main():
    s = zerorpc.Server(MotioSecureApi())
    s.bind('tcp://127.0.0.1:4242')
    print('start running on {}'.format(addr))
    s.run()


if __name__ == '__main__':
    main()
