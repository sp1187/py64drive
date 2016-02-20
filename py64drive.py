from pylibftdi import Device
import struct
import sys
import enum

class BankType(enum.IntEnum):
    INVALID = 0
    CARTROM = 1
    SRAM256 = 2
    SRAM768 = 3
    FLASHRAM = 4
    FLASHRAM_PKMNST2 = 5
    EEPROM = 6

class SaveType(enum.IntEnum):
    NONE = 0
    EEPROM4 = 1
    EEPROM16 = 2
    SRAM256 = 3
    FLASHRAM = 4
    SRAM768 = 5
    FLASHRAM_PKMNST2 = 6

class CommandType:
    pass

CHUNK_SIZE = 4 * 1024 * 1024

class Py64drive:
    def __init__(self):
        self.device = Device(device_id="64drive USB device")

    def _send_cmd(self, cmd, params):
        txbuf = struct.pack(">B3s",cmd,b"CMD")
        if len(params) >= 1:
            txbuf += struct.pack(">L",params[0])
        if len(params) >= 2:
            txbuf += struct.pack(">L",params[1])

        self.device.write(txbuf)

    def _recv_resp(self):
        rxbuf = self.device.read(4)
        return struct.unpack(">L", rxbuf)

    def _recv_ver_resp(self):
        rxbuf = self.device.read(8)
        return struct.unpack(">L4s", rxbuf)

    def _recv_success(self,command):
        while True:
            rxbuf = self.device.read(4)
            if rxbuf: break

        if rxbuf != b"CMP" + bytes([command]):
            #print("Got {}, expected CMP{}",rxbuf,command,file=sys.stderr)
            return False

        return True

    def load_image(self, data, bank, ram_addr=0):
        length = len(data)

        if length % 512:
            #print("File was truncated during loading.", file=sys.stderr)
            length -= length % 512

        for offset in range(0, length, CHUNK_SIZE):
            size = min(CHUNK_SIZE, length - offset)

            block = data[offset:offset+size]

            self._send_cmd(0x20, (ram_addr + offset, (bank << 24) | (size & 0xffffff)))
            self.device.write(block)

            self._recv_success(0x20)

    def dump_image(self, length, bank, ram_addr=0):		
        data = b""

        if length % 512:
            #print("File was truncated during dumping.", file=sys.stderr)
            length -= length % 512

        for offset in range(0, length, CHUNK_SIZE):
            size = min(CHUNK_SIZE, length - offset)

            self._send_cmd(0x30, (ram_addr + offset, (bank << 24) | (size & 0xffffff)))
            data += self.device.read(size)

            self._recv_success(0x30)

        return data

    def set_save(self, save_type):
        self._send_cmd(0x70, (save_type,))
        self._recv_success(0x70)

    def read_version(self):
        self._send_cmd(0x80,())

        val,magic = self._recv_ver_resp()
        if val == 0 or magic != b"UDEV":
            #print("Incorrect 64drive version reported.", file=sys.stderr)
            return False

        self._recv_success(0x80)
        return True

    def pi_write_block(self,*args):
        raise NotImplementedError("Not implemented yet")

    def pi_write_block_long(self,*args):
        raise NotImplementedError("Not implemented yet")

    def pi_read_int32(self):
        raise NotImplementedError("Not implemented yet")

    def pi_write_int32(self,num):
        raise NotImplementedError("Not implemented yet")

