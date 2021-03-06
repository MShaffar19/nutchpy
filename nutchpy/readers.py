"""
Various Readers for the Nutch EcoSystem
"""

from __future__ import absolute_import, division, print_function

from .JVM import gateway

class GeneralReader(object):
    gateway = gateway

    def read(self, path=None, auto_convert=True):
        """
        method to read entire contents of a file

        Parameters
        ----------
        path : str

        Returns
        -------
        list of strings
        """

        data = self.reader.read(path)
        if auto_convert:
            data = [dict(d) for d in data]
        return data

    def head(self, nrows=5, path=None, auto_convert=True):
        """
        method to read first n-rows of a file

        Parameters
        ----------
        nrows : int
        path : str

        Returns
        -------
        list of strings
        """

        data = self.reader.head(nrows, path)
        if auto_convert:
            data = [dict(d) for d in data]

        return data

    def slice(self, start, stop, path=None, auto_convert=True):
        """
        method to slice (start, stop) contents of a file

        Parameters
        ----------
        nrows : int
        path : str

        Returns
        -------
        list of strings
        """

        data = self.reader.slice(start, stop, path)
        if auto_convert:
            data = [dict(d) for d in data]

        return data

    def count(self,path=None, auto_convert=True):
        """
        method to count number of rows in a file

        Parameters
        ----------
        path : str

        Returns
        -------
        long

        """

        count = self.reader.count(path)
        if auto_convert:
            data = long(count)

        return data


class SequenceReader(GeneralReader):
    """
    Generalized sequence file reader
    """

    def __init__(self):
        #grab object from jvm
        self.reader = self.gateway.jvm.SequenceReader

    def read(self, path=None, auto_convert=True):
        """
        method to read entire contents of a sequence file

        Parameters
        ----------
        path : str

        Returns
        -------
        list of strings
        """

        data = self.reader.read(path)
        if auto_convert:
            data = [list(d) for d in data]

        return data

    def head(self, nrows=5, path=None, auto_convert=True):
        """
        method to read first n-rows of a sequence file

        Parameters
        ----------
        nrows : int
        path : str

        Returns
        -------
        list of strings
        """

        data = self.reader.head(nrows, path)
        if auto_convert:
            data = [list(d) for d in data]

        return data

    def slice(self, start, stop, path=None, auto_convert=True):
        """
        method to slice (start, stop) contents of a sequence file

        Parameters
        ----------
        nrows : int
        path : str

        Returns
        -------
        list of strings
        """

        data = self.reader.slice(start, stop, path)
        if auto_convert:
            data = [list(d) for d in data]

        return data

    def count(self, path=None, auto_convert=True):
        """
        method to count number of rows in a sequence file

        Parameters
        ----------
        path : str

        Returns
        -------
        long

        """

        count = self.reader.count(path)
        if auto_convert:
            data = long(count)

        return data

    def read_all(self, paths, start=0, auto_convert=True, limit=None):
        '''
        Reads a stream of documents from all the given sequence files
        :param segment_paths: list of segment paths
        :param start the starting position
        :return: stream of records
        '''
        count = 0
        for path in paths:
            for rec in self.read_iterator(path, start, auto_convert=auto_convert):
                count += 1
                if limit and count > limit:
                    return
                yield rec

    def _rec_to_doc(self, rec):
        '''
        Converts the sequence file record into (k, doc) pair
        :param rec: record of key:value pair read from a sequence file
        :return: tuple containing (rec[0], dict(rec(1)))
        '''
        if len(rec) != 2:
            raise Exception("Expected input: [key,value], given=%s" % rec)
        datum = rec[1].toString() # This object is a java object
        #print (datum)
        #print (type(datum))
        parts = datum.split("\n")
        doc = {}
        for part in parts:
            splits = part.strip().split(":", 1)
            if len(splits) >= 1:
                doc[splits[0]] = splits[-1]
        return (rec[0], doc)

    def read_iterator(self, path, start=0, auto_convert=True):
        '''
        Creates a stream of (key:value) pairs by reading given sequence file
        This is a streaming reader, unlike reader.read(...) which loads whole file contents
         into memory at once
        :param path: path of the file
        :param start: the start position, default is 0
        :return: stream of records
        '''
        rec_iterator = self.reader.getRecordIterator(path, start)
        while rec_iterator.hasNext():
            rec = rec_iterator.next()
            yield self._rec_to_doc(list(rec)) if auto_convert else rec

class LinkReader(GeneralReader):
    """
    Link Reader
    """

    def __init__(self):
        #grab object from jvm
        self.reader = self.gateway.jvm.LinkReader
        self.schema = '{key_url: string, url: string, anchor: string, score: float64, ' \
                      'timestamp: int64, linktype: string}'


class NodeReader(GeneralReader):
    """
    Link Reader
    """

    def __init__(self):
        #grab object from jvm
        self.reader = self.gateway.jvm.NodeReader
        self.schema = '{key_url: string, num_inlinks: int64, num_outlinks: int64, ' \
                      'inlink_score: float64, outlink_score: float64, metadata: string}'


sequence_reader = SequenceReader()
link_reader = LinkReader()
node_reader = NodeReader()
