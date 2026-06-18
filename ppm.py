import numpy as np


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
        self.chars_in_text = np.ones((256, 256), dtype=np.uint64)
        self.freq_table = np.cumsum(self.chars_in_text, axis=1)
        self.MAX_freq = 16000
        self.allsymbols = 0
        self.agr = 200
    
    def update(self, last: np.uint8, byte:np.uint8):
        if self.freq_table[last][-1] + self.agr >= self.MAX_freq:
            self.chars_in_text[last] //= 2
            self.chars_in_text[last] += 1
            self.chars_in_text[last][byte] += self.agr
            self.freq_table[last] = np.cumsum(self.chars_in_text[last])
        else:
            self.chars_in_text[last][byte] += self.agr
            self.freq_table[last][byte:256] += self.agr
        self.allsymbols += 1


class PPMCompressor:
    def __init__(self, bitstream : BitStream, frequency_table : FrequencyTable):
        self.bitstream = bitstream
        self.frequency_table = frequency_table
        self.l = 0
        self.h = (1 << 16) - 1
        self.freq_table = frequency_table.freq_table

        self.First_qtr = np.uint32(self.h + 1) >> 2
        self.Half = self.First_qtr << 1
        self.Third_qtr = self.First_qtr * 3
        
        self.last = 0
        self.bits_to_follow = 0
        self.value = np.uint16(0)


    def encode_byte(self, byte: np.uint8):
        hl_range = np.uint32(self.h - self.l) + 1
        self.h = np.uint16(self.l + hl_range * self.freq_table[self.last][byte]//self.freq_table[self.last][-1] - 1)
        if byte:
            self.l = np.uint16(self.l + hl_range * self.freq_table[self.last][byte - 1]//self.freq_table[self.last][-1])
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

        self.frequency_table.update(self.last, byte)
        self.freq_table = self.frequency_table.freq_table
        self.last = byte

    def bits_plus_follow(self, bit: np.uint8):
        self.bitstream.write_bit(bit)
        while self.bits_to_follow > 0:
            self.bitstream.write_bit(not bit)
            self.bits_to_follow -= 1

    def decode_byte(self):
        hl_range = np.uint32(self.h - self.l + 1)

        freq_value = (np.uint64(self.value - self.l + 1) * self.freq_table[self.last][-1] - 1)//hl_range
        
        for symbol in range(256):
            if self.frequency_table.freq_table[self.last][symbol] > freq_value:
                break

        self.h = np.uint16(self.l + hl_range * self.freq_table[self.last][symbol]//self.freq_table[self.last][-1] - 1)
        if symbol:
            self.l = np.uint16(self.l + hl_range * self.freq_table[self.last][symbol - 1]//self.freq_table[self.last][-1])

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

        self.frequency_table.update(self.last, byte)
        self.freq_table = self.frequency_table.freq_table
        self.last = byte

        return byte


def compress_ppm(ifile : str, ofile : str):
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

    compressor = PPMCompressor(bitstream, frequency_table)
    
    while (byte := bitstream.read_byte()).size:
        compressor.encode_byte(byte)
    compressor.bits_to_follow += 1
    compressor.bits_plus_follow(compressor.h > compressor.Third_qtr)

    bitstream.close()

    file = open(ofile, "a")
    print('\n' + str(frequency_table.allsymbols), file=file)
    file.close()
    

    ### This is an implementation of simple copying
    """
    bitstream = BitStream(ifile, ofile)
    bit = 0
    while (bit := bitstream.read_bit()).size:
        bitstream.write_bit(bit)
    bitstream.close()
    """


def decompress_ppm(ifile : str, ofile : str):
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
    
    compressor = PPMCompressor(bitstream, frequency_table)

    i = 2
    total = ''
    while chr(bitstream.ifile[-i]) != '\n':
        total = chr(bitstream.ifile[-i]) + total
        i += 1
    
    total = int(total)

    for _ in range(16):
        compressor.value <<= 1
        if (bit := bitstream.read_bit()).size:
            compressor.value = compressor.value | bit
    
    for _ in range(total):
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