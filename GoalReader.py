#!/usr/bin/env python2.7
from __future__ import print_function

import pdb
import atexit
#atexit.register(pdb.set_trace)
import SocketServer
import argparse
import array
import collections
import json
import socket
import struct
import threading
import time
import usb.core
import lcm

from Forseti import Flags
from Forseti import Tag
from Forseti import Health

usb_lock = threading.Lock()
debug_reads = False

'''
GoalReader reads the Grizzly-adafruit and PcProx readers, and publishes Tag messages.

TODO(ajc): ReaderState, health
'''
class Uptimer(object):

    def __init__(self):
        self.start_time = time.time()

    def time(self):
        return time.time() - self.start_time

def Nothing(*args):
    pass

class ReaderReactor(object):

    def __init__(self, update_callback, add_callback=Nothing,
            remove_callback=Nothing):
        self.update_callback = update_callback
        self.remove_callback = remove_callback
        self.add_callback = add_callback
        self.readers = self.get_readers()
        self.setup_readers(self.readers)
        self.addr_map = self.get_addr_map()
        self.last_ids = [0] * len(self.readers)
        self._thread = threading.Thread(target=self.check_loop)
        self._thread.daemon = True
        self._thread.start()

    def get_addr_map(self):
        return dict([(dev.address, 0) for dev in self.readers])

    def get_more_readers(self):
        try:
            devs = self.get_readers()
        except usb.core.USBError as e:
            print('Unexpected error when scanning for new readers.')
            print(e)
        for dev in devs:
            if dev.address not in self.addr_map:
                self.setup_readers([dev])
                self.readers.append(dev)
                self.addr_map[dev.address] = 0
                self.last_ids.append(0)
                print('Got new reader.')
                self.add_callback(self, len(self.readers) - 1)

    def setup_readers(self, devs):
        for dev in devs:
            try:
                usb_lock.acquire()
                dev.detach_kernel_driver(0)
            except usb.core.USBError as e:
                print('Could not detach kernel driver.')
                print('This is normal if octopus has been restarted.')
            finally:
                usb_lock.release()
        return devs


    def get_readers(self):
        try:
            usb_lock.acquire()
            devs = usb.core.find(
                idVendor = self.idVendor, 
                idProduct = self.idProduct,
                find_all=True)
            return devs
        finally:
            usb_lock.release()

    def get_id(self, dev):
        raise NotImplemented()

    def check_loop(self):
        i = 0
        while True:
            i += 1
            self.do_read()
            if i % 5 == 0:
                self.get_more_readers()

    def count(self):
        return len(self.readers)

    def do_read(self):
        time.sleep(0.01)
        for i in range(len(self.readers)):
            if self.readers[i] is None:
                continue
            try:
                val = self.get_id(self.readers[i])
            except usb.core.USBError as e:
                print('Control transfer with reader failed.')
                print(e)
                print('Backend_eroor_code', e.backend_error_code)
                if e.backend_error_code != -7:
                    # If the reader encountered an error besides timeout,
                    # remove it.

                    self.readers[i] = None
                    self.remove_callback(self, i)
                continue
            if self.last_ids[i] != val:
                self.last_ids[i] = val
                if val != 0:
                    #print('New value from reader:', val)
                    self.update_callback(self, i, val)

    def _reverse_byte(self, val):
        out = 0
        for i in range(8):
            out <<= 1
            out |= (val >> i) & 1
        return out


class GrizzlyReaderReactor(ReaderReactor):

    # Magic numbers from the Grizzly Bear Motor Controller Reader
    idVendor = 0x03eb
    idProduct = 0x204f

    def __init__(self, *args, **kwargs):
        # < sets endianess here
        self.id_format = struct.Struct('<I')
        ReaderReactor.__init__(self, *args, **kwargs)

    def get_id(self, dev):
        try:
            usb_lock.acquire()
            card_id = dev.ctrl_transfer(0xa1, 0x01, 0x0300, 0, 4)
            unpacked = self.id_format.unpack(card_id)[0]
            #unpacked >>= 1
            #unpacked &= ~0xc0000000
            if debug_reads and unpacked and unpacked != self.last_ids[self.readers.index(dev)]:
                reved = array.array('B', map(self._reverse_byte, card_id))
                print('Grizzly Read:', card_id, 'Reversed:', reved)
                print('unpacked:\t{:032b}'.format(unpacked))
                rev_unpacked = self.id_format.unpack(reved)[0]
                print('rev_unpacked:\t{:032b}'.format(rev_unpacked))
                #print('unpacked:\t', bin(unpacked))
                #print('rev_unpacked:\t', bin(rev_unpacked))
            #if card_id[0]:
                #print('Grizzly read', card_id)
            return unpacked
        finally:
            usb_lock.release()


class PcProxReaderReactor(ReaderReactor):

    # Magic numbers from the pcProx reader
    idVendor = 0x0c27
    idProduct = 0x3bfa

    CMD_GET_CARD_ID                = '\x8f\x00\x00\x00\x00\x00\x00\x00'
    CMD_GET_CARD_ID_32             = '\x8d%c\x00\x00\x00\x00\x00\x00'
    CMD_GET_CARD_ID_EXTRA_INFO     = '\x8e\x00\x00\x00\x00\x00\x00\x00'
    CMD_BEEP                       = '\x8c\x03%c\x00\x00\x00\x00\x00'
    CMD_GET_MODEL                  = '\x8c\x01%c\x00\x00\x00\x00\x00'
    CMD_CONFIG_FIELD_82            = '\x82\x00\x00\x00\x00\x00\x00\x00'
    CMD_GET_VERSION                = '\x8a\x00\x00\x00\x00\x00\x00\x00'

    def __init__(self, *args, **kwargs):
        # < sets endianess here
        self.id_format = struct.Struct('<I')
        ReaderReactor.__init__(self, *args, **kwargs)

    def _send_bytes(self, dev, cmd):
        '''Send a command to the card reader. Do not try to read anything back.'''
        assert len(cmd) == 8, 'Must send only 8 bytes'
        #feature report out, id = 0
        try:
            usb_lock.acquire()
            dev.ctrl_transfer(0x21, 0x09, 0x0300, 0, cmd)
        finally:
            usb_lock.release()

    def _exchange_bytes(self, dev, cmd):
        '''Send a command to the card reader and read 8 bytes of reply back.'''
        assert len(cmd) == 8, 'Must send only 8 bytes'
        #feature report out, id = 0
        try:
            usb_lock.acquire()
            dev.ctrl_transfer(0x21, 0x09, 0x0300, 0, cmd)
            #feature report in, id = 1
            return dev.ctrl_transfer(0xa1, 0x01, 0x0301, 0, 8)
        finally:
            usb_lock.release()

    def get_id(self, dev):
        card_id = self._exchange_bytes(dev, self.CMD_GET_CARD_ID)[:4]
        unpacked = self.id_format.unpack(card_id)[0]
        unpacked <<= 1
        if debug_reads and unpacked and unpacked != self.last_ids[self.readers.index(dev)]:
            reved = array.array('B', map(self._reverse_byte, card_id))
            print('pcProx Read:', card_id, 'Reversed:', reved)
            print('unpacked:\t{:032b}'.format(unpacked))
            rev_unpacked = self.id_format.unpack(reved)[0]
            print('rev_unpacked:\t{:032b}'.format(rev_unpacked))
        return unpacked

    def get_id_256bit(self, dev):
        big_format = struct.Struct('<QQ')
        accum = []
        for i in range(4):
            accum.extend(self._exchange_bytes(dev, 
                                              self.CMD_GET_CARD_ID_32 % i))
        return sum(big_format.unpack(card_id))


class RandomTestReaderReactor(ReaderReactor):

    def __init__(self, *args, **kwargs):
        self.readers = [(), (), (), ()]
        ReaderReactor.__init__(self, *args, **kwargs)

    def get_id(self, dev):
        import random
        return random.getrandbits(32)

    def get_readers(self):
        return self.readers

    def get_more_readers(self):
        return []

    def setup_readers(self, devs):
        return devs

    def get_addr_map(self):
        return {}

    def do_read(self):
        time.sleep(1)
        ReaderReactor.do_read(self)


class Handler(SocketServer.BaseRequestHandler):

    def handle(self):
        print('Got packet.')
        msg = self.request[0]
        print(msg)
        packet = json.loads(msg)
        print(packet)
        if packet[u'Type'] == u'Confirm':
            print('Got confirm.')
            self.server.read_sender.repeater.push_confirm(msg)
        else:
            print('Received unknown packet {}'.format(msg))

    def handle_confirm(self, msg):
        self.server.read_sender.repeater.push_confirm(msg)


class Server(SocketServer.UDPServer):

    def __init__(self, in_addr, out_addr):
        SocketServer.UDPServer.__init__(self, in_addr, Handler)
        self.in_addr = in_addr
        self.out_addr = out_addr
        self.out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.read_sender = TagReadSender(None, None, self)
        self.grizzlies = GrizzlyReaderReactor(self.read_sender.respond)
        self.pcproxen = PcProxReaderReactor(self.read_sender.respond)
        #self.pcproxen = RandomTestReaderReactor(self.read_sender.respond)
        #self.grizzlies = RandomTestReaderReactor(self.read_sender.respond)

        grizzly_special_ids = {
            299738614:'A',
            300432102:'B',
            299078422:'C',
            300136398:'D',
        }
        pcproxen_special_ids = {
            301040998:'Dispense',
            766208925:'Verify',
            299738614:'VerifyA',
            300432102:'VerifyB',
            299078422:'VerifyC',
            300136398:'VerifyD',
        }
        self.field_state = FieldState([self.grizzlies, self.pcproxen],
                [grizzly_special_ids, pcproxen_special_ids])
        self.grizzlies.remove_callback = self.field_state.remove_reader
        self.pcproxen.remove_callback = self.field_state.remove_reader
        self.grizzlies.add_callback = self.field_state.add_reader
        self.pcproxen.add_callback = self.field_state.add_reader
        self.formatter = Formatter(Uptimer(), self.field_state)
        self.read_sender.field_state = self.field_state
        self.read_sender.formatter = self.formatter
        self.health_sender = HealthSender(self.formatter, self)
        self._lock = threading.Lock()
        self.lcm = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")
        subscription = self.lcm.subscribe("GoalReader/TagConfirm", self.msg_handler)
        self._thread = threading.Thread(target=self._loop)
        self._thread.daemon = True


    def run(self):
        self._thread.run()

    def _loop(self):
        try:
            while True:
                self.lcm.handle()
        except:
            pass


    def send(self, topic, msg):
        self.lcm.publish(topic, msg.encode())
        '''
        try:
            self._lock.acquire()
            print('Sending', msg)
            self.out_sock.sendto(msg, self.out_addr)
        except Exception as e:
            print('Exception when sending packet:', e)
        finally:
            self._lock.release()
        '''

    def msg_handler(self, channel, data):
        if channel == "GoalReader/TagConfirm":
            msg = Tag.decode(data)
            print ("received tagConfirm!")
            print("reader=" + msg.reader)
            print("tagId="  + str(msg.tagId))
            self.read_sender.repeater.push_confirm(msg)

class HealthSender(object):

    def __init__(self, formatter, server):
        self.formatter = formatter
        self.server = server
        self._thread = threading.Thread(target=self._loop)
        self._thread.daemon = True
        self._thread.start()

    def _loop(self):
        while True:
            time.sleep(0.25)
            self.server.send("GoalReader/Health", self.formatter.format_health())


class TagReadSender(object):

    def __init__(self, field_state, formatter, server):
        self.field_state = field_state
        self.formatter = formatter
        self.server = server
        self.repeater = Repeater(formatter, server)
        #self.lc = lcm.LCM("udpm://239.255.76.67:7667?ttl=1")

    def respond(self, reactor, idx, new_val):
        if self.field_state.is_special_id(reactor, new_val):
            self.field_state.update_reader_map(reactor, idx, new_val)
        else:
            msg = self.formatter.format_tag_read(reactor, idx, new_val)
            #self.lc.publish("GoalReader/Tags", msg.encode());
            #self.server.publish("GoalReader/Tags", msg.encode());
            self.server.send("GoalReader/Tags", msg)
            self.repeater.push_send(msg.tagId, msg)
            '''
            print(msg)
            self.server.send(msg)
            self.repeater.push_send(unicode(new_val), msg)
            '''


class Repeater(object):

    def __init__(self, formatter, server):
        self.server = server
        self.formatter = formatter
        self.unconfirmed = {}
        self._thread = threading.Thread(target=self._loop)
        self._thread.daemon = True
        self._thread.start()

    def _loop(self):
        while True:
            time.sleep(0.1)
            for record in self.unconfirmed.values():
                self.server.send("GoalReader/Tags", record)

    def push_send(self, tag_id, msg):
        #print ("push send")
        self.unconfirmed[tag_id] = msg

    def push_confirm(self, msg):
        try:
            tag_id = msg.tagId
            del self.unconfirmed[tag_id]
            print('Removing from unconfirmed', tag_id)            
        except KeyError:
            pass
        '''
        try:
            obj = json.loads(msg)
            tag_id = unicode(msg.tagId)
            try:
                tag_id = obj[u'Packet'][u'TagID']
            except KeyError:
                tag_id = obj[u'TagID']
            del self.unconfirmed[tag_id]
            print('Removing from unconfirmed', tag_id)
        except KeyError:
            pass
        '''

class ReactorState(object):

    def __init__(self, field_state, reactor, special_ids):
        self._field_state = field_state
        self._reactor = reactor
        self._special_id_to_reader = special_ids
        self._idx_to_reader = dict(zip(range(reactor.count()), ['Unknown'] *
            reactor.count()))

    def reader_of_idx(self, idx):
        try:
            return self._idx_to_reader[idx]
        except KeyError:
            return 'Unknown'

    def is_special_id(self, tag_id):
        return tag_id in self._special_id_to_reader.keys()

    def update_reader_map(self, idx, tag_id):
        self._field_state.names_to_count[self._idx_to_reader[idx]] -= 1
        reader = self._special_id_to_reader[tag_id]
        self._idx_to_reader[idx] = reader
        self._field_state.names_to_count[self._idx_to_reader[idx]] += 1

    def remove_reader(self, idx):
        self._field_state.names_to_count[self._idx_to_reader[idx]] -= 1
        self._idx_to_reader[idx] = 'Unknown'

    def add_reader(self, idx):
        self._field_state.names_to_count['Unknown'] += 1
        self._idx_to_reader[idx] = 'Unknown'

class FieldState(object):
    def __init__(self, reactors, special_idses):
        self._reactors = {}
        self.names_to_count = {'Unknown':0}
        for reactor, special_ids in zip(reactors, special_idses):
            self._reactors[reactor] = ReactorState(self, reactor, special_ids)
            self.names_to_count['Unknown'] += reactor.count()
            for reader in special_ids.values():
                self.names_to_count[reader] = 0

    def reader_of_idx(self, reactor, idx):
        try:
            return self._reactors[reactor].reader_of_idx(idx)
        except KeyError:
            return 'Unknown'

    def is_special_id(self, reactor, tag_id):
        return self._reactors[reactor].is_special_id(tag_id)

    def update_reader_map(self, reactor, idx, tag_id):
        return self._reactors[reactor].update_reader_map(idx, tag_id)

    def remove_reader(self, reactor, idx):
        return self._reactors[reactor].remove_reader(idx)

    def add_reader(self, reactor, idx):
        return self._reactors[reactor].add_reader(idx)


class Formatter(object):

    tag_read_format = \
            '''{"Type":"TagRead","Time":1235243,"Reader":"Unknown","TagID":41231231232}'''
    tag_health_format = \
            '''{"Type":"Health","Time":31231231,"Readers":{"A":2,"B":0,"C":1,"D":0,"Unknown":1,"Verify":0,"Dispense":0}}'''
    tag_read_confirm_format = \
            '''{"Type":"Confirm","Time":1231323,"Packet":{"Type":"TagRead","Time":1235243,"Reader":"A","TagID":41231323132}}'''
    def __init__(self, timer, field_state):
        self.field_state = field_state
        self.timer = timer

    def format_health(self):
        '''
        obj = { 'Type': 'Health', 
                'Time': self.timer.time(),
                'Readers': self.field_state.names_to_count }
        return json.dumps(obj)
        '''
        msg = Health()
        msg.uptime = self.timer.time()
        print ("readers=" + str(self.field_state.names_to_count))
        return msg


    def format_tag_read(self, reactor, idx, new_val):
        '''
        obj = { 'Type': 'TagRead',
                'Time': self.timer.time(),
                'Reader': self.field_state.reader_of_idx(reactor, idx),
                'TagID': unicode(new_val) }
        return json.dumps(obj)
        '''
        msg = Tag()
        msg.uptime = self.timer.time()
        msg.reader = self.field_state.reader_of_idx(reactor, idx)
        msg.tagId = new_val
        return msg


def main():

    parser = argparse.ArgumentParser(
        description='Read tags from readers and send packets to Forseti')
    #in_addr = ('localhost', 1922)
    #out_addr = ('localhost', 1921)
    #out_addr = ('10.10.67.197', 8000)

    in_addr = ('', 8000)
    #out_addr = ('10.42.0.1', 8000)
    out_addr = ('10.20.34.100', 8000)

    Server(in_addr, out_addr).run()

if __name__ == '__main__':
    main()
