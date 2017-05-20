import sys
import codecs
import re

__version__ = '1.0.0'
__licence__ = 'GPL-3.0+'
__all__ = ()

# Python 2 compatibility
if sys.version_info < (3,):
    chr = unichr
    bytes_int_iter = bytearray
else:
    # Call to ensure that iterating over a bytes will be ints
    bytes_int_iter = lambda bytes: bytes

### Codec APIs

class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        # bin_str = '0'.join(map('1'.__mul__, map(ord, input))) + '0'
        # bin_str += '1' * (-len(bin_str) % 8)
        # return (int(bin_str, 2).to_bytes(len(bin_str) // 8, 'big'), len(input))
        return (IncrementalEncoder(errors).encode(input, True),
                len(input))

    def decode(self, input, errors='strict'):
        # return (''.join(map(chr, map(len, bin(int.from_bytes(input, 'big'))[2:].split('0')[:-1]))), len(input))
        return (IncrementalDecoder(errors).decode(input, True),
                len(input))


def reverse_byte(byte):
   byte = (byte & 0xF0) >> 4 | (byte & 0x0F) << 4
   byte = (byte & 0xCC) >> 2 | (byte & 0x33) << 2
   byte = (byte & 0xAA) >> 1 | (byte & 0x55) << 1
   return byte


class IncrementalEncoder(codecs.IncrementalEncoder):
    state = 0
    __slots__ = ()

    def encode(self, input, final=False):
        encoded = bytearray()
        state = self.state or 1
        for char in input:
            bits = ord(char)
            used = self.used_bits(state)
            state ^= 1 << used  # Flip fill bit
            state |= ((1 << bits) - 1) << used
            state_bits = used + bits + 1
            state |= 1 << state_bits  # Reflip fill bit
            while state_bits > 7:
                byte = state & 0b11111111
                encoded.append(reverse_byte(byte))
                state >>= 8
                state_bits -= 8
        self.state = 0 if state == 1 else state
        if final:
            used = self.used_bits(state)
            state |= 0b11111111 ^ ((1 << used) - 1)
            encoded.append(reverse_byte(state))
            self.reset()
        
        return bytes(encoded)

    def reset(self):
        self.state = 0

    def getstate(self):
        return self.state

    def setstate(self, state):
        self.state = state

    @staticmethod
    def used_bits(state):
        for used in range(7, -1, -1):
            if state & (1 << used):
                break
        else:
            raise ValueError('Invalid state: {!r}'.format(state))
        return used

class IncrementalDecoder(codecs.IncrementalDecoder):
    state = 0
    __slots__ = ()

    def decode(self, input, final=False):
        decoded = []
        state = self.state
        for byte in bytes_int_iter(input):
            if byte == 0xff:
                state += 8
                continue
            cons = 0
            for bit in range(7, -1, -1):
                if byte & (1 << bit):
                    cons += 1
                else:
                    try:
                        decoded.append(chr(cons + state))
                    except ValueError:
                        if self.errors != 'ignore':
                            if self.errors != 'replace':
                                raise
                            decoded.append(u'?')
                    state = cons = 0
            state += cons
        if final:
            state = 0
        self.state = state
        return u''.join(decoded)

    def reset(self):
        self.state = 0

    def getstate(self):
        return self.state

    def setstate(self, state):
        self.state = state

class StreamReader(Codec, codecs.StreamReader):
    pass
    
class StreamWriter(Codec, codecs.StreamWriter):
    pass

### Codecs API for UTF-1 for source files (Allows for shebang and `# coding=` comments)

class CodecSource(Codec):
    def encode(self, input, errors='strict'):
        return (IncrementalEncoderSource(errors).encode(input, True),
                len(input))
    def decode(self, input, errors='strict'):
        return (IncrementalDecoderSource(errors).decode(input, True),
                len(input))

class IncrementalDecoderSource(IncrementalDecoder):
    started = 0
    shebang_re = re.compile(b'^(?:[^\r\n]*(?:\r\n?|\n\r?))?[ \t\v]*#.*?coding[:=][ \t]*[Uu][Tt][Ff][-_]?1[-_]?[Ss][Oo][Uu][Rr][Cc][Ee][^\r\n]*(?:\r\n?|\n\r?)?')

    def decode(self, input, final=False):
        shebang = u''
        if not self.started:
            self.started = 1
            shebang = self.shebang_re.search(input)
            if shebang:
                input = input[shebang.end():]
                shebang = shebang.group().decode('UTF-8')
            else:
                shebang = u''
        return shebang + IncrementalDecoder.decode(self, input, final)

    def getstate(self):
        return (self.state << 1) | started

    def setstate(self, state):
        self.started = state & 1
        self.state = state >> 1

    def reset(self):
        self.state = 0
        self.started = 0

class IncrementalEncoderSource(IncrementalEncoder):
    started = 0
    shebang_re = re.compile(u'^(?:[^\r\n]*(?:\r\n?|\n\r?))?[ \t\v]*#.*?coding[:=][ \t]*[Uu][Tt][Ff][-_]?1[-_]?[Ss][Oo][Uu][Rr][Cc][Ee][^\r\n]*(?:\r\n?|\n\r?)?')
    
    def encode(self, input, final=False):
        shebang = b''
        if not self.started:
            self.started = 1
            shebang = self.shebang_re.search(input)
            if shebang:
                input = input[shebang.end():]
                shebang = shebang.group().encode('UTF-8')
            else:
                shebang = b''
        return shebang + IncrementalEncoder.encode(self, input, final)
        
    def getstate(self):
        return (self.state << 1) | started

    def setstate(self, state):
        self.started = state & 1
        self.state = state >> 1

    def reset(self):
        self.state = 0
        self.started = 0

class StreamReaderSource(CodecSource, codecs.StreamReader):
    pass
    
class StreamWriterSource(CodecSource, codecs.StreamWriter):
    pass

_REGENTRY_UTF_1 = codecs.CodecInfo(
    name='UTF-1',
    encode=Codec().encode,
    decode=Codec().decode,
    incrementalencoder=IncrementalEncoder,
    incrementaldecoder=IncrementalDecoder,
    streamreader=StreamReader,
    streamwriter=StreamWriter
)
_REGENTRY_UTF_1_SOURCE = codecs.CodecInfo(
    name='UTF-1-SOURCE',
    encode=CodecSource().encode,
    decode=CodecSource().decode,
    incrementalencoder=IncrementalEncoderSource,
    incrementaldecoder=IncrementalDecoderSource,
    streamreader=StreamReaderSource,
    streamwriter=StreamWriterSource
)
_REGENTRY_MAPPING = {
    'utf1': _REGENTRY_UTF_1,
    'utf1source': _REGENTRY_UTF_1_SOURCE
}.get

def search_fn(encoding):
    normalised = encoding.lower().replace('_', '-').replace('-', '')
    return _REGENTRY_MAPPING(normalised)

codecs.register(search_fn)
