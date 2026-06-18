from colorsys import hls_to_rgb
import numpy as np
import os

DIR = os.path.dirname(os.path.abspath(__file__))

class BitStream:
    def __init__(self, ifile: str, ofile: str):
        """Create a BitStream

        Parameters
        ----------
        ifile: str
            Name of input file
        ofile: str
            Name of output file
        """
        self.ifile = np.fromfile(ifile, dtype=np.uint8)
        self.file_size = len(self.ifile)
        self.ibits = np.unpackbits(self.ifile, bitorder="little")
        self.bits_count = self.file_size * 8
        self.ibyte_idx = 0
        self.bits_in_ibuffer = 0

        self.ofp = open(ofile, "wb")
        self.buffer_size = 64
        self.bits_in_obuffer = 0
        self.obuffer = np.zeros(self.buffer_size, dtype=np.uint8)

    def read_bit(self) -> np.uint8:
        """Read 1 bit from ifile

        Returns
        -------
        bit: np.uint8
            Next bit from ifile
        """
        if self.bits_in_ibuffer >= self.bits_count:
            return np.array([], dtype=np.uint8)
        bit = self.ibits[self.bits_in_ibuffer]
        self.bits_in_ibuffer += 1
        return bit

    def write_bit(self, bit: np.uint8):
        """Write 1 bit to ofile

        Parameters
        ----------
        bit: dtype=np.uint8
            1 bit to write to ofile
        """
        self.obuffer[self.bits_in_obuffer] = bit
        self.bits_in_obuffer += 1
        if self.bits_in_obuffer == self.buffer_size:
            self.bits_in_obuffer = 0
            self.ofp.write(np.packbits(self.obuffer, bitorder="little").tobytes())

    def read_byte(self) -> np.uint8:
        """Read 1 symbol (1 byte) from ifile

        Returns
        -------
        byte: np.uint8
            Next symbol (byte) from ifile
        """
        if self.ibyte_idx >= self.file_size:
            return np.array([], dtype=np.uint8)
        byte = self.ifile[self.ibyte_idx]
        self.ibyte_idx += 1
        return byte

    def write_byte(self, byte: np.uint8):
        """Write 1 symbol (byte) to ofile

        Parameters
        ----------
        byte : np.uint8
            1 symbol (byte) to write to ofile
        """
        self.ofp.write(byte)

    def close(self):
        """Write last bits from obuffer to ofile and close ifile, ofile"""
        if self.bits_in_obuffer > 0:
            self.obuffer[self.bits_in_obuffer :] = 0
            n_bytes = self.bits_in_obuffer // 8 + 1
            self.ofp.write(
                np.packbits(self.obuffer, bitorder="little")[: n_bytes].tobytes()
            )
        self.ofp.close()


class FrequencyTable:
    def __init__(self):
        """Create frequency table
        """
        ### your code here

        self.chars_in_text = np.ones(256, dtype=np.ulonglong)
        self.freq_table = np.cumsum(self.chars_in_text)
        self.MAXfreq = 16000
        self.allsymbols = 0
        self.agr = 256


    def update(self, byte : np.uint8):
        """Use 1 byte (symbol) to update frequency table

        Parameters
        ----------
        byte : np.uint8
            1 byte (symbol)
        """
        ### your code here
        
        if self.freq_table[-1] + self.agr >= self.MAXfreq:
            self.chars_in_text //= 2
            self.chars_in_text += 1
            self.chars_in_text[byte] += self.agr
            self.freq_table = np.cumsum(self.chars_in_text)
        else:
            self.chars_in_text[byte] += self.agr
            self.freq_table[byte:256] += self.agr
        self.allsymbols += 1
    
    def save_total(self):
        np.savetxt(os.path.join(DIR, 'total.txt'), [self.allsymbols], fmt = "%d")

    def load_total(self):
        self.total = np.loadtxt(os.path.join(DIR, 'total.txt'))


class ArithmeticCompressor:
    def __init__(self, bitstream : BitStream, frequency_table : FrequencyTable):
        """Create arithmetic compressor, initialize all parameters

        Parameters
        ----------
        bitstream : BitStream
            bitstream to read/write bits/bytes
        frequency_table : FrequencyTable
            Frequency table for arithmetic compressor
        """
        ### your code here
        self.bitstream = bitstream
        self.frequency_table = frequency_table
        self.l = 0
        self.h = (1 << 16) - 1
        self.freq_table = frequency_table.freq_table

        self.First_qtr = np.uint32(self.h + 1) >> 2
        self.Half = self.First_qtr << 1
        self.Third_qtr = self.First_qtr * 3
        
        self.bits_to_follow = 0
        self.value = np.uint16(0)

    def encode_byte(self, byte : np.uint8):
        """Encode 1 byte (symbol) using arithmetic encoding algorithm

        Parameters
        ----------
        byte : np.uint8
            1 byte (symbol) to encode
        """
        ### your code here

        hl_range = np.uint32(self.h - self.l) + 1
        self.h = np.uint16(self.l + hl_range * self.freq_table[byte]//self.freq_table[-1] - 1)
        if byte:
            self.l = np.uint16(self.l + hl_range * self.freq_table[byte - 1]//self.freq_table[-1])
        while True:

            if self.h < self.Half:
                self.bits_plus_follow(0)
            elif self.l >= self.Half:
                self.bits_plus_follow(1)
                self.l -= self.Half
                self.h -= self.Half
            elif (self.l >= self.First_qtr) and (self.h < self.Third_qtr):
                self.bits_to_follow += 1
                self.l -= self.First_qtr
                self.h -= self.First_qtr
            else:
                break
            self.l <<= 1
            self.h = (self.h << 1) + 1

        self.frequency_table.update(byte)
        self.freq_table = self.frequency_table.freq_table

    def bits_plus_follow(self, bit: np.uint8):
        self.bitstream.write_bit(bit)
        while self.bits_to_follow > 0:
            self.bitstream.write_bit(not bit)
            self.bits_to_follow -= 1




    def decode_byte(self):
        """Decode 1 byte (symbol) using arithmetic decoding algorithm

        Returns
        -------
        byte : np.uint8
            1 decoded byte (symbol)
        """
        ### your code here
        hl_range = np.uint32(self.h - self.l + 1)

        freq_value = (np.uint64(self.value - self.l + 1) * self.freq_table[-1] - 1)//hl_range
        
        for symbol in range(256):
            if self.frequency_table.freq_table[symbol] > freq_value:
                break

        self.h = np.uint16(self.l + hl_range * self.freq_table[symbol]//self.freq_table[-1] - 1)
        if symbol:
            self.l = np.uint16(self.l + hl_range * self.freq_table[symbol - 1]//self.freq_table[-1])

        while True:
            if self.h < self.Half: 
                pass
            elif self.l >= self.Half:
                self.value -= self.Half
                self.l -= self.Half
                self.h -= self.Half
            elif (self.l >= self.First_qtr) and (self.h < self.Third_qtr):
                self.value -= self.First_qtr
                self.l -= self.First_qtr
                self.h -= self.First_qtr
            else:
                break

            self.l <<= 1
            self.h = (self.h << 1) + 1
            if (bit := self.bitstream.read_bit()).size:
                self.value = (self.value << 1) | bit
            else:
                self.value = self.value << 1
        
        byte = np.uint8(symbol)

        self.frequency_table.update(byte)
        self.freq_table = self.frequency_table.freq_table
        return byte


def compress_ari(ifile : str, ofile : str):
    """PUT YOUR CODE HERE
       implement an arithmetic encoding algorithm for compression
    Parameters
    ----------
    ifile: str
        Name of input file
    ofile: str
        Name of output file
    """

    bitstream = BitStream(ifile, ofile)
    frequency_table = FrequencyTable()

    compressor = ArithmeticCompressor(bitstream, frequency_table)
    
    while (byte := bitstream.read_byte()).size:
        compressor.encode_byte(byte)
    compressor.bits_to_follow += 1
    compressor.bits_plus_follow(compressor.h > compressor.Third_qtr)

    frequency_table.save_total()
    bitstream.close()
    

    ### This is an implementation of simple copying
    """
    bitstream = BitStream(ifile, ofile)
    bit = 0
    while (bit := bitstream.read_bit()).size:
        bitstream.write_bit(bit)
    bitstream.close()
    """


def decompress_ari(ifile : str, ofile : str):
    """PUT YOUR CODE HERE
       implement an arithmetic decoding algorithm for decompression
    Parameters
    ----------
    ifile: str
        Name of input file
    ofile: str
        Name of output file
    """

    bitstream = BitStream(ifile, ofile)
    frequency_table = FrequencyTable()
    
    frequency_table.load_total()
    print(bitstream.ibits)
    compressor = ArithmeticCompressor(bitstream, frequency_table)

    for _ in range(16):
        compressor.value <<= 1
        if (bit := bitstream.read_bit()).size:
            compressor.value = compressor.value | bit

    for _ in range(int(frequency_table.total)):
        byte = compressor.decode_byte()
        bitstream.write_byte(byte)

    bitstream.close()
    ### This is an implementation of simple copying
    """
    bitstream = BitStream(ifile, ofile)
    byte = 0
    while (byte := bitstream.read_byte()).size:
        bitstream.write_byte(byte)
    bitstream.close()
    """