from threading import Thread


def prescript(num):
    for i in range(num):
        if i > 5:
            print(f"{i} > 5")
        else:
            print(f"{i} < 5")


#
#
thread1 = Thread(target=prescript, args=(200,))
thread2 = Thread(target=prescript, args=(100,))
#
thread1.start()
thread2.start()
thread1.join()
thread2.join()

# prescript(10)
