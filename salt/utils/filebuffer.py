# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`


    salt.utils.filebuffer
    ~~~~~~~~~~~~~~~~~~~~~

    This utility allows parsing a file in chunks.
'''

# Import salt libs
import salt.utils
from salt.exceptions import SaltException


class InvalidFileMode(SaltException):
    '''
    An invalid file mode was used to open the file passed to the buffer
    '''


class BufferedReader(object):
    '''
    This object allows iterating through the contents of a file keeping
    X configurable bytes in memory which can be used to, for example,
    do regex search/matching on more than a single line.

    So, **an imaginary, non accurate**, example could be:

        1 - Initiate the BufferedReader filing it to max_in_men:
            br = [1, 2, 3]

        2 - next chunk(pop chunk_size from the left, append chunk_size to the
        right):
            br = [2, 3, 4]


    :type  path: str
    :param path: The file path to be read

    :type  max_in_mem: int
    :param max_in_mem: The maximum bytes kept in memory while iterating through
                       the file. Default 256KB.

    :type  chunk_size: int
    :param chunk_size: The size of each consequent read chunk. Default 32KB.

    :type  mode: str
    :param mode: The mode the file should be opened. **Only read modes**.

    '''
    def __init__(self, path, max_in_mem=256 * 1024, chunk_size=32 * 1024,
                 mode='r'):
        if 'a' in mode or 'w' in mode:
            raise InvalidFileMode("Cannot open file in write or append mode")
        self.__path = path
        self.__file = salt.utils.fopen(self.__path, mode)
        self.__max_in_mem = max_in_mem
        self.__chunk_size = chunk_size
        self.__buffered = None

    # Public attributes
    @property
    def buffered(self):
        return self.__buffered

    # Support iteration
    def __iter__(self):
        return self

    def next(self):
        '''
        Return the next iteration by popping `chunk_size` from the left and
        appending `chunk_size` to the right if there's info on the file left
        to be read.
        '''
        if self.__buffered is None:
            multiplier = self.__max_in_mem / self.__chunk_size
            self.__buffered = ""
        else:
            multiplier = 1
            self.__buffered = self.__buffered[self.__chunk_size:]

        data = self.__file.read(self.__chunk_size * multiplier)

        if not data:
            self.__file.close()
            raise StopIteration

        self.__buffered += data
        return self.__buffered

    # Support with statements
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
